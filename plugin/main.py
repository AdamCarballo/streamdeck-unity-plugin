import os

# Setup logging
import logging
if os.environ.get("SDI_DEBUG", False):
    logging.basicConfig(filename="sdi_debug.log", filemode="w", level=logging.DEBUG)

import sys
import websocket
import json
import unity_socket
from threading import Thread
from event_data import EventData
from actions import InvokeMethodAction, SetFieldPropertyAction, \
        PlayModeAction, PauseModeAction, ExecuteMenuAction, \
        ScriptedAction, DialInvokeAction


# Open the web socket to Stream Deck
def open_streamdeck_socket():
    global sd_socket
    # websocket.enableTrace(True)  # <- Not sure if needed
    # Use 127.0.0.1 because Windows needs 300ms to resolve localhost
    host = "ws://127.0.0.1:%s" % SD_PORT
    sd_socket = websocket.WebSocketApp(host, on_message=on_message, on_error=on_error, on_close=on_close)
    sd_socket.on_open = on_open
    sd_socket.run_forever()


def on_message(ws, message):
    logging.debug(message)
    data = EventData(message)

    # Switch function blocks
    def device_did_connect():
        # Add device if is not in the devices array
        if data.device in devices:
            return

        devices[data.device] = data.device_info

    def will_appear():
        # Add current instance if is not in actions	array
        if data.context in actions:
            return

        # Map events to function blocks
        mapped_action_classes = {
            get_action_name("invoke-method"): InvokeMethodAction,
            get_action_name("set-field-property"): SetFieldPropertyAction,
            get_action_name("play-mode"): PlayModeAction,
            get_action_name("pause-mode"): PauseModeAction,
            get_action_name("execute-menu"): ExecuteMenuAction,
            get_action_name("dial-invoke"): DialInvokeAction,
            get_action_name("scripted"): ScriptedAction
        }

        # If crashes, probably mapped_action_classes is missing a new class
        actions[data.context] = mapped_action_classes[data.action](
            data.context,
            data.settings,
            data.coordinates,
            data.state
        )

        set_dial_feedback(data.context)

    def will_disappear():
        # Remove current instance from array
        if data.context in actions:
            actions.pop(data.context)

    def did_receive_settings():
        # Set settings
        if data.context in actions:
            actions[data.context].set_settings(data.settings)

    def key_down():
        # Send onKeyDown event to actions
        if data.context in actions:
            action = actions[data.context]
            action.on_key_down(data.state)

            sent = u_socket.send(action.get_action_name(), data.event, action.context, action.settings, action.state)
            if not sent:
                show_alert(data.context)

    def key_up():
        # Send onKeyUp event to actions
        if data.context in actions:
            action = actions[data.context]
            action.on_key_up(data.state)

            # Support for unavoidable state change manually triggered by Elgato
            if action.state_changed:
                # setTimeout(function(){ Utils.setState(self.context, self.state); }, 4000);
                set_state(action.context, action.state)

            # 1.3+ Also send events on keyUp, ignored by default unless Unity target is listening for them
            sent = u_socket.send(action.get_action_name(), data.event, action.context, action.settings, action.state)
            if not sent:
                show_alert(data.context)

    # Send onDialRotate event to actions
    def dial_rotate():
        if data.context not in actions:
            return

        if sd_socket is None:
            return

        action = actions[data.context]
        action.on_dial_rotate(data.ticks)

        new_settings = {
            "event": "setSettings",
            "context": action.context,
            "payload": action.settings
        }
        sd_socket.send(json.dumps(new_settings))

        set_dial_feedback(action.context)

        if data.pressed or action.settings.get("dial", False):
            sent = u_socket.send(action.get_action_name(), data.event, action.context, action.settings, action.state)
            if not sent:
                show_alert(data.context)

    # Undefined default event
    def event_default():
        pass

    # Map events to function blocks
    {
        "deviceDidConnect": device_did_connect,
        "willAppear": will_appear,
        "willDisappear": will_disappear,
        "didReceiveSettings": did_receive_settings,
        "keyDown": key_down,
        "dialDown": key_down,
        "touchTap": key_down,
        "keyUp": key_up,
        "dialUp": key_up,
        "dialRotate": dial_rotate
    }.get(data.event, event_default)()


def on_error(ws, error):
    logging.error(error)


def on_close(ws):
    logging.info("### Closed StreamDeck Socket ###")


def on_open(ws):
    # Register plugin to Stream Deck
    def register_plugin():
        json_data = {
            "event": SD_REGISTER_EVENT,
            "uuid": SD_PLUGIN_UUID
        }
        ws.send(json.dumps(json_data))

    Thread(target=register_plugin).start()


# Create the web socket for Unity
def create_unity_socket():
    global u_socket
    u_socket = unity_socket.UnityWebSocket(UNITY_PORT)
    u_socket.on_play_mode_state_changed = lambda data: set_state_all_actions(PlayModeAction, data.payload["state"])
    u_socket.on_pause_mode_state_changed = lambda data: set_state_all_actions(PauseModeAction, data.payload["state"])
    u_socket.on_set_title = lambda data: set_title_by_settings(data.payload["group-id"], data.payload["id"], data.payload["title"])
    u_socket.on_set_image = lambda data: set_image_by_settings(data.payload["group-id"], data.payload["id"], data.payload["image"])
    u_socket.on_set_value = lambda data: set_value_by_settings(data.payload["group-id"], data.payload["id"], data.payload["value"])
    u_socket.on_set_state = lambda data: set_state(data.context, data.payload["state"])
    u_socket.on_get_devices = lambda data: get_devices()
    u_socket.start()


def get_action_name(action_name):
    return "%s.%s" % (BASE_PLUGIN_NAME, action_name)


def set_state_all_actions(class_type, state):
    context_list = get_actions_context_by_class(class_type)

    for context in context_list:
        set_state(context, state)


def set_title_by_settings(group_id, member_id, title):
    if sd_socket is None:
        return

    context = get_action_context_by_settings(group_id, member_id)
    if context is None:
        return

    data = {
        "event": "setTitle",
        "context": context,
        "payload": {
            "title": title
        }
    }

    logging.info("Changing title from context %s to %s" % (context, title))
    sd_socket.send(json.dumps(data))


def set_image_by_settings(group_id, member_id, image):
    if sd_socket is None:
        return

    context = get_action_context_by_settings(group_id, member_id)
    if context is None:
        return

    data = {
        "event": "setImage",
        "context": context,
        "payload": {
            "image": image
        }
    }

    logging.info("Changing image from context %s to %s" % (context, image))
    sd_socket.send(json.dumps(data))


def set_value_by_settings(group_id, member_id, value):
    if sd_socket is None:
        return

    context = get_action_context_by_settings(group_id, member_id)
    if context is None:
        return

    action = actions[context]

    try:
        action.settings["value"] = value
    except Exception:
        pass

    new_settings = {
        "event": "setSettings",
        "context": action.context,
        "payload": action.settings
    }

    logging.info("Changing value from context %s to %s" % (context, value))
    sd_socket.send(json.dumps(new_settings))

    set_dial_feedback(action.context)


def get_action_context_by_settings(group_id, member_id):
    for key, value in actions.items():
        action_id = value.settings.get("id")
        if (action_id == member_id) or (action_id == None and not member_id):
            action_group = value.settings.get("group-id")
            if (action_group == group_id) or (action_group == None and not group_id):
                return key


def get_actions_context_by_class(class_type):
    results = []

    for key, value in actions.items():
        if isinstance(value, class_type):
            results.append(key)

    return results


# Set the state of a key
def set_state(context, state):
    if sd_socket is None:
        return

    if context not in actions:
        return

    data = {
        "event": "setState",
        "context": context,
        "payload": {
            "state": state
        }
    }

    sd_socket.send(json.dumps(data))
    actions[context].set_state(state)

# Get list of connected devices
def get_devices():
    logging.info(f'Devices: {devices}')
    u_socket.send('connected-devices', None, None, devices)

def set_dial_feedback(context):
    action = actions[context]

    try:
        feedback = {
            "event": "setFeedback",
            "context": action.context,
            "payload": {
                "value": action.settings["value"]
            }
        }
        sd_socket.send(json.dumps(feedback))
    except Exception:
        pass

# Show alert icon on the key
def show_alert(context):
    if sd_socket is None:
        return

    data = {
        "event": "showAlert",
        "context": context
    }

    sd_socket.send(json.dumps(data))

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


if __name__ == "__main__":
    logging.info("### Start ###")

    BASE_PLUGIN_NAME = "com.adamcarballo.unity-integration"
    devices = {}
    actions = {}
    sd_socket = None
    u_socket = None
    UNITY_PORT = 2245

    # Setup the web socket and handle communication
    # -port [The port that should be used to create the WebSocket]
    SD_PORT = sys.argv[2]
    # -pluginUUID [A unique identifier string that should be used to register the plugin once the web socket is opened]
    SD_PLUGIN_UUID = sys.argv[4]
    # -registerEvent [The event type that should be used to register the plugin once the web socket is opened]
    SD_REGISTER_EVENT = sys.argv[6]
    # -info [A stringified json containing the Stream Deck application information and devices information.]
    SD_INFO = sys.argv[8]

    # Create Unity web socket
    Thread(target=create_unity_socket, daemon=True).start()

    # Open the web socket to Stream Deck
    # Thread(target=open_streamdeck_socket, daemon=True).start()
    open_streamdeck_socket()

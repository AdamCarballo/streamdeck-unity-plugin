# Setup logging
import logging
logging.basicConfig(filename="main.log", filemode="w", level=logging.DEBUG)

import sys
import websocket
import json
import unity_socket
from threading import Thread
from event_data import EventData
from actions import InvokeMethodAction, SetFieldPropertyAction, PlayModeAction, PauseModeAction, ExecuteMenu


# Open the web socket to Stream Deck
def open_streamdeck_socket():
    global sd_socket
    websocket.enableTrace(True)  # <- Not sure if needed
    # Use 127.0.0.1 because Windows needs 300ms to resolve localhost
    host = "ws://127.0.0.1:%s" % SD_PORT
    sd_socket = websocket.WebSocketApp(host, on_message=on_message, on_error=on_error, on_close=on_close)
    sd_socket.on_open = on_open
    sd_socket.run_forever()


def on_message(ws, message):
    logging.debug(message)
    data = EventData(message)

    # Switch function blocks
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
            get_action_name("execute-menu"): ExecuteMenu
        }

        # If crashes, probably mapped_action_classes is missing a new class
        actions[data.context] = mapped_action_classes[data.action](
            data.context,
            data.settings,
            data.coordinates,
            data.state
        )

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

            sent = u_socket.send(action.get_action_name(), action.context, action.settings, action.state)
            if not sent:
                show_alert(data.context)

    def key_up():
        # Send onKeyUp event to actions
        if data.context in actions:
            action = actions[data.context]
            action.on_key_up(data.state)

            # Support for stupid unavoidable state change manually triggered by Elgato
            if action.state_changed:
                # setTimeout(function(){ Utils.setState(self.context, self.state); }, 4000);
                set_state(action.context, action.state)

    def event_default():
        pass

    # Map events to function blocks
    {
        "willAppear": will_appear,
        "willDisappear": will_disappear,
        "didReceiveSettings": did_receive_settings,
        "keyDown": key_down,
        "keyUp": key_up
    }.get(data.event, event_default)()


def on_error(ws, error):
    logging.error(error)


def on_close(ws):
    logging.info("### closed ###")


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
	u_socket.on_set_state = lambda data: set_state(data.context, data.payload["state"])
	u_socket.start()


def get_action_name(action_name):
    return "%s.%s" % (BASE_PLUGIN_NAME, action_name)


def set_state_all_actions(class_type, state):
    context_list = get_actions_context_by_class(class_type)

    for context in context_list:
        set_state(context, state)


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


# Show alert icon on the key
def show_alert(context):
    if sd_socket is None:
        return

    data = {
        "event": "showAlert",
        "context": context
    }

    sd_socket.send(json.dumps(data))


if __name__ == "__main__":
    logging.info("### Start ###")

    BASE_PLUGIN_NAME = "com.adamcarballo.unity-integration"
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

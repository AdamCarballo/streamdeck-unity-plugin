import json
import logging
from websocket_server import WebsocketServer
from unity_response_data import UnityResponseData


class UnityWebSocket:
	def __init__(self, port):
		logging.info("Creating Unity socket")
		self.server = WebsocketServer(port)
		self.server.set_fn_new_client(self.new_client)
		self.server.set_fn_message_received(self.on_message)

		self.on_play_mode_state_changed = self.event_default
		self.on_pause_mode_state_changed = self.event_default
		self.on_set_title = self.event_default
		self.on_set_image = self.event_default
		self.on_set_value = self.event_default
		self.on_set_state = self.event_default
		self.on_get_devices = self.event_default

	def start(self):
		self.server.run_forever()

	def new_client(self, client, ws):
		self.send("open-socket")

	def on_message(self, client, ws, message):
		logging.debug(message)
		data = UnityResponseData(message)

		{
			"setState": self.on_set_state,
			"playModeStateChanged": self.on_play_mode_state_changed,
			"pauseModeStateChanged": self.on_pause_mode_state_changed,
			"setTitle": self.on_set_title,
			"setImage": self.on_set_image,
			"setValue": self.on_set_value,
			"getDevices": self.on_get_devices
		}.get(data.event, self.event_default)(data)

	def send(self, action, event=None, context=None, settings=None, state=0):
		if len(self.server.clients) == 0:
			return False

		data = {
			"action": action,
			"event": event,
			"context": context,
			"settings": settings,
			"state": state
		}

		self.server.send_message_to_all(json.dumps(data))
		return True

	def event_default(self, data):
		pass

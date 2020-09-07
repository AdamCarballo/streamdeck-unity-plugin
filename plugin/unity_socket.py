import json
from websocket_server import WebsocketServer
from unity_response_data import UnityResponseData


class UnityWebSocket:
	def __init__(self, port):
		print("Creating Unity socket")
		self.server = WebsocketServer(port)
		self.server.set_fn_new_client(self.new_client)
		self.server.set_fn_message_received(self.on_message)

		self.on_play_mode_state_changed = self.event_default
		self.on_pause_mode_state_changed = self.event_default
		self.on_set_state = self.event_default

	def start(self):
		self.server.run_forever()

	def new_client(self, client, ws):
		self.send("open-socket")

	def on_message(self, client, ws, message):
		print(message)
		data = UnityResponseData(message)

		{
			"setState": self.on_set_state,
			"playModeStateChanged": self.on_play_mode_state_changed,
			"pauseModeStateChanged": self.on_pause_mode_state_changed
		}.get(data.event, self.event_default)(data)

	def send(self, action, context=None, settings=None, state=0):
		if len(self.server.clients) == 0:
			return False

		data = {
			"action": action,
			"context": context,
			"settings": settings,
			"state": state
		}

		self.server.send_message_to_all(json.dumps(data))
		return True

	def event_default(self, data):
		pass


# Web socket used for communication with Unity
def create_socket():
	print("creating Unity socket")
	global server
	server = WebsocketServer(PORT)
	server.set_fn_new_client(new_client)
	server.set_fn_message_received(on_message)
	server.run_forever()


def dispose_socket():
	print("disposed Unity socket")
	global server
	server.server_close()
	server = None


def new_client(client, server_param):
	send_event("open-socket", client)


def on_message(client, server_param, message):
	print(message)
	data = UnityResponseData(message)

	def set_state():
		#main.set_state(data.context, data.payload["state"])
		print("set_state called form Unity!")

	def play_mode_state_changed():
		#main.set_state_all_actions(PlayModeAction, data.payload["state"])
		print("play_mode_state_changed called from Unity!")

	def event_default():
		pass

	# Map events to function blocks
	{
		"setState": set_state,
		"playModeStateChanged": play_mode_state_changed
	}.get(data.event, event_default)()


def send_event(action, client=None, context=None, settings=None, state=0):
	data = {
		"action": action,
		"context": context,
		"settings": settings,
		"state": state
	}

	__send_message_to_unity(client, json.dumps(data), context)


def __send_message_to_unity(client, message, context):
	global server
	if server is None:
		return

	if len(server.clients) == 0:
		if context and context.strip():
			#main.show_alert(context)
			pass
		return

	if client is None:
		server.send_message_to_all(message)
	else:
		server.send_message(client, message)


PORT = 2245
server = None

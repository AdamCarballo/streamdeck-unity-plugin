import json


class EventData:
	def __init__(self, json_data):
		data = json.loads(json_data)

		self.action = data.get("action")
		self.event = data.get("event")
		self.context = data.get("context")
		self.device = data.get("device")

		data_payload = data.get("payload")

		self.settings = data_payload.get("settings")
		self.coordinates = data_payload.get("coordinates")
		self.state = data_payload.get("state", 0)

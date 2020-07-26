import json


class UnityResponseData:
	def __init__(self, json_data):
		data = json.loads(json_data)

		self.event = data.get("event")
		self.context = data.get("context")
		self.payload = data.get("payload")

import json


class EventData:
    def __init__(self, json_data):
        data = json.loads(json_data)

        self.action = data.get("action")
        self.event = data.get("event")
        self.context = data.get("context")
        self.device = data.get("device")
        self.device_info = data.get("deviceInfo")

        data_payload = data.get("payload")

        if data_payload is not None:
            self.settings = data_payload.get("settings")
            self.coordinates = data_payload.get("coordinates")
            self.state = data_payload.get("state", 0)
            self.ticks = data_payload.get("ticks", 0)
            self.pressed = data_payload.get("pressed", False)

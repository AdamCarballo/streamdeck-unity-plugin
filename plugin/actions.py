class Action:
	def __init__(self, context, settings, coordinates, state=0):
		self.action_name = self.get_action_name()
		self.context = context
		self.coordinates = coordinates
		self.state = state
		self.settings = settings
		self.state_changed = False

	def get_action_name(self):
		return "action"

	def set_settings(self, settings):
		self.settings = settings

	def set_state(self, state):
		self.state = state

	def on_key_down(self, state):
		self.state = state

	def on_key_up(self, state):
		self.state = state

	def on_dial_rotate(self, ticks):
		self.state = ticks


class InvokeMethodAction(Action):
	def get_action_name(self):
		return "invoke-method"


class SetFieldPropertyAction(Action):
	def get_action_name(self):
		return "set-field-property"


class PlayModeAction(Action):
	def get_action_name(self):
		return "play-mode"

	def on_key_down(self, state):
		super().on_key_down(state)
		self.state_changed = False

	def set_state(self, state):
		super().set_state(state)
		self.state_changed = True


class PauseModeAction(Action):
	def get_action_name(self):
		return "pause-mode"

	def on_key_down(self, state):
		super().on_key_down(state)
		self.state_changed = False

	def set_state(self, state):
		super().set_state(state)
		self.state_changed = True


class ExecuteMenuAction(Action):
	def get_action_name(self):
		return "execute-menu"


class ScriptedAction(Action):
	def get_action_name(self):
		return "scripted"
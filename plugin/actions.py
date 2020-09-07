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


# endregion

# region Invoke Method
class InvokeMethodAction(Action):
	def get_action_name(self):
		return "invoke-method"


# endregion

# region Set Field Property
class SetFieldPropertyAction(Action):
	def get_action_name(self):
		return "set-field-property"


# endregion

# region Play Mode
class PlayModeAction(Action):
	def get_action_name(self):
		return "play-mode"

	def on_key_down(self, state):
		super().on_key_down(state)
		self.state_changed = False

	def set_state(self, state):
		super().set_state(state)
		self.state_changed = True


# endregion

# region Pause Mode
class PauseModeAction(Action):
	def get_action_name(self):
		return "pause-mode"

	def on_key_down(self, state):
		super().on_key_down(state)
		self.state_changed = False

	def set_state(self, state):
		super().set_state(state)
		self.state_changed = True


# endregion

# region Set Field Property
class ExecuteMenu(Action):
	def get_action_name(self):
		return "execute-menu"


# endregion

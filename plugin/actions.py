import logging
from decimal import *

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

	def on_dial_rotate(self, ticks):
		try:
			match self.settings["type"]:
				case "int":
					self.settings["value"] = str(int(self.settings["value"]) + ticks)
				case "float":
					self.settings["value"] = str(Decimal(self.settings["value"]) + ticks * Decimal("0.1"))
				case "bool":
					# Flipping booleans only happens if the tick is odd
					if (ticks % 2) == 0:
						pass
					self.settings["value"] = str(not str2bool(self.settings["value"]))
				case _:
					logging.warning("Dials can only operate on numeric values")
		except Exception as e:
			pass


class SetFieldPropertyAction(Action):
	def get_action_name(self):
		return "set-field-property"

	def on_dial_rotate(self, ticks):
		try:
			match self.settings["type"]:
				case "int":
					self.settings["value"] = str(int(self.settings["value"]) + ticks)
				case "float":
					self.settings["value"] = str(Decimal(self.settings["value"]) + ticks * Decimal("0.1"))
				case "bool":
					# Flipping booleans only happens if the tick is odd
					if (ticks % 2) == 0:
						pass
					self.settings["value"] = str(not str2bool(self.settings["value"]))
				case _:
					logging.warning("Dials can only operate on numeric values")
		except Exception:
			pass


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


class DialInvokeAction(Action):
	def get_action_name(self):
		return "dial-invoke"

	def on_key_down(self, state):
		if self.state > 1:
			self.state = self.state - 2

		if self.state == 0:
			self.state = 1
		else:
			self.state = 0

	def on_key_up(self, state):
		pass

	def on_dial_rotate(self, ticks):
		if self.state <= 1:
			self.state = self.state + 2

		if not self.settings.get("value", None):
			return

		self.settings["value"] = str(Decimal(self.settings["value"]) + ticks * Decimal(self.settings["steps"]))


class ScriptedAction(Action):
	def get_action_name(self):
		return "scripted"
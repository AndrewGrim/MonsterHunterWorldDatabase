import typing
from typing import Tuple

def hexToRGB(color: str) -> Tuple[int, int, int]:
	"""
	color = The hexadecimal representation of the color, # hash optional.

	returns:

		A tuple containing the red, green and blue color information.
	"""

	assert len(color) is 6 or len(color) is 7, "The color string should have the following format: #FF00FF - # is optional"

	color = color.replace("#", "")
	red = int(color[0:2], 16)
	green = int(color[2:4], 16)
	blue = int(color[4:6], 16)

	return (red, green, blue)

damageColors = {
	"fire": {
		0: "#FFEBEE",
		2: "#FFEBEE",
		5: "#FFEBEE",
		7: "#FFCDD2",
		10: "#FFCDD2",
		15: "#EF9A9A",
		20: "#E57373",
		25: "#EF5350",
		30: "#F44336",
		35: "#E53935",
		40: "#E53935",
		50: "#E53935",
	},
	"water": {
		0: "#E0F7FA",
		2: "#E0F7FA",
		3: "#E0F7FA",
		5: "#B2EBF2",
		7: "#B2EBF2",
		10: "#80DEEA",
		15: "#4DD0E1",
		20: "#26C6DA",
		25: "#00BCD4",
		30: "#00BCD4",
		35: "#00BCD4",
		40: "#00BCD4",
		45: "#00BCD4",
		50: "#00BCD4",
		80: "#00BCD4",
	},
	"ice": {
		0: "#E3F2FD",
		5: "#E3F2FD",
		10: "#BBDEFB",
		15: "#90CAF9",
		20: "#64B5F6",
		25: "#42A5F5",
		30: "#2196F3",
		35: "#2196F3",
		40: "#2196F3",
		50: "#2196F3",
	},
	"thunder": {
		0: "#FFF8E1",
		3: "#FFF8E1",
		5: "#FFF8E1",
		7: "#FFECB3",
		10: "#FFECB3",
		15: "#FFE082",
		20: "#FFD54F",
		25: "#FFCA28",
		30: "#FFB300",
		35: "#FFB300",
		40: "#FFB300",
		50: "#FFB300",
	},
	"dragon": {
		0: "#EDE7F6",
		5: "#EDE7F6",
		10: "#D1C4E9",
		15: "#B39DDB",
		20: "#9575CD",
		25: "#7E57C2",
		30: "#7E57C2",
		35: "#7E57C2",
		40: "#7E57C2",
		50: "#7E57C2",
		85: "#7E57C2",
	},
}

extractColors = {
	"red": "#F44336",
	"white": "#FFFFFF",
	"orange": "#FF9800",
	"green": "#4CAF50",
}

class Link:

	def __init__(self):
		self.reset()


	def reset(self):
		self.event = False
		self.eventType = ""
		self.item = 0
		self.weapon = 0
		self.armor = 0
		self.decoration = 0
		self.skill = 0
		self.location = 0
		self.charm = 0
		self.kinsect = 0


	def __repr__(self):
		return f"{self.__dict__!r}"
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
		60: "#E53935",
		70: "#E53935",
		80: "#E53935",
		90: "#E53935",
		100: "#E53935",
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
		60: "#00BCD4",
		70: "#00BCD4",
		80: "#00BCD4",
		90: "#00BCD4",
		100: "#00BCD4",
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
		60: "#2196F3",
		70: "#2196F3",
		80: "#2196F3",
		90: "#2196F3",
		100: "#2196F3",
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
		60: "#FFB300",
		70: "#FFB300",
		80: "#FFB300",
		90: "#FFB300",
		100: "#FFB300",
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
		60: "#7E57C2",
		70: "#7E57C2",
		80: "#7E57C2",
		90: "#7E57C2",
		100: "#7E57C2",
	},
}

extractColors = {
	"red": "#F44336",
	"white": "#FFFFFF",
	"orange": "#FF9800",
	"green": "#4CAF50",
}

# TODO these will need to be check when i have access to iceborne
setBonusColors = {
	"Anjanath Power": "SetBonusPink.png",
	"Anjanath Will": "SetBonusPink.png",
	"Anjanath Dominance": "SetBonusPink.png",
	"Astera Blessing": "SetBonusWhite.png",
	"Bazelgeuse Protection": "SetBonusWhite.png",
	"Bazelgeuse Ambition": "SetBonusWhite.png",
	"Commission Guidance": "SetBonusGreen.png",
	"Diablos Mastery": "SetBonusBeige.png",
	"Diablos Power": "SetBonusBeige.png",
	"Diablos Ambition": "SetBonusBeige.png",
	"Guild Guidance": "SetBonusGold.png",
	"Kirin Blessing": "SetBonusWhite.png",
	"Kirin Favor": "SetBonusWhite.png",
	"Kirin Favor": "SetBonusWhite.png",
	"Kushala Daora Flight": "SetBonusGray.png",
	"Legiana Blessing": "SetBonusBlue.png",
	"Legiana Favor": "SetBonusBlue.png",
	"Legiana Ambition": "SetBonusBlue.png",
	"Lunastra Favor": "SetBonusBlue.png",
	"Nergigante Hunger": "SetBonusGray.png",
	"Odogaron Mastery": "SetBonusDarkRed.png",
	"Odogaron Power": "SetBonusDarkRed.png",
	"Pink Rathian Mastery": "SetBonusPink.png",
	"Rathalos Mastery": "SetBonusRed.png",
	"Rathalos Power": "SetBonusRed.png",
	"Rathalos Essence": "SetBonusRed.png",
	"Rathian Essence": "SetBonusGreen.png",
	"Soul of the Dragoon": "SetBonusViolet.png",
	"Teostra Technique": "SetBonusRed.png",
	"Uragaan Protection": "SetBonusGold.png",
	"Uragaan Ambition": "SetBonusGold.png",
	"Vaal Hazak Vitality": "SetBonusWhite.png",
	"Vaal Soulvein": "SetBonusWhite.png",
	"Xeno'jiiva Divinity": "SetBonusWhite.png",
	"Zorah Magdaros Mastery": "SetBonusGray.png",
	"Zorah Magdaros Essence": "SetBonusGray.png",
	"Ancient Divinity": "SetBonusBeige.png",
	"Commission Alchemy": "SetBonusBeige.png",
	"Barioth Hidden Art": "SetBonusWhite.png",
	"Nargacuga Essence": "SetBonusGray.png",
	"Glavenus Essence": "SetBonusRed.png",
	"Brachydios Essence": "SetBonusBlue.png",
	"Tigrex Essence": "SetBonusBeige.png",
	"Instructor's Guidance": "SetBonusLightBeige.png",
	"Deviljho Essence": "SetBonusRed.png",
	"Velkhana Divinity": "SetBonusWhite.png",
	"Namielle Divinity": "SetBonusBlue.png",
	"Shara Ishvalda Divinity": "SetBonusBeige.png",
	"Zinogre Essence": "SetBonusCyan.png",
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
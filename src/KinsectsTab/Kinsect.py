class Kinsect:

	def __init__(self, dbRow):
		self.id = dbRow[0]
		self.rarity = dbRow[1]
		self.previousID = dbRow[2]
		self.attackType = dbRow[3]
		self.dustEffect = dbRow[4]
		self.power = dbRow[5]
		self.speed = dbRow[6]
		self.heal = dbRow[7]
		self.final = dbRow[8]
		self.name = dbRow[9]


	def __repr__(self):
		return f"{self.__dict__!r}"


class KinsectMaterial:

	def __init__(self, dbRow):
		self.kinsectID = dbRow[0]
		self.materialID = dbRow[1]
		self.quantity = dbRow[2]
		self.kinsectName = dbRow[3]
		self.category = dbRow[4]
		self.iconName = dbRow[5]
		self.iconColor = dbRow[6]
		self.name = dbRow[7]


	def __repr__(self):
		return f"{self.__dict__!r}"
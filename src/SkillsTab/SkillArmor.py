class SkillArmor:

	def __init__(self, dbRow):
		self.id = dbRow[0]
		self.skillMaxLevel = dbRow[1]
		self.armorID = dbRow[2]
		self.armorName = dbRow[3]
		self.armorRarity = dbRow[4]
		self.armorType = dbRow[5]
		self.skillLevel = dbRow[6]


	def __repr__(self):
		return f"{self.__dict__!r}"
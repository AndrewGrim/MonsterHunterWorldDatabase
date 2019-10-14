class SkillArmorSetBonus:

	def __init__(self, dbRow):
		self.id = dbRow[0]
		self.name = dbRow[1]
		self.skillMaxLevel = dbRow[2]
		self.setBonusID = dbRow[3]
		self.setBonusName = dbRow[4]
		self.setBonusRequired = dbRow[5]


	def __repr__(self):
		return f"{self.__dict__!r}"
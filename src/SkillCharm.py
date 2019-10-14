class SkillCharm:

	def __init__(self, dbRow):
		self.id = dbRow[0]
		self.rarity = dbRow[1]
		self.name = dbRow[2]
		self.skillID = dbRow[3]
		self.skillName = dbRow[4]
		self.skillMaxLevel = dbRow[5]
		self.skillLevel = dbRow[6]


	def __repr__(self):
		return f"{self.__dict__!r}"
class SkillDetail:

	def __init__(self, dbRow):
		self.id = dbRow[0]
		self.name = dbRow[1]
		self.description = dbRow[2]
		self.skillMaxLevel = dbRow[3]
		self.skillLevel = dbRow[4]
		self.skillLevelDescription = dbRow[5]
		self.iconColor = dbRow[6]


	def __repr__(self):
		return f"{self.__dict__!r}"
class CharmSkill:

	def __init__(self, dbRow):
		self.id = dbRow[0]
		self.name = dbRow[1]
		self.maxLevel = dbRow[2]
		self.iconColor = dbRow[3]
		self.level = dbRow[4]


	def __repr__(self):
		return f"{self.__dict__!r}"
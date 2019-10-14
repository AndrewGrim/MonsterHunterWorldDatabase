class Skill:

	def __init__(self, dbRow):
		self.id = dbRow[0]
		self.name = dbRow[1]
		self.skillMaxLevel = dbRow[2]
		self.description = dbRow[3]
		self.iconColor = dbRow[4]


	def __repr__(self):
		return f"{self.__dict__!r}"
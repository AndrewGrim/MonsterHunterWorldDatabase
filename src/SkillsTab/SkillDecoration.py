class SkillDecoration:

	def __init__(self, dbRow):
		self.id = dbRow[0]
		self.name = dbRow[1]
		self.skillMaxLevel = dbRow[2]
		self.decorationID = dbRow[3]
		self.decorationName = dbRow[4]
		self.decorationSlot = dbRow[5]
		self.decorationIconColor = dbRow[6]
		self.skillLevel = dbRow[7]


	def __repr__(self):
		return f"{self.__dict__!r}"
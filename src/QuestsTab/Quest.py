class Quest:

	def __init__(self, dbRow):
		self.id = dbRow[0]
		self.name = dbRow[1]
		self.description = dbRow[2]
		self.objective = dbRow[3]
		self.questType = dbRow[4]
		self.category = dbRow[5]
		self.location = dbRow[6]
		self.stars = dbRow[7]
		self.zenny = dbRow[8]


	def __repr__(self):
		return f"{self.__dict__!r}"
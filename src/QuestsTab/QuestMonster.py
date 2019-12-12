class QuestMonster:

	def __init__(self, dbRow):
		self.id = dbRow[0]
		self.name = dbRow[1]
		self.quantity = dbRow[2]
		self.isObjective = dbRow[3]


	def __repr__(self):
		return f"{self.__dict__!r}"
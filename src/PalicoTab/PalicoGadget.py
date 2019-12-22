class PalicoGadget:

	def __init__(self, dbRow):
		self.id = dbRow[0]
		self.location = dbRow[1]
		self.unlockCondition = dbRow[2]
		self.name = dbRow[3]
		self.description = dbRow[4]


	def __repr__(self):
		return f"{self.__dict__!r}"
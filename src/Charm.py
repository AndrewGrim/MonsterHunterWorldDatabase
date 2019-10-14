class Charm:

	def __init__(self, dbRow):
		self.id = dbRow[0]
		self.orderId = dbRow[1]
		self.previousID = dbRow[2]
		self.rarity = dbRow[3]
		self.name = dbRow[4]


	def __repr__(self):
		return f"{self.__dict__!r}"
class Monster:

	def __init__(self, dbRow):
		self.id = dbRow[0]
		self.size = dbRow[1]
		self.name = dbRow[2]


	def __repr__(self):
		return f"{self.__dict__!r}"
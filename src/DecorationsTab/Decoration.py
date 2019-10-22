class Decoration:

	def __init__(self, dbRow):
		self.id = dbRow[0]
		self.name = dbRow[1]
		self.slot = dbRow[2]
		self.iconColor = dbRow[3]


	def __repr__(self):
		return f"{self.__dict__!r}"
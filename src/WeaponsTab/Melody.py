class Melody:

	def __init__(self, dbRow):
		self.id = dbRow[0]
		self.notes = dbRow[1]
		self.effect1 = dbRow[2]
		self.effect2 = dbRow[3]
		self.duration = dbRow[4]
		self.extension = dbRow[5]


	def __repr__(self):
		return f"{self.__dict__!r}"
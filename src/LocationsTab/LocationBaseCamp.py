class LocationBaseCamp:

	def __init__(self, dbRow):
		self.name = dbRow[0]
		self.area = dbRow[1]


	def __repr__(self):
		return f"{self.__dict__!r}"
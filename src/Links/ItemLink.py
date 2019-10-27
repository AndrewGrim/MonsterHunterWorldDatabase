class ItemLink:

	def __init__(self, dbRow):
		self.id = dbRow[0]
		self.category = dbRow[1]


	def __repr__(self):
		return f"{self.__dict__!r}"
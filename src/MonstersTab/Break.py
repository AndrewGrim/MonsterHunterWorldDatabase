class Break:

	def __init__(self, dbRow):
		self.flinch = dbRow[0]
		self.wound = dbRow[1]
		self.sever = dbRow[2]
		self.extract = dbRow[3]
		self.name = dbRow[4]


	def __repr__(self):
		return f"{self.__dict__!r}"
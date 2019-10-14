class LocationMaterial:

	def __init__(self, dbRow):
		self.id = dbRow[0]
		self.name = dbRow[1]
		self.iconName = dbRow[2]
		self.iconColor = dbRow[3]
		self.category = dbRow[4]
		self.rank = dbRow[5]
		self.area = dbRow[6]
		self.stack = dbRow[7]
		self.percentage = dbRow[8]
		self.nodes = dbRow[9]


	def __repr__(self):
		return f"{self.__dict__!r}"
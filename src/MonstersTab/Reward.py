class Reward:

	def __init__(self, dbRow):
		self.conditionName = dbRow[0]
		self.stack = dbRow[1]
		self.percentage = dbRow[2]
		self.itemID = dbRow[3]
		self.itemName = dbRow[4]
		self.iconName = dbRow[5]
		self.category = dbRow[6]
		self.iconColor = dbRow[7]


	def __repr__(self):
		return f"{self.__dict__!r}"
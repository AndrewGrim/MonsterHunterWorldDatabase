class MonsterMaterialLink:

	def __init__(self, dbRow):
		self.rank = dbRow[0]
		self.rewardCondition = dbRow[1]
		self.stack = dbRow[2]
		self.percentage = dbRow[3]
		self.id = dbRow[4]
		self.name = dbRow[5]
		self.iconName = dbRow[6]
		self.category = dbRow[7]
		self.iconColor = dbRow[8]


	def __repr__(self):
		return f"{self.__dict__!r}"
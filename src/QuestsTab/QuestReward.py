class QuestReward:

	def __init__(self, dbRow):
		self.id = dbRow[0]
		self.name = dbRow[1]
		self.category = dbRow[2]
		self.stack = dbRow[3]
		self.percentage = dbRow[4]
		self.rewardGroup = dbRow[5]
		self.iconName = dbRow[6]
		self.iconColor = dbRow[7]


	def __repr__(self):
		return f"{self.__dict__!r}"
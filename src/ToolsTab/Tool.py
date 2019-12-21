class Tool:

	def __init__(self, dbRow):
		self.id = dbRow[0]
		self.orderID = dbRow[1]
		self.duration = dbRow[2]
		self.rechargeTime = dbRow[3]
		self.associatedQuest = dbRow[4]
		self.name = dbRow[5]
		self.unlockCondition = dbRow[6]
		self.description = dbRow[7]


	def __repr__(self):
		return f"{self.__dict__!r}"


class ToolMaterial:

	def __init__(self, dbRow):
		self.id = dbRow[0]
		self.name = dbRow[1]
		self.category = dbRow[2]
		self.quantity = dbRow[3]
		self.iconName = dbRow[4]
		self.iconColor = dbRow[5]


	def __repr__(self):
		return f"{self.__dict__!r}"
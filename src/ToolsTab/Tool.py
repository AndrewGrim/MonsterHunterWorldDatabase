class Tool:

	def __init__(self, dbRow):
		self.id = dbRow[0]
		self.duration = dbRow[1]
		self.rechargeTime = dbRow[2]
		self.associatedQuest = dbRow[3]
		self.name = dbRow[4]
		self.unlockCondition = dbRow[5]
		self.description = dbRow[6]


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
class Kinsect:

	def __init__(self, dbRow):
		self.id = dbRow[0]
		self.orderID = dbRow[1]
		self.previousID = dbRow[2]
		self.attackType = dbRow[3]
		self.dustEffect = dbRow[4]
		self.power = dbRow[5]
		self.speed = dbRow[6]
		self.heal = dbRow[7]
		self.final = dbRow[8]
		self.name = dbRow[9]


	def __repr__(self):
		return f"{self.__dict__!r}"
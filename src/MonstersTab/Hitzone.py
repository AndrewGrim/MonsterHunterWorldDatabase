class Hitzone:

	def __init__(self, dbRow):
		self.id = dbRow[0]
		self.monsterID = dbRow[1]
		self.cut = dbRow[2]
		self.impact = dbRow[3]
		self.shot = dbRow[4]
		self.fire = dbRow[5]
		self.water = dbRow[6]
		self.ice = dbRow[7]
		self.thunder = dbRow[8]
		self.dragon = dbRow[9]
		self.ko = dbRow[10]
		self.name = dbRow[11]


	def __repr__(self):
		return f"{self.__dict__!r}"
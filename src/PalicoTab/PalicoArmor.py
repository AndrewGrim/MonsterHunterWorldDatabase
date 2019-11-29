class PalicoArmor:

	def __init__(self, dbRow):
		self.id = dbRow[0]
		self.rarity = dbRow[1]
		self.rank = dbRow[2]
		self.name = dbRow[3]
		self.setName = dbRow[4]
		self.defense = dbRow[5]
		self.fire = dbRow[6]
		self.water = dbRow[7]
		self.thunder = dbRow[8]
		self.ice = dbRow[9]
		self.dragon = dbRow[10]
		self.fullArmorSet = dbRow[11]
		self.description = dbRow[12]


	def __repr__(self):
		return f"{self.__dict__!r}"
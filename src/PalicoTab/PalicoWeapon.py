class PalicoWeapon:

	def __init__(self, dbRow):
		self.id = dbRow[0]
		self.rarity = dbRow[1]
		self.rank = dbRow[2]
		self.name = dbRow[3]
		self.setName = dbRow[4]
		self.attackMelee = dbRow[5]
		self.attackRanged = dbRow[6]
		self.attackType = dbRow[7]
		self.element = dbRow[8]
		self.elementAttack = dbRow[9]
		self.affinity = dbRow[10]
		self.defense = dbRow[11]
		self.description = dbRow[12]


	def __repr__(self):
		return f"{self.__dict__!r}"
class WeaponMaterial:

	def __init__(self, dbRow):
		self.id = dbRow[0]
		self.name = dbRow[1]
		self.iconName = dbRow[2]
		self.category = dbRow[3]
		self.iconColor = dbRow[4]
		self.quantity = dbRow[5]
		self.recipeType = dbRow[6]


	def __repr__(self):
		return f"{self.__dict__!r}"
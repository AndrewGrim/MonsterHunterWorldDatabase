class Armor:

	def __init__(self, dbRow):
		self.id = dbRow[0]
		self.orderID = dbRow[1]
		self.rarity = dbRow[2]
		self.rank = dbRow[3]
		self.armorType = dbRow[4]
		self.armorSetID = dbRow[5]
		self.armorSetBonusID = dbRow[6]
		self.male = dbRow[7]
		self.female = dbRow[8]
		self.slot1 = dbRow[9]
		self.slot2 = dbRow[10]
		self.slot3 = dbRow[11]
		self.defense = f"{dbRow[12]} {dbRow[13]} {dbRow[14]}"
		self.defenseBase = dbRow[12]
		self.defenseMax = dbRow[13]
		self.defenseAugmentedMax = dbRow[14]
		self.fire = dbRow[15]
		self.water = dbRow[16]
		self.thunder = dbRow[17]
		self.ice = dbRow[18]
		self.dragon = dbRow[19]
		self.name = dbRow[20]
		self.armorSetName = dbRow[21]


	def __repr__(self):
		return f"{self.__dict__!r}"


class ArmorSkill:

	def __init__(self, dbRow):
		self.id = dbRow[0]
		self.name = dbRow[1]
		self.skillMaxLevel = dbRow[2]
		self.iconColor = dbRow[3]
		self.skillLevel = dbRow[4]


	def __repr__(self):
		return f"{self.__dict__!r}"


class ArmorSetBonus:

	def __init__(self, dbRow):
		self.id = dbRow[0]
		self.name = dbRow[1]
		self.skillMaxLevel = dbRow[2]
		self.iconColor = dbRow[3]
		self.setBonusID = dbRow[4]
		self.setBonusName = dbRow[5]
		self.setBonusAmtRequired = dbRow[6]


	def __repr__(self):
		return f"{self.__dict__!r}"


class ArmorMaterial:

	def __init__(self, dbRow):
		self.id = dbRow[0]
		self.name = dbRow[1]
		self.iconName = dbRow[2]
		self.category = dbRow[3]
		self.iconColor = dbRow[4]
		self.quantity = dbRow[5]
		

	def __repr__(self):
		return f"{self.__dict__!r}"
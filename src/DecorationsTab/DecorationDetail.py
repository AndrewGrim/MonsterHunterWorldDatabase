class DecorationDetail:

	def __init__(self, dbRow):
		self.id = dbRow[0]
		self.rarity = dbRow[1]
		self.skillTreeID = dbRow[2]
		self.slot = dbRow[3]
		self.iconColor = dbRow[4]
		self.mysteriousFeystonePercent = dbRow[5]
		self.glowingFeystonePercent = dbRow[6]
		self.wornFeystonePercent = dbRow[7]
		self.warpedFeystonePercent = dbRow[8]
		self.name = dbRow[9]
		self.skillID = dbRow[10]
		self.skillName = dbRow[11]
		self.skillMaxLevel = dbRow[12]
		self.skillIconColor = dbRow[13]
		self.skillLevel = dbRow[14]


	def __repr__(self):
		return f"{self.__dict__!r}"
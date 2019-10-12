class ArmorUsage:

    def __init__(self, dbRow):
        self.id = dbRow[0]
        self.name = dbRow[1]
        self.armorType = dbRow[2]
        self.rarity = dbRow[3]
        self.quantity = dbRow[4]


    def __repr__(self):
        return f"{self.__dict__!r}"
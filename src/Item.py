class Item:

    def __init__(self, dbRow):
        self.id = dbRow[0]
        self.category = dbRow[1]
        self.subcategory = dbRow[2]
        self.rarity = dbRow[3]
        self.buyPrice = dbRow[4]
        self.sellPrice = dbRow[5]
        self.carryLimit = dbRow[6]
        self.points = dbRow[7]
        self.iconName = dbRow[8]
        self.iconColor = dbRow[9]
        self.name = dbRow[10]
        self.description = dbRow[11]


    def __repr__(self):
        return f"{self.__dict__!r}"
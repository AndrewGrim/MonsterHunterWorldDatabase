class CharmUsage:

    def __init__(self, dbRow):
        self.id = dbRow[0]
        self.rarity = dbRow[1]
        self.name = dbRow[2]
        self.quantity = dbRow[3]


    def __repr__(self):
        return f"{self.__dict__!r}"
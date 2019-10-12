class WeaponUsage:

    def __init__(self, dbRow):
        self.id = dbRow[0]
        self.rarity = dbRow[1]
        self.weaponType = dbRow[2]
        self.name = dbRow[4]
        self.quantity = dbRow[5]


    def __repr__(self):
        return f"{self.__dict__!r}"
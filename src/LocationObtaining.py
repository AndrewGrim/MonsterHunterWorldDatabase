class LocationObtaining:

    def __init__(self, dbRow):
        self.id = dbRow[0]
        self.name = dbRow[1]
        self.rank = dbRow[2]
        self.area = dbRow[3]
        self.stack = dbRow[4]
        self.percentage = dbRow[5]
        self.nodes = dbRow[6]


    def __repr__(self):
        return f"{self.__dict__!r}"
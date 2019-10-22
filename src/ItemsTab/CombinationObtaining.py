class CombinationObtaining:

    def __init__(self, dbRow):
        self.id = dbRow[0]

        self.resultID = dbRow[1]
        self.resultName = dbRow[2]
        self.resultIconName = dbRow[3]
        self.resultIconColor = dbRow[4]
        self.resultCategory = dbRow[5]

        self.firstID = dbRow[6]
        self.firstName = dbRow[7]
        self.firstIconName = dbRow[8]
        self.firstIconColor = dbRow[9]
        self.firstCategory = dbRow[10]

        self.secondID = dbRow[11]
        self.secondName = dbRow[12]
        self.secondIconName = dbRow[13]
        self.secondIconColor = dbRow[14]
        self.secondCategory = dbRow[15]

        self.quantity = dbRow[16]


    def __repr__(self):
        return f"{self.__dict__!r}"
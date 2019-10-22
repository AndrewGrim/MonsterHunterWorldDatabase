class RewardObtaining:

    def __init__(self, dbRow):
        self.id = dbRow[0]
        self.monsterName = dbRow[1]
        self.size = dbRow[2]
        self.rewardName = dbRow[3]
        self.rank = dbRow[4]
        self.stack = dbRow[5]
        self.percentage = dbRow[6]


    def __repr__(self):
        return f"{self.__dict__!r}"
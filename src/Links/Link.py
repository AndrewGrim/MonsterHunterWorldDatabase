class Link:

	def __init__(self):
		self.reset()


	def reset(self):
		self.event = False
		self.eventType = ""
		self.item = 0
		self.weapon = 0
		self.armor = 0
		self.decoration = 0
		self.skill = 0
		self.location = 0
		self.charm = 0
		self.kinsect = 0


	def __repr__(self):
		return f"{self.__dict__!r}"

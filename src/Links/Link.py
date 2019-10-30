class Link:

	def __init__(self):
		self.reset()


	def reset(self):
		self.event = False
		self.eventType = None
		self.info = 0


	def __repr__(self):
		return f"{self.__dict__!r}"

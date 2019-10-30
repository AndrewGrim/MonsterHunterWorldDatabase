class GenericDoubleLink:

	def __init__(self, info):
		self.id = info[0]
		self.category = info[1]


	def __repr__(self):
		return f"ID = {self.id}\nCategory = {self.category}"
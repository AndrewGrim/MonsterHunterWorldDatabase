class RedirectText():

	def __init__(self, wxTextCtrl):
		self.out = wxTextCtrl


	def write(self, string):
		self.out.WriteText(string)
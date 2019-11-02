import wx

from Utilities import debug

class Preferences:

	def __init__(self, root):
		self.root = root
		self.initialTab = None
		self.readPreferencesFile()
		self.misspelled = {
			"weapon": "Weapons", 
			"armors": "Armor", 
			"monster": "Monsters", 
			"decoration": "Decorations", 
			"item": "Items", 
			"charm": "Charms", 
			"location": "Locations", 
			"skill": "Skills",
		}


	def readPreferencesFile(self):
		f = open("preferences.config", "r")
		for line in f:
			line = line.strip("\n")
			if line == "[INITIAL TAB]":
				self.initialTab = f.readline()


	def getTabIndex(self, text:str) -> int:
		if text.lower() in self.misspelled.keys():
			text = self.misspelled[text.lower()]
		index = -1
		for i in range(self.root.mainNotebook.GetPageCount()):
			if self.root.mainNotebook.GetPageText(i) == text.capitalize():
				index = i
				break

		if index == -1:
				debug(text, "pref.text", "Tab name not found!")
				wx.MessageBox(f"Couldn't find the specified tab name: '{text}'",
						"Invalid tab name in preferences!",
						wx.OK|wx.ICON_INFORMATION)
				self.root.mainNotebook.SetSelection(0)

		return index 


	def __repr__(self):
		return f"{self.__dict__!r}"
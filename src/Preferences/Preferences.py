import wx
import os
from Debug.debug import debug

class Preferences:

	def __init__(self, root):
		self.root = root
		self.initialTab = None
		self.rememberSize = False
		self.rememberPosition = False
		self.windowSize = None
		self.windowPosition = None
		self.unicodeSymbols = False
		self.keepSearchOpen = False
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
		if not os.path.isfile("preferences.config"):
			self.writeDefaultPreferencesFile()
			wx.MessageBox("The preferences file could not be found and has been created with default values.", "Preferences file not found!", wx.OK|wx.ICON_INFORMATION)
		f = open("preferences.config", "r")
		for line in f:
			line = line.strip("\n")
			if line == "[INITIAL TAB]":
				self.initialTab = f.readline().strip("\n")
			elif line == "[WINDOW SIZE]":
				self.windowSize = (int(f.readline().strip("\n")), int(f.readline().strip("\n")))
			elif line == "[WINDOW POSITION]":
				self.windowPosition = (int(f.readline().strip("\n")), int(f.readline().strip("\n")))
			elif line == "[REMEMBER SIZE]":
				self.rememberSize = (self.strToBool(f.readline().strip("\n")))
			elif line == "[REMEMBER POSITION]":
				self.rememberPosition = (self.strToBool(f.readline().strip("\n")))
			elif line == "[USE UNICODE SYMBOLS]":
				self.unicodeSymbols = (self.strToBool(f.readline().strip("\n")))
			elif line == "[KEEP SEARCH WINDOW OPEN]":
				self.keepSearchOpen = (self.strToBool(f.readline().strip("\n")))

	def writePreferencesFile(self):
		settings = f"""
[INITIAL TAB]
{self.initialTab}
[WINDOW SIZE]
{self.windowSize[0]}
{self.windowSize[1]}
[WINDOW POSITION]
{self.windowPosition[0]}
{self.windowPosition[1]}
[REMEMBER SIZE]
{self.rememberSize}
[REMEMBER POSITION]
{self.rememberPosition}
[USE UNICODE SYMBOLS]
{self.unicodeSymbols}
[KEEP SEARCH WINDOW OPEN]
{self.keepSearchOpen}
""".strip("\n")

		f = open("preferences.config", "w")
		f.write(settings)


	def writeDefaultPreferencesFile(self):
		settings = f"""
[INITIAL TAB]
Monsters
[WINDOW SIZE]
1420
850
[WINDOW POSITION]
0
0
[REMEMBER SIZE]
False
[REMEMBER POSITION]
False
[USE UNICODE SYMBOLS]
True
[KEEP SEARCH WINDOW OPEN]
False
""".strip("\n")

		f = open("preferences.config", "w")
		f.write(settings)


	def strToBool(self, text: str) -> bool:
		if text.lower() == "false":
			return False
		elif text.lower() == "true":
			return True


	def getTabIndex(self, text:str) -> int:
		if text.lower() in self.misspelled.keys():
			text = self.misspelled[text.lower()]
			self.initialTab = text
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
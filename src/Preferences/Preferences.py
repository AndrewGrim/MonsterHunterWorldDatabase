import wx
import os

from Utilities import debug

class Preferences:

	def __init__(self, root):
		self.root = root
		self.initialTab = None
		self.rememberSize = False
		self.rememberPosition = False
		self.windowSize = None
		self.windowPosition = None
		self.autoExpand = False
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
			elif line == "[AUTO EXPAND MONSTER MATERIALS]":
				self.autoExpand = (self.strToBool(f.readline().strip("\n")))

	def writePreferencesFile(self):
		f = open("preferences.config", "w")
		f.write("[INITIAL TAB]\n")
		f.write(str(self.initialTab) + "\n")
		f.write("[WINDOW SIZE]\n")
		f.write(str(self.windowSize[0]) + "\n")
		f.write(str(self.windowSize[1]) + "\n")
		f.write("[WINDOW POSITION]\n")
		f.write(str(self.windowPosition[0]) + "\n")
		f.write(str(self.windowPosition[1]) + "\n")
		f.write("[REMEMBER SIZE]\n")
		f.write(str(self.rememberSize) + "\n")
		f.write("[REMEMBER POSITION]\n")
		f.write(str(self.rememberPosition) + "\n")
		f.write("[AUTO EXPAND MONSTER MATERIALS]\n")
		f.write(str(self.autoExpand) + "\n")

	def writeDefaultPreferencesFile(self):
		f = open("preferences.config", "w")
		f.write("[INITIAL TAB]\n")
		f.write("Monsters" + "\n")
		f.write("[WINDOW SIZE]\n")
		f.write("1420" + "\n")
		f.write("850" + "\n")
		f.write("[WINDOW POSITION]\n")
		f.write("0" + "\n")
		f.write("0" + "\n")
		f.write("REMEMBER SIZE" + "\n")
		f.write("False" + "\n")
		f.write("REMEMBER POSITION" + "\n")
		f.write("False" + "\n")
		f.write("[AUTO EXPAND MONSTER MATERIALS]\n")
		f.write("False" + "\n")


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
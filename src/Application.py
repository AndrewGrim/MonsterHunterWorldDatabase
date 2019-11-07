import wx
import wx.grid
import time
import sys
import platform

import CustomGridRenderer as cgr
import MonstersTab as m
import WeaponsTab as w
import ArmorTab as a
import ItemsTab as i
import DecorationsTab as d
import SkillsTab as s
import CharmsTab as c
import LocationsTab as l
import KinsectsTab as k
import Utilities as util
import Links as link
import Preferences as p
import Debug as debug
import AboutWindow as about
import SearchWindow as search

class Application(wx.Frame):

	def __init__(self, *args, **kw):
		super(Application, self).__init__(*args, **kw)

		cmdArgs = sys.argv
		self.windowWidth = 0 
		self.windowHeight = 0
		if "-size" in cmdArgs:
			index = cmdArgs.index("-size")
			self.windowWidth = int(cmdArgs[index + 1])
			self.windowHeight = int(cmdArgs[index + 2])

		root = self
		self.SetIcon(wx.Icon("images/Nergigante.png"))
		self.SetTitle("Database")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.pref = p.Preferences(root)

		self.link = link.Link()

		self.initMainNotebook()
		il = wx.ImageList(24, 24)
		mon = il.Add(wx.Bitmap("images/Nergigante24.png"))
		wep = il.Add(wx.Bitmap("images/weapons/great-sword/rarity-24/5.png"))
		arm = il.Add(wx.Bitmap("images/armor/armorset/rarity-24/8.png"))
		charm = il.Add(wx.Bitmap("images/charms-24/7.png"))
		deco = il.Add(wx.Bitmap("images/items-24/FeystoneGold.png"))
		skill = il.Add(wx.Bitmap("images/skills-24/SkillBlue.png"))
		item = il.Add(wx.Bitmap("images/items-24/TrapGreen.png"))
		local = il.Add(wx.Bitmap("images/locations-24/Elder's Recess.png"))
		self.mainNotebook.AssignImageList(il)

		self.monsters = m.MonstersTab(root, self.mainNotebook, self.link)
		self.weapons = w.WeaponsTab(root, self.mainNotebook, self.link)
		self.armor = a.ArmorTab(root, self.mainNotebook, self.link)
		self.charms = c.CharmsTab(root, self.mainNotebook, self.link)
		self.decos = d.DecorationsTab(root, self.mainNotebook, self.link)
		self.skills = s.SkillsTab(root, self.mainNotebook, self.link)
		self.items = i.ItemsTab(root, self.mainNotebook, self.link)
		self.locations = l.LocationsTab(root, self.mainNotebook, self.link)
		#self.kinsects = k.KinsectsTab(root, self.mainNotebook) # TODO need images

		self.mainNotebook.SetPageImage(0, mon)
		self.mainNotebook.SetPageImage(1, wep)
		self.mainNotebook.SetPageImage(2, arm)
		self.mainNotebook.SetPageImage(3, charm)
		self.mainNotebook.SetPageImage(4, deco)
		self.mainNotebook.SetPageImage(5, skill)
		self.mainNotebook.SetPageImage(6, item)
		self.mainNotebook.SetPageImage(7, local)	

		self.makeMenuBar()
		self.CreateStatusBar()

		self.SetStatusText("Copyright © AndrewGrim https://github.com/AndrewGrim")

		try:
			self.mainNotebook.SetSelection(self.pref.getTabIndex(self.pref.initialTab))
		except Exception as e:
			print(e)
			self.mainNotebook.SetSelection(0)

		if self.windowWidth != 0:
			self.SetSize(self.windowWidth - 1, self.windowHeight)
		else:
			if self.pref.rememberSize:
				self.SetSize(self.pref.windowSize[0] - 1, self.pref.windowSize[1])
			else:
				self.SetSize(1419, 850)

		if self.pref.rememberPosition:
			self.SetPosition(self.pref.windowPosition)
		else:
			self.Center()	

		wi, he = self.GetSize()
		self.SetSize(wi + 1, he)

		if "-debug" in cmdArgs:
			self.debugWindow(None)

		self.Show()


	def initMainNotebook(self):
		# the outermost panel holding in all the widgets
		self.mainPanel = wx.Panel(self)
		# main geometry manager
		self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
		# main notebook holding the top tabs ie: monsters, weapons etc.
		self.mainNotebook = wx.Notebook(self.mainPanel)
		# add notebook to sizer
		self.mainSizer.Add(self.mainNotebook, 1, wx.EXPAND)

		# set the sizer for mainWindow
		self.mainPanel.SetSizer(self.mainSizer)


	def followLink(self):
		if self.link.event == True:
			if self.link.eventType == "item":
				self.items.currentItemCategory = self.link.info.category
				self.items.loadItemList()
				self.items.currentlySelectedItemID = self.link.info.id
				self.items.loadItemDetailAll()
				self.selectTab("Items")

			elif self.link.eventType == "skill":
				self.skills.currentSkillID = self.link.info.id
				self.skills.loadSkillDetail()
				self.selectTab("Skills")

			elif self.link.eventType == "decoration":
				self.decos.currentDecorationID = self.link.info.id
				self.decos.loadDecorationDetail()
				self.selectTab("Decorations")

			elif self.link.eventType == "charm":
				self.charms.currentCharmID = self.link.info.id
				self.charms.loadCharmDetail()
				self.selectTab("Charms")

			elif self.link.eventType == "armor":
				self.armor.currentlySelectedArmorID = self.link.info.id
				if self.armor.currentArmorTree != self.link.info.category:
					self.armor.currentArmorTree = self.link.info.category
					self.armor.loadArmorTree()
				self.armor.loadArmorDetailAll()
				self.selectTab("Armor")

			elif self.link.eventType == "armorset":
				self.armor.currentlySelectedArmorSetID = self.link.info.id
				if self.armor.currentArmorTree != self.link.info.category:
					self.armor.currentArmorTree = self.link.info.category
					self.armor.loadArmorTree()
				self.armor.loadArmorSetDetail()
				self.selectTab("Armor")
				self.armor.armorDetailsNotebook.SetSelection(1)

			elif self.link.eventType == "weapon":
				self.weapons.skip = True
				self.weapons.currentlySelectedWeaponID = self.link.info.id
				if self.weapons.currentWeaponTree != self.link.info.category:
					self.weapons.currentWeaponTree = self.link.info.category
					self.weapons.loadWeaponTree()
				self.weapons.loadWeaponDetailAll()
				self.selectTab("Weapons")

			elif self.link.eventType == "monster":
				self.monsters.currentMonsterID = self.link.info.id
				self.monsters.currentMonsterName = self.link.info.category
				self.monsters.loadMonsterDetail()
				self.selectTab("Monsters")

			elif self.link.eventType == "location":
				self.locations.currentLocationID = self.link.info.id
				self.locations.currentLocationName = self.link.info.category
				self.locations.loadLocationDetail()
				self.selectTab("Locations")

			else:
				debug(self.link, "self.link", "Link type not supported!")


	def selectTab(self, text:str) -> None:
		index = -1
		for i in range(self.mainNotebook.GetPageCount()):
			if self.mainNotebook.GetPageText(i) == text:
				index = i
				break
		assert index > -1, "Tab not found! The page index is -1, must be >= 0."
		self.mainNotebook.SetSelection(index) 


	def reloadUnicode(self):
		self.monsters.loadMonsterSummary()
		self.weapons.loadWeaponTree()
		self.weapons.loadWeaponDetailAll()
		self.armor.loadArmorTree()
		self.armor.loadArmorDetailAll()
		self.charms.loadCharmDetail()
		self.decos.loadDecorationDetail()
		self.skills.loadSkillDetail()


	def reloadMaterials(self):
		self.monsters.loadMonsterMaterials()


	def makeMenuBar(self):
		fileMenu = wx.Menu()
		searchItem = fileMenu.Append(-1, "&Search\tCtrl-F", "Searches for the given phrase globally.")
		exitItem = fileMenu.Append(-1, "&Quit\tCtrl-Q", "Exits the program.")

		optionsMenu = wx.Menu()
		prefItem = optionsMenu.Append(-1, "&Preferences\tCtrl-P", "A window used to set preferences.")
		debugItem = optionsMenu.Append(-1, "&Debug\tCtrl-D", "A debug window that redirects the wx errors and stdout/sterr to itself.")

		helpMenu = wx.Menu()
		aboutItem = helpMenu.Append(-1, "About", "Shows a dialog with information about the application.")

		menuBar = wx.MenuBar()
		menuBar.Append(fileMenu, "&File")
		menuBar.Append(optionsMenu, "&Options")
		menuBar.Append(helpMenu, "&Help")

		self.SetMenuBar(menuBar)

		self.Bind(wx.EVT_MENU, self.onSearch, searchItem)
		self.Bind(wx.EVT_MENU, self.onClose, exitItem)
		self.Bind(wx.EVT_MENU, self.preferencesWindow, prefItem)
		self.Bind(wx.EVT_MENU, self.debugWindow, debugItem)
		self.Bind(wx.EVT_MENU, self.onAbout, aboutItem)


	def onSearch(self, event):
		self.search = search.SearchWindow(self, self.link)

	
	def onClose(self, event):
		self.pref.windowSize = self.GetSize()
		self.pref.windowPosition = self.GetPosition()
		self.pref.writePreferencesFile()

		try:
			self.debug.onClose(None)
		except:
			pass

		sys.exit()


	def debugWindow(self, event):
		self.debug = debug.DebugWindow(self)


	def preferencesWindow(self, event):
		p.PreferencesWindow(self, self.pref)


	def onAbout(self, event):
		self.about = about.AboutWindow(self)


if __name__ == '__main__':
	start = time.time()
	app = wx.App()
	frm = Application(None, title="Database")
	end = time.time()
	print(f"Application load time: {round(end - start, 2)}s")
	if "-speedTest" in sys.argv:
		speedTest = True
	else:
		speedTest = False
	if speedTest:
		sys.exit()
	app.MainLoop()
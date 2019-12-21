import wx
import wx.grid
import time
import sys
import platform

import CustomGridRenderer as cgr
import MonstersTab as m
import WeaponsTab as w
import ArmorTab as a
import PalicoTab as pp
import ItemsTab as i
import DecorationsTab as d
import SkillsTab as s
import CharmsTab as c
import LocationsTab as l
import KinsectsTab as k
import QuestsTab as q
import ToolsTab as t
import Utilities as util
import Links as link
import Preferences as p
from Debug.debug import debug
import Debug.DebugWindow
import AboutWindow as about
import SearchWindow as search
import LoadingWindow as load

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
		self.Center()	
		lo = load.LoadingWindow(self)
		self.SetIcon(wx.Icon("images/Nergigante.png"))
		self.SetTitle("Monster Hunter World Database")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.pref = p.Preferences(root)
		self.link = link.Link()

		self.initMainNotebook()
		il = wx.ImageList(24, 24)
		mon = il.Add(wx.Bitmap("images/Nergigante24.png"))
		que = il.Add(wx.Bitmap("images/rank-stars-24/hr.png")) # TODO change to proper icon
		wep = il.Add(wx.Bitmap("images/weapons/great-sword/rarity-24/5.png"))
		arm = il.Add(wx.Bitmap("images/armor/armorset/rarity-24/8.png"))
		tool = il.Add(wx.Bitmap("images/hunter-tools-24/Challenger Mantle.png"))
		pal = il.Add(wx.Bitmap("images/palico/head-rarity-24/9.png"))
		kin = il.Add(wx.Bitmap("images/kinsects/blunt-rarity-24/10.png"))
		charm = il.Add(wx.Bitmap("images/charms-24/7.png"))
		deco = il.Add(wx.Bitmap("images/items-24/FeystoneGold.png"))
		skill = il.Add(wx.Bitmap("images/skills-24/SkillBlue.png"))
		item = il.Add(wx.Bitmap("images/items-24/TrapGreen.png"))
		local = il.Add(wx.Bitmap("images/locations-24/Elder's Recess.png"))
		self.mainNotebook.AssignImageList(il)

		lo.loading.SetValue(30)
		self.monsters = m.MonstersTab(root, self.mainNotebook, self.link)
		self.quests = q.QuestsTab(root, self.mainNotebook, self.link)
		lo.loading.SetValue(60)
		self.weapons = w.WeaponsTab(root, self.mainNotebook, self.link)
		lo.loading.SetValue(80)
		self.armor = a.ArmorTab(root, self.mainNotebook, self.link)
		self.hunterTools = t.ToolsTab(root, self.mainNotebook, self.link)
		lo.loading.SetValue(90)
		self.palico = pp.PalicoTab(root, self.mainNotebook, self.link)
		self.kinsects = k.KinsectsTab(root, self.mainNotebook)
		lo.loading.SetValue(100)
		self.charms = c.CharmsTab(root, self.mainNotebook, self.link)
		self.decos = d.DecorationsTab(root, self.mainNotebook, self.link)
		self.skills = s.SkillsTab(root, self.mainNotebook, self.link)
		self.items = i.ItemsTab(root, self.mainNotebook, self.link)
		self.locations = l.LocationsTab(root, self.mainNotebook, self.link)

		self.mainNotebook.SetPageImage(0, mon)
		self.mainNotebook.SetPageImage(1, que)
		self.mainNotebook.SetPageImage(2, wep)
		self.mainNotebook.SetPageImage(3, arm)
		self.mainNotebook.SetPageImage(4, tool)
		self.mainNotebook.SetPageImage(5, pal)
		self.mainNotebook.SetPageImage(6, kin)
		self.mainNotebook.SetPageImage(7, charm)
		self.mainNotebook.SetPageImage(8, deco)
		self.mainNotebook.SetPageImage(9, skill)
		self.mainNotebook.SetPageImage(10, item)
		self.mainNotebook.SetPageImage(11, local)	

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
				self.SetSize(1429, 850)

		if self.pref.rememberPosition:
			self.SetPosition(self.pref.windowPosition)
		else:
			self.Center()	

		wi, he = self.GetSize()
		self.SetSize(wi + 1, he)

		if "-debug" in cmdArgs:
			self.debugWindow(None)

		
		lo.win.Destroy()
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

			elif self.link.eventType == "armor" or self.link.eventType == "armorset":
				self.armor.currentlySelectedArmorID = self.link.info.id
				if self.armor.currentArmorTree != self.link.info.category:
					self.armor.currentArmorTree = self.link.info.category
					self.armor.loadArmorTree()
				self.armor.loadArmorDetailAll()
				self.selectTab("Armor")
				if self.link.eventType == "armor":
					self.armor.armorDetailsNotebook.SetSelection(0)
				else:
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

			elif self.link.eventType == "palico":
				self.palico.currentEquipmentID = self.link.info.id
				if self.palico.currentEquipmentTree != self.link.info.category:
					self.palico.currentEquipmentTree = self.link.info.category
					self.palico.loadEquipmentTree()
				self.palico.loadEquipmentDetailTab()
				self.selectTab("Palico")
				self.palico.palicoNotebook.SetSelection(0)

			elif self.link.eventType == "gadget":
				self.palico.currentGadgetID = self.link.info.id
				self.palico.loadGadgetDetail()
				self.selectTab("Palico")
				self.palico.palicoNotebook.SetSelection(1)

			elif self.link.eventType == "kinsect":
				self.kinsects.currentlySelectedKinsectID = self.link.info.id
				self.kinsects.loadKinsectDetails()
				self.selectTab("Kinsects")

			elif self.link.eventType == "quest":
				self.quests.currentlySelectedQuestID = self.link.info.id
				if self.quests.currentQuestTree != self.link.info.category:
					self.quests.currentQuestTree = self.link.info.category
					self.quests.loadQuestTree()
				self.quests.loadQuestDetail()
				self.selectTab("Quests")

			elif self.link.eventType == "tool":
				self.hunterTools.currentlySelectedToolID = self.link.info.id
				self.hunterTools.loadToolDetail()
				self.selectTab("Tools")

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
		self.quests.loadQuestDetail()
		self.weapons.loadWeaponTree()
		self.weapons.loadWeaponDetailAll()
		self.armor.loadArmorTree()
		self.armor.loadArmorDetailAll()
		self.charms.loadCharmDetail()
		self.palico.loadEquipmentTree()
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
		self.debug = Debug.DebugWindow(self)


	def preferencesWindow(self, event):
		p.PreferencesWindow(self, self.pref)


	def onAbout(self, event):
		self.about = about.AboutWindow(self)


if __name__ == '__main__':
	start = time.time()
	app = wx.App()
	frm = Application(None)
	end = time.time()
	print(f"Application load time: {round(end - start, 2)}s")
	if "-speedTest" in sys.argv:
		speedTest = True
	else:
		speedTest = False
	if speedTest:
		sys.exit()
	app.MainLoop()
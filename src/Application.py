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

class Application(wx.Frame):

	def __init__(self, *args, **kw):
		super(Application, self).__init__(*args, **kw)

		cmdArgs = sys.argv
		self.windowWidth = 1420 
		self.windowHeight = 900
		if "-size" in cmdArgs:
			index = cmdArgs.index("-size")
			self.windowWidth = int(cmdArgs[index + 1])
			self.windowHeight = int(cmdArgs[index + 2])

		root = self
		self.SetIcon(wx.Icon("images/Nergigante.png"))
		self.SetSize(1200, 1000)
		self.SetTitle("Database")

		self.link = link.Link()

		self.initMainNotebook()
		il = wx.ImageList(24, 24)
		mon = il.Add(wx.Bitmap("images/Nergigante24.png"))
		wep = il.Add(wx.Bitmap("images/weapons/great-sword/rarity-24/5.png"))
		arm = il.Add(wx.Bitmap("images/armor/armorset/rarity-24/8.png"))
		charm = il.Add(wx.Bitmap("images/charms-24/7.png"))
		deco = il.Add(wx.Bitmap("images/materials-24/FeystoneGold.png"))
		skill = il.Add(wx.Bitmap("images/skills-24/SkillBlue.png"))
		item = il.Add(wx.Bitmap("images/materials-24/TrapGreen.png"))
		local = il.Add(wx.Bitmap("images/locations-24/Elder's Recess.png"))
		self.mainNotebook.AssignImageList(il)

		self.monsters = m.MonstersTab(root, self.mainNotebook, self.link)
		w.WeaponsTab(root, self.mainNotebook, self.link)
		a.ArmorTab(root, self.mainNotebook, self.link)
		c.CharmsTab(root, self.mainNotebook, self.link)
		d.DecorationsTab(root, self.mainNotebook)
		s.SkillsTab(root, self.mainNotebook)
		self.items = i.ItemsTab(root, self.mainNotebook, self.link)
		l.LocationsTab(root, self.mainNotebook)
		#k.KinsectsTab(root, self.mainNotebook)

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

		self.SetSize(self.windowWidth, self.windowHeight)
		self.Center()

		# TEST
		self.mainNotebook.SetSelection(2)

		self.Show()
		if "-debug" in cmdArgs:
			self.debugWindow(None)


	def initMainNotebook(self):
		# the outermost panel holding in all the widgets
		self.mainPanel = wx.Panel(self)
		# main geometry manager
		self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
		# main notebook holding the top tabs ie: monsters, weapons etc.
		self.mainNotebook = wx.Notebook(self.mainPanel)
		self.mainNotebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onTabChanged)
		# add notebook to sizer
		self.mainSizer.Add(self.mainNotebook, 1, wx.EXPAND)

		# set the sizer for mainWindow
		self.mainPanel.SetSizer(self.mainSizer)


	def onTabChanged(self, event):
		if event.GetEventObject() == self.mainNotebook:
			w, h = self.GetSize()
			self.SetSize(w + 3, h)
			self.SetSize(w, h)


	def followLink(self):
		if self.link.event == True:
			if self.link.eventType == "item":
				self.items.currentItemCategory = self.link.item.category
				self.items.loadItemList()
				self.items.currentlySelectedItemID = self.link.item.id
				self.items.loadItemDetail()
				self.items.loadItemUsage()
				self.items.loadItemObtaining()
				index = -1
				for i in range(self.mainNotebook.GetPageCount()):
					if self.mainNotebook.GetPageText(i) == "Items":
						index = i
						break
				assert index > -1, "The page index must be at least 0 and usually higher!"
				self.mainNotebook.SetSelection(index) 


	# TODO make a preferences page
	def makeMenuBar(self):
		fileMenu = wx.Menu()
		exitItem = fileMenu.Append(-1, "&Quit\tCtrl-Q", "Exits the program.")

		helpMenu = wx.Menu()
		aboutItem = helpMenu.Append(-1, "About", "Shows a dialog with information about the application.")

		optionsMenu = wx.Menu()
		debugItem = optionsMenu.Append(-1, "&Debug\tCtrl-D", "A debug window that redirects the wx errors and stdout/sterr to itself.")

		menuBar = wx.MenuBar()
		menuBar.Append(fileMenu, "&File")
		menuBar.Append(helpMenu, "&Help")
		menuBar.Append(optionsMenu, "&Options")

		self.SetMenuBar(menuBar)

		self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)
		self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)
		self.Bind(wx.EVT_MENU, self.debugWindow, debugItem)


	def debugWindow(self, event):
		self.log = wx.LogWindow(self, "Debug", show=True)
		frame = self.log.GetFrame()
		frame.SetIcon(wx.Icon("images/Nergigante.png"))
		frame.SetSize(400, self.windowHeight)
		frame.SetPosition((self.GetPosition()[0] - 385, self.GetPosition()[1]))
		text = self.log.GetFrame().GetChildren()[0]

		assert type(text) == wx.TextCtrl, "Redirect target must be a wx.TextCtrl!"

		wx.Log.SetActiveTarget(self.log)

		redir=util.RedirectText(text)
		sys.stdout=redir
		sys.stderr=redir

		self.SetFocus()


	def OnExit(self, event):
		self.Close(True)


	def OnAbout(self, event):
		# TODO make a custom messagebox with links to github profiles
		#https://wxpython.org/Phoenix/docs/html/wx.MessageDialog.html
		#https://wxpython.org/Phoenix/docs/html/wx.lib.agw.hyperlink.HyperLinkCtrl.html
		wx.MessageBox("Created by github.com/AndrewGrim.\n" + 
						"This application uses a database and images from github.com/gatheringhallstudios\n" +
						"as well as some of their SQL queries and their sharpness adjust function.\n" +
						"All licenses are MIT.\n" +
						"https://github.com/gatheringhallstudios/MHWorldDatabase\n" +
						"https://github.com/gatheringhallstudios/MHWorldData",
						"About",
						wx.OK|wx.ICON_INFORMATION)


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
	# TEST
	if speedTest:
		sys.exit()
	app.MainLoop()
import wx
import wx.grid
import time
import sys

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
		icon = wx.Icon("images/OfflineDatabase.ico") # TODO possibly change to nerg for base game and velkhana for iceborne, same with pyinstaller icon
		self.SetIcon(icon)
		self.SetSize(1200, 1000)
		self.SetTitle("Database")

		self.link = util.Link()

		self.initMainNotebook()
		self.monsters = m.MonstersTab(root, self.mainNotebook, self.link)
		#w.WeaponsTab(root, self.mainNotebook)
		a.ArmorTab(root, self.mainNotebook)
		#self.items = i.ItemsTab(root, self.mainNotebook, self.link)
		#d.DecorationsTab(root, self.mainNotebook)
		#s.SkillsTab(root, self.mainNotebook)
		#c.CharmsTab(root, self.mainNotebook)
		#l.LocationsTab(root, self.mainNotebook)
		#k.KinsectsTab(root, self.mainNotebook)
			
		self.makeMenuBar()
		self.CreateStatusBar()

		self.SetStatusText("Welcome to wxPython!")

		self.SetSize(self.windowWidth, self.windowHeight)
		self.Center()

		# TEST
		self.mainNotebook.SetSelection(1)

		self.Show()


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
			self.SetSize(self.windowWidth + 3, self.windowHeight)
			self.SetSize(self.windowWidth, self.windowHeight)


	def followLink(self):
		if self.link.event == True:
			if self.link.eventType == "item":
				self.items.itemList.ClearAll()
				self.items.currentItemCategory = self.link.item.category
				self.items.loadItemList()
				self.items.currentlySelectedItemID = self.link.item.id
				self.items.loadItemDetail()
				self.items.loadItemUsage()
				self.items.loadItemObtaining()
				self.mainNotebook.SetSelection(1) # TEST needs to be changed if more tabs are loaded
				# prob make a dict for all the tabs with their respective indexes


	# TODO make a preferences page
	def makeMenuBar(self):
		fileMenu = wx.Menu()
		# The "\t..." syntax defines an accelerator key that also triggers the same event
		helloItem = fileMenu.Append(-1, "&Hello...\tCtrl-H",
				"Help string shown in status bar for this menu item")
		fileMenu.AppendSeparator()

		exitItem = fileMenu.Append(wx.ID_EXIT)

		helpMenu = wx.Menu()
		aboutItem = helpMenu.Append(wx.ID_ABOUT)

		menuBar = wx.MenuBar()
		menuBar.Append(fileMenu, "&File")
		menuBar.Append(helpMenu, "&Help")

		self.SetMenuBar(menuBar)

		self.Bind(wx.EVT_MENU, self.OnHello, helloItem)
		self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)
		self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)


	def OnExit(self, event):
		self.Close(True)


	def OnHello(self, event):
		wx.MessageBox("Hello again from wxPython")


	def OnAbout(self, event):
		wx.MessageBox("This is a wxPython Hello World sample",
						"About Hello World 2",
						wx.OK|wx.ICON_INFORMATION)


if __name__ == '__main__':
	start = time.time()
	app = wx.App()
	frm = Application(None, title="Database")
	end = time.time()
	print("application load time: " + str(end - start))
	if "-speedTest" in sys.argv:
		speedTest = True
	else:
		speedTest = False
	# TEST
	if speedTest:
		sys.exit()
	app.MainLoop()
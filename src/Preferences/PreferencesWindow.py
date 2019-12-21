import wx

class PreferencesWindow:

	def __init__(self, root, preferences):
		self.root = root
		self.pref = preferences

		self.win = wx.Frame(self.root, title="Preferences")
		self.win.SetIcon(wx.Icon("images/Nergigante.png"))
		self.win.SetSize(300, 300)
		self.win.Center()
		self.win.Bind(wx.EVT_CLOSE, self.onClose)

		panel = wx.Panel(self.win)
		sizer = wx.BoxSizer(wx.VERTICAL)
		vSizer = wx.BoxSizer(wx.VERTICAL)

		tabs = ["Monsters", "Quests", "Weapons", "Armor", "Tools", "Palico", "Kinsects" "Charms", "Decorations", "Skills", "Items", "Locations",]
		self.label = wx.StaticText(panel, label="Set initial tab:")
		self.selectTab = wx.Choice(panel, choices=tabs, size=(200, 20))
		self.selectTab.SetSelection(self.selectTab.FindString(self.pref.initialTab))

		self.rememberSize = wx.CheckBox(panel, label="Remember window size", size=(200, 20))
		self.rememberSize.SetValue(self.pref.rememberSize)
		self.rememberPosition = wx.CheckBox(panel, label="Remember window position", size=(200, 20))
		self.rememberPosition.SetValue(self.pref.rememberPosition)
		self.unicodeSymbols = wx.CheckBox(panel, label="Use unicode symbols", size=(200, 20))
		self.unicodeSymbols.SetValue(self.pref.unicodeSymbols)
		self.keepSearchOpen = wx.CheckBox(panel, label="Keep search window open", size=(200, 20))
		self.keepSearchOpen.SetValue(self.pref.keepSearchOpen)

		vSizer.Add(self.label, 1, wx.LEFT)
		vSizer.Add(self.selectTab, 1, wx.CENTER)
		vSizer.Add((0, 20))
		vSizer.Add(self.rememberSize, 1, wx.CENTER)
		vSizer.Add((0, 20))
		vSizer.Add(self.rememberPosition, 1, wx.CENTER)
		vSizer.Add((0, 20))
		vSizer.Add(self.unicodeSymbols, 1, wx.CENTER)
		vSizer.Add((0, 20))
		vSizer.Add(self.keepSearchOpen, 1, wx.CENTER)

		sizer.Add((0,0), 1, wx.EXPAND)
		sizer.Add(vSizer, 0, wx.CENTER)
		sizer.Add((0,0), 1, wx.EXPAND)

		panel.SetSizer(sizer)

		self.makeMenuBar()

		self.win.Show()


	def makeMenuBar(self):
		fileMenu = wx.Menu()
		closeItem = fileMenu.Append(-1, "&Close\tCtrl-P", "Closes the preferences window.")
		
		menuBar = wx.MenuBar()
		menuBar.Append(fileMenu, "&File")

		self.win.SetMenuBar(menuBar)

		self.win.Bind(wx.EVT_MENU, self.onClose, closeItem)


	def onClose(self, event):
		r = False
		a = False
		self.pref.initialTab = self.selectTab.GetString(self.selectTab.GetSelection())
		self.pref.rememberSize = self.rememberSize.GetValue()
		self.pref.rememberPosition = self.rememberPosition.GetValue()
		if self.pref.unicodeSymbols != self.unicodeSymbols.GetValue():
			r = True
		self.pref.unicodeSymbols = self.unicodeSymbols.GetValue()
		if r:
			self.root.reloadUnicode()
		if a:
			self.root.reloadMaterials()
		self.pref.keepSearchOpen = self.keepSearchOpen.GetValue()
			
		self.pref.writePreferencesFile()
		
		self.win.Destroy()
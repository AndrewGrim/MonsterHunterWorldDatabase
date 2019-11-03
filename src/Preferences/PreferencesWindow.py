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

		tabs = ["Monsters", "Weapons", "Armor", "Charms", "Decorations", "Skills", "Items", "Locations",]
		self.label = wx.StaticText(panel, label="Set initial tab:")
		self.selectTab = wx.Choice(panel, choices=tabs, size=(200, 20))
		self.selectTab.SetSelection(self.selectTab.FindString(self.pref.initialTab))

		self.rememberSize = wx.CheckBox(panel, label="Remember window size", size=(200, 20))
		self.rememberSize.SetValue(self.pref.rememberSize)
		self.rememberPosition = wx.CheckBox(panel, label="Remember window position", size=(200, 20))
		self.rememberPosition.SetValue(self.pref.rememberPosition)
		self.autoExpand = wx.CheckBox(panel, label="Auto expand monster materials", size=(200, 20))
		self.autoExpand.SetValue(self.pref.autoExpand)
		self.unicodeSymbols = wx.CheckBox(panel, label="Use unicode symbols", size=(200, 20))
		self.unicodeSymbols.SetValue(self.pref.unicodeSymbols)

		vSizer.Add(self.label, 1, wx.LEFT)
		vSizer.Add(self.selectTab, 1, wx.CENTER)
		vSizer.Add((0, 20))
		vSizer.Add(self.rememberSize, 1, wx.CENTER)
		vSizer.Add((0, 20))
		vSizer.Add(self.rememberPosition, 1, wx.CENTER)
		vSizer.Add((0, 20))
		vSizer.Add(self.autoExpand, 1, wx.CENTER)
		vSizer.Add((0, 20))
		vSizer.Add(self.unicodeSymbols, 1, wx.CENTER)

		sizer.Add((0,0), 1, wx.EXPAND)
		sizer.Add(vSizer, 0, wx.CENTER)
		sizer.Add((0,0), 1, wx.EXPAND)

		panel.SetSizer(sizer)

		self.win.Show()


	def onClose(self, event):
		r = False
		a = False
		self.pref.initialTab = self.selectTab.GetString(self.selectTab.GetSelection())
		self.pref.rememberSize = self.rememberSize.GetValue()
		self.pref.rememberPosition = self.rememberPosition.GetValue()
		if self.pref.autoExpand != self.autoExpand.GetValue():
			a = True
		self.pref.autoExpand = self.autoExpand.GetValue()
		if self.pref.unicodeSymbols != self.unicodeSymbols.GetValue():
			r = True
		self.pref.unicodeSymbols = self.unicodeSymbols.GetValue()
		if r:
			self.root.reloadUnicode()
		if a:
			self.root.reloadMaterials()
			
		self.pref.writePreferencesFile()
		
		self.win.Destroy()
import wx
import wx.grid
import sqlite3

class HelloFrame(wx.Frame): # frame would be a tk window

	def __init__(self, *args, **kw):
		# ensure the parent's __init__ is called
		super(HelloFrame, self).__init__(*args, **kw)

		icon = wx.Icon("images/OfflineDatabase.ico")
		self.SetIcon(icon)
		self.SetSize(1000, 1000)
		self.SetTitle("Database")

		# create a panel in the frame
		#pnl = wx.Panel(self) # or frame in tk

		# put some text with a larger bold font on it
		#st = wx.StaticText(pnl, label="Hello World!") # static text ie label
		#font = st.GetFont()
		#font.PointSize += 10
		#font = font.Bold()
		#st.SetFont(font)

		# notebook
		#self.notebook = wx.Notebook(pnl)
		#self.frame = wx.Panel(self.notebook)
		#self.frame2 = wx.Panel(self.notebook)
		#self.notebook.AddPage(self.frame, "Tab 1")
		#self.notebook.AddPage(self.frame2, "Tab 2")

		# grid table
		self.table = wx.grid.Grid(self) #self.frame
		self.table.CreateGrid(60, 5)
		self.table.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.onSingleSelect)
		self.table.Bind(wx.EVT_SIZE, self.onSize)
		#self.sizer2 = wx.BoxSizer(wx.VERTICAL)
		#self.sizer2.Add(self.table, 1, wx.EXPAND|wx.ALL)
		#table.SetRowSize(0, 60) # row index 0, width 60 something
		#table.SetColSize(0, 120)
		#table.SetCellValue(0, 0, "wxGrid is dope")
		#table.SetReadOnly(0, 0)
		#table.SetCellTextColour(0, 0, wx.BLUE)
		#table.SetCellBackgroundColour(0, 0, wx.YELLOW)
		#table.SetColFormatFloat(5, 6, 2) # \\\width 6, precision 2
		#table.SetCellValue(0, 1, "3.1415")

		# and create a sizer to manage the layout of child widgets
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.table, 0, wx.EXPAND) # self.notebook
		self.SetSizer(sizer)
		#sizer.Fit(self)
		#pnl.SetSizer(sizer)
		#sizer.Fit(pnl)

		# create a menu bar
		self.makeMenuBar()

		# and a status bar
		self.CreateStatusBar()
		self.SetStatusText("Welcome to wxPython!")

		# db
		#wx.Bind(self, wx.GridRangeSelectEvent(), onSelection, source=None, id=wx.ID_ANY, id2=wx.ID_ANY)
		self.loadData()


	def onSize(self, event):
		width, height = self.GetSize()
		numOfColumns = 5
		# all columns equal width
		for col in range(numOfColumns):
			self.table.SetColSize(col, (width / numOfColumns) - 13) 
		# the name and species columns are longer than the rest
		#self.table.SetColSize(0, (width / 3) / 3) 
		#self.table.SetColSize(1, width / 3.3)
		#self.table.SetColSize(2, width / 3.3)
		#self.table.SetColSize(3, (width / 3) / 3)
		#self.table.SetColSize(4, (width / 3) / 3)
	


	def loadData(self):
		conn = sqlite3.connect("../wxTable/MonsterHunter.db")
		data = conn.execute("SELECT * FROM monsters")
		i = 0
		for row in data:
			#print("________________________________________________________________")
			#print("| {:<3} | {:<20} | {:<15} | {:<5} | {:<5} |".format(row[0], row[1], row[2], row[3], row[4]))
			self.table.SetCellValue(i, 0, str(row[0]))
			self.table.SetCellValue(i, 1, row[1])
			self.table.SetCellValue(i, 2, row[2])
			self.table.SetCellValue(i, 3, row[3])
			self.table.SetCellValue(i, 4, row[4])
			i += 1
			# GetGridCursorCoords(self)

		#self.frame.SetSizer(self.sizer2)
		#self.sizer2.Fit(self.frame)
		#self.table.Fit()
		self.table.SetRowLabelSize(30)
		self.table.SetColLabelSize(30)
		self.table.SetColLabelValue(0, "ID")
		self.table.SetColLabelValue(1, "Name")
		self.table.SetColLabelValue(2, "Species")
		self.table.SetColLabelValue(3, "Generation")
		self.table.SetColLabelValue(4, "Size")



	def onSingleSelect(self, event):
		print("row: {}, col: {}".format(event.GetRow(), event.GetCol()))


	def makeMenuBar(self):
		# Make a file menu with Hello and Exit items
		fileMenu = wx.Menu()
		# The "\t..." syntax defines an accelerator key that also triggers
		# the same event
		helloItem = fileMenu.Append(-1, "&Hello...\tCtrl-H",
				"Help string shown in status bar for this menu item")
		fileMenu.AppendSeparator()
		# When using a stock ID we don't need to specify the menu item's
		# label
		exitItem = fileMenu.Append(wx.ID_EXIT)

		# Now a help menu for the about item
		helpMenu = wx.Menu()
		aboutItem = helpMenu.Append(wx.ID_ABOUT)

		# Make the menu bar and add the two menus to it. The '&' defines
		# that the next letter is the "mnemonic" for the menu item. On the
		# platforms that support it those letters are underlined and can be
		# triggered from the keyboard.
		menuBar = wx.MenuBar()
		menuBar.Append(fileMenu, "&File")
		menuBar.Append(helpMenu, "&Help")

		# Give the menu bar to the frame
		self.SetMenuBar(menuBar)

		# Finally, associate a handler function with the EVT_MENU event for
		# each of the menu items. That means that when that menu item is
		# activated then the associated handler function will be called.
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
	# When this module is run (not imported) then create the app, the
	# frame, show it, and start the event loop.
	app = wx.App()
	frm = HelloFrame(None, title='Hello World 2')
	frm.Show()
	app.MainLoop()
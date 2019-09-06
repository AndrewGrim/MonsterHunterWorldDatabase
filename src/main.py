import wx
import wx.grid
import sqlite3

"""scale all images to the same resolution"""

class HelloFrame(wx.Frame):

	def __init__(self, *args, **kw):
		super(HelloFrame, self).__init__(*args, **kw)

		icon = wx.Icon("images/OfflineDatabase.ico")
		self.SetIcon(icon)
		self.SetSize(1200, 1000)
		self.SetTitle("Database")

		# main window notebook
		mainWindow = wx.Panel(self)
		mainFrame = wx.BoxSizer(wx.HORIZONTAL)
		mainNotebook = wx.Notebook(mainWindow)
		self.monstersFrame = wx.Panel(mainNotebook)
		weaponsFrame = wx.Panel(mainNotebook)
		mainNotebook.AddPage(self.monstersFrame, "Monsters")
		mainNotebook.AddPage(weaponsFrame, "Weapons")
		mainFrame.Add(mainNotebook, 1, wx.EXPAND)
		
		# monsters tab
		self.outerFrame = wx.BoxSizer(wx.HORIZONTAL)

		# left
		tableView = wx.BoxSizer(wx.HORIZONTAL)

		self.table = wx.grid.Grid(self.monstersFrame)
		self.table.CreateGrid(56, 5)
		self.table.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.onSingleSelect)
		self.table.Bind(wx.EVT_SIZE, self.onSize)

		self.outerFrame.Add(tableView, 1, wx.EXPAND)
		tableView.Add(self.table, 1, wx.EXPAND)

		# right
		self.detailedView = wx.BoxSizer(wx.VERTICAL)

		self.img = wx.Bitmap("images/monsters/256/Nergigante.png", wx.BITMAP_TYPE_ANY)
		self.imageLabel = wx.StaticBitmap(self.monstersFrame, bitmap=self.img)

		self.notebook = wx.Notebook(self.monstersFrame)
		self.frame = wx.Panel(self.notebook)
		self.frame2 = wx.Panel(self.notebook)
		self.notebook.AddPage(self.frame, "Overview")
		self.notebook.AddPage(self.frame2, "Damage")

		self.outerFrame.Add(self.detailedView, 1, wx.EXPAND)
		self.detailedView.Add(self.imageLabel, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL | wx.ADJUST_MINSIZE, 10)
		self.detailedView.Add(self.notebook, 1, wx.EXPAND)

		mainWindow.SetSizer(mainFrame)
		self.monstersFrame.SetSizer(self.outerFrame)
		
		self.makeMenuBar()
		self.CreateStatusBar()
		self.SetStatusText("Welcome to wxPython!")
		self.loadData()
		self.SetSize(1201, 980)
		width, height = wx.DisplaySize()
		self.SetPosition(wx.Point(width / 1.4 - self.GetSize().width, height / 1.5 - self.GetSize().height / 1.3))


	def onSize(self, event):
		width, height = self.GetSize()
		numOfColumns = 5
		halfOfWindow = 2
		# all columns equal width
		for col in range(numOfColumns):
			self.table.SetColSize(col, ((width / halfOfWindow) / numOfColumns) - 11) 
		
	
	def loadData(self):
		# possibly add icon to the first col since the id and row# are the same
		conn = sqlite3.connect("../MonsterHunterWorld/MonsterHunter.db")
		data = conn.execute("SELECT * FROM monsters")
		i = 0

		for row in data:
			self.table.SetCellValue(i, 0, str(row[0]))
			self.table.SetCellValue(i, 1, row[1])
			self.table.SetCellValue(i, 2, row[2])
			self.table.SetCellValue(i, 3, row[3])
			self.table.SetCellValue(i, 4, row[4])
			i += 1

		self.table.SetRowLabelSize(30)
		self.table.SetColLabelSize(30)
		self.table.SetColLabelValue(0, "ID")
		self.table.SetColLabelValue(1, "Name")
		self.table.SetColLabelValue(2, "Species")
		self.table.SetColLabelValue(3, "Generation")
		self.table.SetColLabelValue(4, "Size")


	def onSingleSelect(self, event):
		if str(self.table.GetCellValue(event.GetRow(), 1)) != "":
			self.img.LoadFile("images/monsters/256/" + str(self.table.GetCellValue(event.GetRow(), 1)) + ".png")
		else:
			self.img.LoadFile("images/monsters/256/Unknown.png")
		self.imageLabel.SetBitmap(self.img)


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
	app = wx.App()
	frm = HelloFrame(None, title='Hello World 2')
	frm.Show()
	app.MainLoop()
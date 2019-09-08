import wx
import wx.grid
import wx.lib.mixins.gridlabelrenderer as glr
import sqlite3


class Application(wx.Frame):

	def __init__(self, *args, **kw):
		super(Application, self).__init__(*args, **kw)

		icon = wx.Icon("images/OfflineDatabase.ico")
		self.SetIcon(icon)
		self.SetSize(1200, 1000)
		self.SetTitle("Database")
		self.init = True

		self.initMainNotebook()
		self.initMonstersTab()
		self.weaponsFrame = wx.Panel(self.mainNotebook) # TODO move to weapons init
		self.mainNotebook.AddPage(self.weaponsFrame, "Weapons") # TODO move to weapons init!
		self.makeMenuBar()
		self.CreateStatusBar()

		self.SetStatusText("Welcome to wxPython!")
		self.loadData()
		self.initDamage()
		self.init = False

		# to trigger onSize event so the table looks as it should
		self.SetSize(1201, 980)
		width, height = wx.DisplaySize()
		# roughly center
		self.SetPosition(wx.Point(width / 1.4 - self.GetSize().width, height / 1.5 - self.GetSize().height / 1.3))

		# testing: damage tab
		self.monsterDetailsNotebook.SetSelection(1)


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


	def initMonstersTab(self):
		# the outermost panel for the monsters tab
		self.monstersPanel = wx.Panel(self.mainNotebook)
		# add page to notebook
		self.mainNotebook.AddPage(self.monstersPanel, "Monsters")
		# main sizer for the monsters tab
		self.monstersSizer = wx.BoxSizer(wx.HORIZONTAL)

		# left side
		# sizer containing the monsters table
		self.monstersTableSizer = wx.BoxSizer(wx.HORIZONTAL)
		# create monsters table and add bindings on selection and on size change of the main window
		self.monstersTable = wx.grid.Grid(self.monstersPanel)
		self.monstersTable.CreateGrid(56, 5) # TODO make the grid based of the monsters data
		# for loading monster's data in detailed view
		self.monstersTable.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.onSingleSelect)
		# for scaling the columns
		self.monstersTable.Bind(wx.EVT_SIZE, self.onSize)
		# add left side sizer to the main sizer of the monsters tab
		self.monstersSizer.Add(self.monstersTableSizer, 1, wx.EXPAND)
		# add table to sizer
		self.monstersTableSizer.Add(self.monstersTable, 1, wx.EXPAND)

		# right side
		# sizer containing the monsters details
		self.monstersDetailedSizer = wx.BoxSizer(wx.VERTICAL)
		# create bitmap from image and load bitmap into a label
		self.img = wx.Bitmap("images/monsters/256/Nergigante.png", wx.BITMAP_TYPE_ANY)
		self.imageLabel = wx.StaticBitmap(self.monstersPanel, bitmap=self.img)
		# detailed view notebook
		self.monsterDetailsNotebook = wx.Notebook(self.monstersPanel)
		self.overviewPanel = wx.Panel(self.monsterDetailsNotebook)
		self.damagePanel = wx.Panel(self.monsterDetailsNotebook)
		self.monsterDetailsNotebook.AddPage(self.overviewPanel, "Overview")
		# main sizer for the overview notebook tab
		self.monsterDamageSizer = wx.BoxSizer(wx.HORIZONTAL)
		#
		self.monsterDetailsNotebook.AddPage(self.damagePanel, "Damage")
		# add the right side detailed view to the main size of the monsters notebook tab
		self.monstersSizer.Add(self.monstersDetailedSizer, 1, wx.EXPAND)
		# add widgets within to their parent sizer
		self.monstersDetailedSizer.Add(self.imageLabel, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL | wx.ADJUST_MINSIZE, 10)
		self.monstersDetailedSizer.Add(self.monsterDetailsNotebook, 1, wx.EXPAND)

		# set sizer for the monsters notebook tab
		self.monstersPanel.SetSizer(self.monstersSizer)

	
	def initDamage(self):
		self.damageTable = HeaderBitmapGrid(self.damagePanel) #wx.grid.Grid(self.damagePanel)
		self.damageTable.CreateGrid(28, 5)
		self.monsterDamageSizer.Add(self.damageTable, 1, wx.EXPAND)
		self.damagePanel.SetSizer(self.monsterDamageSizer)

		self.damageTable.SetCornerLabelRenderer(HeaderBitmapCornerLabelRenderer())
		self.damageTable.SetRowLabelSize(30)
		self.damageTable.SetColLabelSize(30)
		self.damageTable.SetColLabelValue(0, "Part")
		self.damageTable.SetColLabelValue(1, "Cut")
		self.damageTable.SetColLabelValue(2, "Impact")
		self.damageTable.SetColLabelValue(3, "Shot")
		self.damageTable.SetColLabelValue(4, "KO")
		self.loadDamage(46)

		

	def loadDamage(self, monsterId):
		conn = sqlite3.connect("../MonsterHunterWorld/mhw.db")
		data = conn.execute("SELECT cut, impact, shot, ko, id FROM monster_hitzone WHERE monster_id = ?", (monsterId, ))
		bodyPartId = []

		for row in data:
			bodyPartId.append(row[4])

		data = conn.execute("SELECT cut, impact, shot, ko, id FROM monster_hitzone WHERE monster_id = ?", (monsterId, ))

		bodyPartName = []
		for id in bodyPartId:
			data2 = conn.execute("SELECT name FROM monster_hitzone_text WHERE id = ?", (id, ))
			name = data2.fetchone()
			bodyPartName.append(name[0])

		i = 0
		for row in data:
			self.damageTable.SetCellValue(i, 0, str(bodyPartName[i]))
			self.damageTable.SetCellValue(i, 1, str(row[0]))
			self.damageTable.SetCellValue(i, 2, str(row[1]))
			self.damageTable.SetCellValue(i, 3, str(row[2]))
			self.damageTable.SetCellValue(i, 4, str(row[3]))
			i += 1

		#self.damageTable.SetRowLabelSize(1)


	def onSize(self, event):
		width, height = self.GetSize()
		numOfColumns = 5
		halfOfWindow = 2
		# all columns equal width
		for col in range(numOfColumns):
			self.monstersTable.SetColSize(col, ((width / halfOfWindow) / numOfColumns) - 11)
			if self.init == False:
				self.damageTable.SetColSize(col, ((width / halfOfWindow) / numOfColumns) - 11)
				self.damageTable.SetColSize(0, ((width / halfOfWindow) / numOfColumns) + 10)
		
	
	def loadData(self):
		conn = sqlite3.connect("../MonsterHunterWorld/MonsterHunter.db")
		data = conn.execute("SELECT * FROM monsters")
		i = 0

		for row in data:
			self.monstersTable.SetCellValue(i, 0, str(row[0]))
			self.monstersTable.SetCellValue(i, 1, row[1])
			self.monstersTable.SetCellValue(i, 2, row[2])
			self.monstersTable.SetCellValue(i, 3, row[3])
			self.monstersTable.SetCellValue(i, 4, row[4])
			i += 1

		self.monstersTable.SetRowLabelSize(30)
		self.monstersTable.SetColLabelSize(30)
		self.monstersTable.SetColLabelValue(0, "ID")
		self.monstersTable.SetColLabelValue(1, "Name")
		self.monstersTable.SetColLabelValue(2, "Species")
		self.monstersTable.SetColLabelValue(3, "Generation")
		self.monstersTable.SetColLabelValue(4, "Size")



	def onSingleSelect(self, event):
		if str(self.monstersTable.GetCellValue(event.GetRow(), 1)) != "":
			self.img.LoadFile("images/monsters/256/" + str(self.monstersTable.GetCellValue(event.GetRow(), 1)) + ".png")
		else:
			self.img.LoadFile("images/monsters/256/Unknown.png")
		self.imageLabel.SetBitmap(self.img)
		self.damageTable.ClearGrid()
		self.loadDamage(self.monstersTable.GetCellValue(event.GetRow(), 0))


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

					
class HeaderBitmapGrid(wx.grid.Grid, glr.GridWithLabelRenderersMixin):
	def __init__(self, *args, **kw):
		wx.grid.Grid.__init__(self, *args, **kw)
		glr.GridWithLabelRenderersMixin.__init__(self)


class HeaderBitmapRowLabelRenderer(glr.GridLabelRenderer):
	def __init__(self, bgcolor):
		self._bgcolor = bgcolor

	def Draw(self, grid, dc, rect, row):
		dc.SetBrush(wx.Brush(self._bgcolor))
		dc.SetPen(wx.TRANSPARENT_PEN)
		dc.DrawRectangle(rect)
		hAlign, vAlign = wx.grid.GetRowLabelAlignment()
		text = wx.grid.GetRowLabelValue(row)
		self.DrawBorder(wx.grid, dc, rect)
		self.DrawText(wx.grid, dc, rect, text, hAlign, vAlign)


class HeaderBitmapColLabelRenderer(glr.GridLabelRenderer):
	def __init__(self, bgcolor):
		self._bgcolor = bgcolor

	def Draw(self, grid, dc, rect, col):
		dc.SetBrush(wx.Brush(self._bgcolor))
		dc.SetPen(wx.TRANSPARENT_PEN)
		dc.DrawRectangle(rect)
		hAlign, vAlign = wx.grid.GetColLabelAlignment()
		text = wx.grid.GetColLabelValue(col)
		self.DrawBorder(wx.grid, dc, rect)
		self.DrawText(wx.grid, dc, rect, text, hAlign, vAlign)


class HeaderBitmapCornerLabelRenderer(glr.GridLabelRenderer):
	def __init__(self):
		import images
		self._bmp = wx.Bitmap("Nergigante32.png", wx.BITMAP_TYPE_ANY)

	def Draw(self, grid, dc, rect, rc):
		x = rect.left + (rect.width - self._bmp.GetWidth()) / 2
		y = rect.top + (rect.height - self._bmp.GetHeight()) / 2
		dc.DrawBitmap(self._bmp, x, y, True)



"""class TestPanel(wx.Panel):
	def __init__(self, parent, log):
		self.log = log
		wx.Panel.__init__(self, parent, -1)

		ROWS = 27
		COLS = 15

		g = MyGrid(self, size=(100,100))
		g.CreateGrid(ROWS, COLS)

		g.SetCornerLabelRenderer(MyCornerLabelRenderer())

		for row in range(0, ROWS, 3):
			g.SetRowLabelRenderer(row+0, MyRowLabelRenderer('#ffe0e0'))
			g.SetRowLabelRenderer(row+1, MyRowLabelRenderer('#e0ffe0'))
			g.SetRowLabelRenderer(row+2, MyRowLabelRenderer('#e0e0ff'))

		for col in range(0, COLS, 3):
			g.SetColLabelRenderer(col+0, MyColLabelRenderer('#e0ffe0'))
			g.SetColLabelRenderer(col+1, MyColLabelRenderer('#e0e0ff'))
			g.SetColLabelRenderer(col+2, MyColLabelRenderer('#ffe0e0'))

		self.Sizer = wx.BoxSizer()
		self.Sizer.Add(g, 1, wx.EXPAND)"""


if __name__ == '__main__':
	app = wx.App()
	frm = Application(None, title="Database")
	frm.Show()
	app.MainLoop()
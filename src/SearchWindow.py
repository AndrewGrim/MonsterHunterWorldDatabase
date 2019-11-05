import wx
import sqlite3

import CustomGridRenderer as cgr

class SearchWindow:

	def __init__(self, root):
		self.root = root
		self.init = True

		self.win = wx.Frame(root, title="Debug", style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
		self.win.SetIcon(wx.Icon("images/Nergigante.png"))
		self.win.SetSize(700, 700)
		self.win.Center()
		self.win.Bind(wx.EVT_CLOSE, self.onClose)

		panel = wx.Panel(self.win)
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.search = wx.TextCtrl(panel)
		self.search.SetHint("  search by name")
		self.search.Bind(wx.EVT_TEXT, self.onSearchTextEnter)
		sizer.Add(self.search, 1, wx.EXPAND)

		self.results = cgr.HeaderBitmapGrid(panel)
		self.results.EnableEditing(False)
		self.results.EnableDragRowSize(False)
		self.results.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.onResultSelection)
		self.results.CreateGrid(1, 2)
		self.results.SetDefaultRowSize(27, resizeExistingRows=True)
		self.results.HideRowLabels()
		self.results.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
		self.results.SetColLabelValue(0, "Name")
		self.results.SetColSize(0, 660)
		self.results.SetColSize(1, 0)
		sizer.Add(self.results, 120, wx.EXPAND)

		panel.SetSizer(sizer)


		self.makeMenuBar()

		self.win.Show()

		self.init = False


	def onSearchTextEnter(self, event):
		searchText = self.search.GetValue()

		try:
			self.results.DeleteRows(0, self.results.GetNumberRows())
		except:
			pass

		sql = f"""
			SELECT w.id, w.weapon_type, w.rarity, wt.name
			FROM weapon w
				JOIN weapon_text wt USING (id)
			WHERE wt.lang_id = 'en'
				AND wt.name LIKE '%{searchText}%'
			ORDER BY w.id ASC
		"""

		conn = sqlite3.connect("mhw.db")
		data = conn.execute(sql, )
		data = data.fetchall()
		
		padding = " " * 8
		for row in data:
			self.results.AppendRows()
			r = self.results.GetNumberRows() - 1
			img = wx.Bitmap(f"images/weapons/{row[1]}/rarity-24/{row[2]}.png")
			self.results.SetCellRenderer(r, 0, cgr.ImageTextCellRenderer(img, f"{padding}{row[3]}", hAlign=wx.ALIGN_LEFT, imageOffset=320))
			self.results.SetCellValue(r, 1, f"{row[0]}")

	
	def onResultSelection(self, event):
		if not self.init:
			self.currentlySelectedID = self.results.GetCellValue(event.GetRow(), 1)
			if self.currentlySelectedID != "":
				print(self.currentlySelectedID)


	def makeMenuBar(self):
		fileMenu = wx.Menu()
		closeItem = fileMenu.Append(-1, "&Close\tCtrl-F", "Closes the debug window.")
		
		menuBar = wx.MenuBar()
		menuBar.Append(fileMenu, "&File")

		self.win.SetMenuBar(menuBar)

		self.win.Bind(wx.EVT_MENU, self.onClose, closeItem)


	def onClose(self, event):
		self.win.Destroy()
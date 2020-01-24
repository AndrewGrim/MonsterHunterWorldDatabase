import wx
import wx.grid
import wx.lib.gizmos as gizmos
import CustomGridRenderer as cgr
import wx.propgrid as wxpg
import wx.lib.scrolledpanel as scrolled
import sqlite3
import time
import os
import typing
from typing import List
from typing import Union
from typing import Tuple
from typing import Dict
from typing import NewType

import Utilities as util
from Debug import debug
import ToolsTab as t
import Links as link
import ItemsTab as i

wxTreeListItem = NewType('wxTreeListItem', None)

class ToolsTab:

	def __init__(self, root, mainNotebook, link):
		self.root = root
		self.mainNotebook = mainNotebook
		self.link = link
		self.init = True

		self.currentlySelectedToolID = 0
		self.currentToolTree = "optional"
		self.testIcon = wx.Bitmap("images/unknown.png", wx.BITMAP_TYPE_ANY)

		self.initToolsTab()


	def initToolsTab(self):
		self.toolPanel = wx.Panel(self.mainNotebook)
		self.mainNotebook.AddPage(self.toolPanel, "Tools")
		self.toolSizer = wx.BoxSizer(wx.HORIZONTAL)

		self.toolTreeSizer = wx.BoxSizer(wx.VERTICAL) 
		
		self.toolDetailedSizer = wx.BoxSizer(wx.VERTICAL)
		toolImage = wx.Bitmap("images/hunter-tools-180/Ghillie Mantle.jpg", wx.BITMAP_TYPE_ANY)
		self.toolImageLabel = wx.StaticBitmap(self.toolPanel, bitmap=toolImage, size=(180, 180))
		self.toolImageLabel.SetBackgroundColour((0, 0, 0))

		self.toolDetailsNotebook = wx.Notebook(self.toolPanel)
		self.toolDetailPanel = wx.ScrolledWindow(self.toolDetailsNotebook)
		
		self.toolDetailSizer = wx.BoxSizer(wx.VERTICAL)
		self.toolDetailsNotebook.AddPage(self.toolDetailPanel, "Detail")
		self.toolDetailPanel.SetSizer(self.toolDetailSizer)

		self.toolDetailedImagesSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.toolDetailedImagesSizer.Add(self.toolImageLabel, 1, wx.ALIGN_CENTER)
		
		self.toolDetailedSizer.Add(self.toolDetailedImagesSizer, 1, wx.EXPAND)
		self.toolDetailedSizer.Add(self.toolDetailsNotebook, 3, wx.EXPAND)

		self.toolSizer.Add(self.toolTreeSizer, 0, wx.EXPAND)
		self.toolSizer.Add(self.toolDetailedSizer, 1, wx.EXPAND)

		self.toolPanel.SetSizer(self.toolSizer)

		self.initSearch()
		self.initToolTree()
		self.initToolDetail()

		self.toolDetailList.Bind(wx.EVT_SIZE, self.onSize)

		self.toolDetailPanel.SetScrollRate(20, 20)

	
	def initSearch(self):
		self.search = wx.TextCtrl(self.toolPanel, style=wx.TE_PROCESS_ENTER)
		self.search.SetHint("search by name")
		self.search.Bind(wx.EVT_TEXT_ENTER, self.onSearchTextEnter)
		self.toolTreeSizer.Add(self.search, 0, wx.EXPAND)


	def onSearchTextEnter(self, event):
		self.loadToolTree()


	def initToolTree(self):
		self.toolTree = cgr.HeaderBitmapGrid(self.toolPanel)
		self.toolTree.EnableEditing(False)
		self.toolTree.EnableDragRowSize(False)
		self.toolTree.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.onToolSelection)
		self.toolTreeSizer.Add(self.toolTree, 1, wx.EXPAND)

		toolTreeColumns = {
			"Name": [640, None],
			"id": [0,  None],
		}

		self.toolTree.CreateGrid(1, len(toolTreeColumns))
		self.toolTree.SetDefaultRowSize(27, resizeExistingRows=True)
		self.toolTree.SetRowLabelSize(1)
		self.toolTree.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)

		for col, (k, v) in enumerate(toolTreeColumns.items()):
			if v[1] == None:
				self.toolTree.SetColLabelValue(col, k)
			else:
				self.toolTree.SetColLabelRenderer(col, cgr.HeaderBitmapColLabelRenderer(v[1], ""))
			self.toolTree.SetColSize(col, v[0])

		self.loadToolTree()


	def loadToolTree(self):
		self.init = True
		try:
			self.toolTree.DeleteRows(0, self.toolTree.GetNumberRows())
		except:
			pass

		searchText = self.search.GetValue().replace("'", "''")

		if len(searchText) == 0 or searchText == " ":
			sql = """
				SELECT *
				FROM tool t
				ORDER BY order_id
			"""
		else:
			sql = f"""
				SELECT *
				FROM tool t
				WHERE t.name LIKE '%{searchText}%'
				ORDER BY order_id
			"""

		conn = sqlite3.connect("mhw.db")
		data = conn.execute(sql)
		data = data.fetchall()

		tools = []
		for row in data:
			tools.append(t.Tool(row))

		padding = " " * 8
		for row, tool in enumerate(tools):
			self.toolTree.AppendRows() 
			img = wx.Bitmap(f"images/hunter-tools-24/{tool.name}.png")
			self.toolTree.SetCellRenderer(row, 0, cgr.ImageTextCellRenderer(
			img, f"{padding}{tool.name}", imageOffset=310, hAlign=wx.ALIGN_LEFT))
			self.toolTree.SetCellValue(row, 1, str(tool.id))

		self.init = False


	def initToolDetail(self):
		self.toolNameLabel = wx.StaticText(self.toolDetailPanel, label="Name:")
		self.toolDescriptionLabel = wx.StaticText(self.toolDetailPanel, label="Description")
		self.toolUnlockConditionLabel = wx.StaticText(self.toolDetailPanel, label="UnlockCondition:")
		self.toolUnlockConditionDetailLabel = wx.StaticText(self.toolDetailPanel, label="Description")
		self.toolDetailSizer.Add(self.toolNameLabel, 0.1, wx.EXPAND)
		self.toolDetailSizer.Add(self.toolDescriptionLabel, 0.5, wx.EXPAND)
		self.toolDetailSizer.Add(self.toolUnlockConditionLabel, 0.1, wx.EXPAND)
		self.toolDetailSizer.Add(self.toolUnlockConditionDetailLabel, 0.5, wx.EXPAND)

		self.toolDetailList = cgr.HeaderBitmapGrid(self.toolDetailPanel)
		self.toolDetailList.Bind(wx.EVT_SIZE, self.onSize)
		self.toolDetailList.EnableEditing(False)
		self.toolDetailList.EnableDragRowSize(False)
		self.toolDetailList.CreateGrid(3, 2)
		self.toolDetailList.SetDefaultRowSize(24, resizeExistingRows=True)
		self.toolDetailList.SetColSize(0, 480)
		self.toolDetailList.SetColSize(1, 240 - 20)
		self.toolDetailList.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
		self.toolDetailList.SetColLabelSize(2)
		self.toolDetailList.SetRowLabelSize(1)
		self.toolDetailSizer.Add(self.toolDetailList, 0, wx.EXPAND|wx.TOP, 5)

		self.initRequiredToolMaterials()
		self.loadToolDetail()


	def initRequiredToolMaterials(self):
		self.toolMaterialList = wx.ListCtrl(self.toolDetailPanel, style=wx.LC_REPORT
																		| wx.LC_VRULES
																		| wx.LC_HRULES
																		)
		self.toolMaterialList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onListDoubleClick)
		self.il = wx.ImageList(24, 24)
		self.il.Add(self.testIcon)
		self.toolMaterialList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
		self.toolDetailSizer.Add(self.toolMaterialList, 1, wx.EXPAND|wx.TOP, 5)


	def loadToolDetail(self):
		self.root.Freeze()

		self.toolDetailList.DeleteRows(0, self.toolDetailList.GetNumberRows())
		self.toolDetailList.AppendRows(3)
		
		sql = """
			SELECT *
			FROM tool t
			WHERE t.id = :toolID
		"""

		conn = sqlite3.connect("mhw.db")
		data = conn.execute(sql, (self.currentlySelectedToolID,))
		data = data.fetchone()

		tool = t.Tool(data)

		toolDetail = {
			"Effect Duration": f"{tool.duration}s",
			"Recharge Time": f"{tool.rechargeTime}s",
			"Associated Quest": tool.associatedQuest
		}

		self.toolNameLabel.SetFont(self.toolNameLabel.GetFont().Bold())
		self.toolUnlockConditionLabel.SetFont(self.toolUnlockConditionLabel.GetFont().Bold())

		self.toolImageLabel.SetBitmap(wx.Bitmap(f"images/hunter-tools-180/{tool.name}.jpg", wx.BITMAP_TYPE_ANY))
		self.toolNameLabel.SetLabel(f"{tool.name}:")
		self.toolDescriptionLabel.SetLabel(f"{tool.description}\n")
		self.toolDescriptionLabel.Wrap(600)
		self.toolUnlockConditionLabel.SetLabel("Unlock Condition:")
		self.toolUnlockConditionDetailLabel.SetLabel(f"{tool.unlockCondition}\n")
		self.toolUnlockConditionDetailLabel.Wrap(600)

		for i, (k, v) in enumerate(toolDetail.items()):
			self.toolDetailList.SetCellValue(i, 0, k)
			self.toolDetailList.SetCellValue(i, 1, v)

		self.loadRequiredToolMaterials()
		width, height = self.toolPanel.GetSize()
		self.toolPanel.SetSize(width + 1, height + 1)
		self.toolPanel.SetSize(width, height)
		self.root.Thaw()


	def loadRequiredToolMaterials(self):
		self.il.RemoveAll()
		self.toolMaterialList.ClearAll()

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = "Req. Materials"
		self.toolMaterialList.InsertColumn(0, info)
		self.toolMaterialList.SetColumnWidth(0, 480)

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_CENTER
		info.Text = ""
		self.toolMaterialList.InsertColumn(1, info)
		self.toolMaterialList.SetColumnWidth(1, 240 - 20)

		self.toolMaterialList.InsertColumn(2, info)
		self.toolMaterialList.SetColumnWidth(2, 0)

		sql = """
			SELECT i.id, it.name, i.category, tr.quantity, i.icon_name, i.icon_color
			FROM tool_recipe tr
				JOIN item i
					ON tr.item_id = i.id
				JOIN item_text it
					ON tr.item_id = it.id
			WHERE it.lang_id = 'en'
				AND tr.id = :kinId
			ORDER BY i.id
		"""

		conn = sqlite3.connect("mhw.db")
		data = conn.execute(sql, (self.currentlySelectedToolID,))
		data = data.fetchall()

		materials = []
		for row in data:
			materials.append(t.ToolMaterial(row))

		for mat in materials:
			if os.path.exists(f"images/items-24/{mat.iconName}{mat.iconColor}.png"):
				img = self.il.Add(wx.Bitmap(f"images/items-24/{mat.iconName}{mat.iconColor}.png"))
			else:
				img = self.il.Add(wx.Bitmap(f"images/unknown.png"))
			index = self.toolMaterialList.InsertItem(self.toolMaterialList.GetItemCount(), mat.name, img)
			self.toolMaterialList.SetItem(index, 1, f"{mat.quantity}")
			self.toolMaterialList.SetItem(index, 2, f"item,{mat.id},{mat.category}")

	def onToolSelection(self, event):
		if not self.init:
			self.currentlySelectedToolID = self.toolTree.GetCellValue(event.GetRow(), 1)
			if self.currentlySelectedToolID != "":
				self.loadToolDetail()


	def onToolTypeSelection(self, event):
		self.currentToolTree = event.GetEventObject().GetName()
		self.loadToolTree()


	def onListDoubleClick(self, event):
		materialInfo = event.GetEventObject().GetItemText(event.GetEventObject().GetFirstSelected(), 2).split(",")
		self.link.event = True
		self.link.eventType = materialInfo[0]
		materialInfo.remove(materialInfo[0])
		if len(materialInfo) == 1:
			self.link.info = link.GenericSingleLink(materialInfo[0])
		elif len(materialInfo) == 2:
			self.link.info = link.GenericDoubleLink(materialInfo)
		else:
			debug(materialInfo, "materialInfo", "materialInfo length is other than accounted for!")
		self.root.followLink()
		self.link.reset()


	def onSize(self, event):
		try:
			self.toolDetailList.SetColSize(0, self.toolDetailPanel.GetSize()[0] * 0.66)
			self.toolDetailList.SetColSize(1, self.toolDetailPanel.GetSize()[0] * 0.34 - 20)
			self.toolMaterialList.SetColumnWidth(0, self.toolDetailPanel.GetSize()[0] * 0.66)
			self.toolMaterialList.SetColumnWidth(1, self.toolDetailPanel.GetSize()[0] * 0.34 - 20)
		except:
			pass


	def onScroll(self, event):
		if event.GetWheelRotation() > 0:
			if self.toolDetailPanel.GetViewStart()[1] < 3:
				self.toolDetailPanel.Scroll(0, self.toolDetailPanel.GetViewStart()[1] + 1 * -1)
			else:
				self.toolDetailPanel.Scroll(0, self.toolDetailPanel.GetViewStart()[1] + 3 * -1)
		else:
			if self.toolDetailPanel.GetViewStart()[1] < 3:
				self.toolDetailPanel.Scroll(0, self.toolDetailPanel.GetViewStart()[1] + 1)
			else:
				self.toolDetailPanel.Scroll(0, self.toolDetailPanel.GetViewStart()[1] + 3)

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
import QuestsTab as q

wxTreeListItem = NewType('wxTreeListItem', None)

class QuestsTab:

	def __init__(self, root, mainNotebook, link):
		self.root = root
		self.mainNotebook = mainNotebook
		self.init = True

		self.currentlySelectedQuestID = 101
		self.testIcon = wx.Bitmap("images/unknown.png", wx.BITMAP_TYPE_ANY)

		self.initQuestsTab()


	def initQuestsTab(self):
		self.questPanel = wx.Panel(self.mainNotebook)
		self.mainNotebook.AddPage(self.questPanel, "Quests")
		self.questSizer = wx.BoxSizer(wx.HORIZONTAL)

		self.questTreeSizer = wx.BoxSizer(wx.VERTICAL) 
		
		self.questDetailedSizer = wx.BoxSizer(wx.VERTICAL)
		questImage = wx.Bitmap("images/kinsects/Culldrone I.jpg", wx.BITMAP_TYPE_ANY)
		self.questImageLabel = wx.StaticBitmap(self.questPanel, bitmap=questImage, size=(160, 160))
		#self.questImageLabel.SetBackgroundColour((0, 0, 0))

		self.questDetailsNotebook = wx.Notebook(self.questPanel)
		self.questDetailPanel = wx.ScrolledWindow(self.questDetailsNotebook)
		
		self.questDetailSizer = wx.BoxSizer(wx.VERTICAL)
		self.questDetailsNotebook.AddPage(self.questDetailPanel, "Detail")
		self.questDetailPanel.SetSizer(self.questDetailSizer)

		self.questDetailedImagesSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.questDetailedImagesSizer.Add(self.questImageLabel, 1, wx.ALIGN_CENTER)
		
		self.questDetailedSizer.Add(self.questDetailedImagesSizer, 1, wx.EXPAND)
		self.questDetailedSizer.Add(self.questDetailsNotebook, 3, wx.EXPAND)

		self.questSizer.Add(self.questTreeSizer, 0, wx.EXPAND)
		self.questSizer.Add(self.questDetailedSizer, 1, wx.EXPAND)

		self.questPanel.SetSizer(self.questSizer)

		self.initQuestButtons()
		self.initSearch()
		self.initQuestTree()
		self.initQuestDetail()

		self.questDetailList.Bind(wx.EVT_SIZE, self.onSize)

		self.questDetailPanel.SetScrollRate(20, 20)


	def initQuestButtons(self):
		quests = ["assigned", "optional", "event", "special", "arena"]

		self.questButtonsSizer = wx.BoxSizer(wx.HORIZONTAL)
		for i, item in enumerate(quests):
			button = wx.Button(self.questPanel, label=item.capitalize(), name=item)
			button.SetBitmap(wx.Bitmap(f"images/unknown.png"))
			self.questButtonsSizer.Add(button)
			button.Bind(wx.EVT_BUTTON, self.onQuestTypeSelection)

		self.questTreeSizer.Add(self.questButtonsSizer)


	def initSearch(self):
		self.search = wx.TextCtrl(self.questPanel)
		self.search.SetHint("  search by name")
		self.search.Bind(wx.EVT_TEXT, self.onSearchTextEnter)
		self.questButtonsSizer.Add(120, 0, 0)
		self.questButtonsSizer.Add(self.search, 0, wx.ALIGN_CENTER_VERTICAL)


	def onSearchTextEnter(self, event):
		self.loadQuestTree()


	def initQuestTree(self):
		self.questTree = cgr.HeaderBitmapGrid(self.questPanel)
		self.questTree.EnableEditing(False)
		self.questTree.EnableDragRowSize(False)
		self.questTree.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.onQuestSelection)
		self.questTreeSizer.Add(self.questTree, 1, wx.EXPAND)

		questTreeColumns = {
			"Name": [500, None], # joined by quest type icon
			"Location": [100, None],
			"Zenny": [60, wx.Bitmap("images/zenny.png")],
			"id": [0,  None],
		}

		self.questTree.CreateGrid(1, len(questTreeColumns))
		self.questTree.SetDefaultRowSize(27, resizeExistingRows=True)
		self.questTree.HideRowLabels()
		self.questTree.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)

		for col, (k, v) in enumerate(questTreeColumns.items()):
			if v[1] == None:
				self.questTree.SetColLabelValue(col, k)
			else:
				self.questTree.SetColLabelRenderer(col, cgr.HeaderBitmapColLabelRenderer(v[1], ""))
			self.questTree.SetColSize(col, v[0])

		self.loadQuestTree()


	def loadQuestTree(self):
		self.init = True
		try:
			self.questTree.DeleteRows(0, self.questTree.GetNumberRows())
		except:
			pass
		self.init = False


	def initQuestDetail(self):
		self.questDetailList = cgr.HeaderBitmapGrid(self.questDetailPanel)
		self.questDetailList.Bind(wx.EVT_MOUSEWHEEL, self.onScroll)
		self.questDetailList.EnableEditing(False)
		self.questDetailList.EnableDragRowSize(False)
		self.questDetailSizer.Add(self.questDetailList, 1, wx.EXPAND)

		self.questDetailList.CreateGrid(6, 2)
		self.questDetailList.SetDefaultRowSize(24, resizeExistingRows=True)
		self.questDetailList.SetColSize(0, 302)
		self.questDetailList.SetColSize(1, 155 - 20)
		self.questDetailList.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
		self.questDetailList.SetColLabelSize(0)
		self.questDetailList.SetRowLabelSize(0)

		self.questMonstersList = wx.ListCtrl(self.questDetailPanel, style=wx.LC_REPORT
																			| wx.LC_VRULES
																			| wx.LC_HRULES
																			)
		self.questMonstersList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onListDoubleClick)
		self.il = wx.ImageList(24, 24)
		self.questMonstersList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
		self.questDetailSizer.Add(self.questMonstersList, 1, wx.EXPAND|wx.TOP, 5)

		self.materialsRequiredList = wx.ListCtrl(self.questDetailPanel, style=wx.LC_REPORT
																			| wx.LC_VRULES
																			| wx.LC_HRULES
																			)
		self.materialsRequiredList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onListDoubleClick)
		self.materialsRequiredList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
		self.questDetailSizer.Add(self.materialsRequiredList, 1, wx.EXPAND|wx.TOP, 5)

		self.loadQuestDetail()


	def loadQuestDetail(self):
		self.root.Freeze()

		self.questMonstersList.ClearAll()
		self.materialsRequiredList.ClearAll()
		self.il.RemoveAll()

		questDetail = {
			"Name": "Tyrannt Has Fallen",
		}

		for i, (k, v) in enumerate(questDetail.items()):
			self.questDetailList.SetCellValue(i, 0, k)
			self.questDetailList.SetCellValue(i, 1, v)

		self.questDetailList.DeleteRows(0, self.questDetailList.GetNumberRows())
		self.questDetailList.AppendRows(4) # TODO change to length

		self.loadQuestMonsters()
		self.loadQuestMaterials()
		width, height = self.questPanel.GetSize()
		self.questPanel.SetSize(width + 1, height + 1)
		self.questPanel.SetSize(width, height)
		self.root.Thaw()


	def loadQuestMonsters(self):
		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = "Name"
		self.questMonstersList.InsertColumn(0, info)
		self.questMonstersList.SetColumnWidth(0, 380)

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_CENTER
		info.Text = "Quantity"
		self.questMonstersList.InsertColumn(1, info)
		self.questMonstersList.SetColumnWidth(1, 100)

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_CENTER
		info.Text = "Objective"
		self.questMonstersList.InsertColumn(2, info)
		self.questMonstersList.SetColumnWidth(2, 200)

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = ""
		self.questMonstersList.InsertColumn(3, info)
		self.questMonstersList.SetColumnWidth(3, 0)

		sql = """
			SELECT qm.monster_id, mt.name, qm.quantity, qm.is_objective 
			FROM quest q
			JOIN quest_monsters qm
				ON qm.id = q.id
			JOIN monster m
				ON qm.monster_id = m.id
			JOIN monster_text mt
				ON mt.id = m.id
				AND mt.lang_id = 'en'
			WHERE q.id = :questID
		"""

		conn = sqlite3.connect("mhw.db")
		data = conn.execute(sql, (self.currentlySelectedQuestID,))
		data = data.fetchall()

		monsters = []
		for row in data:
			monsters.append(q.QuestMonster(row))

		for mon in monsters:
			img = self.il.Add(wx.Bitmap(f"images/monsters/24/{mon.name}.png"))
			index = self.questMonstersList.InsertItem(self.questMonstersList.GetItemCount(), mon.name, img)
			self.questMonstersList.SetItem(index, 1, f"{mon.quantity}")
			if bool(mon.isObjective):
				if self.root.pref.unicodeSymbols:
					self.questMonstersList.SetItem(index, 2, "✓")
				else:
					self.questMonstersList.SetItem(index, 2, "Yes")
			self.questMonstersList.SetItem(index, 3, f"monster,{mon.id},{mon.name}")


	def loadQuestMaterials(self):
		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = "Req. Materials"
		self.materialsRequiredList.InsertColumn(0, info)
		self.materialsRequiredList.SetColumnWidth(0, 380)

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_CENTER
		info.Text = ""
		self.materialsRequiredList.InsertColumn(1, info)
		self.materialsRequiredList.SetColumnWidth(1, 100)

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_CENTER
		info.Text = "Reward Group"
		self.materialsRequiredList.InsertColumn(2, info)
		self.materialsRequiredList.SetColumnWidth(2, 200)

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_CENTER
		info.Text = ""
		self.materialsRequiredList.InsertColumn(3, info)
		self.materialsRequiredList.SetColumnWidth(3, 0)

		sql = """
			SELECT qr.item_id, it.name, i.category, qr.stack, qr.percentage, qr.reward_group, i.icon_name, i.icon_color
			FROM quest q
			JOIN quest_rewards qr
				ON qr.id = q.id
			JOIN item i
				ON qr.item_id = i.id
			JOIN item_text it
				ON it.id = i.id
				AND it.lang_id = 'en'
			WHERE q.id = :questID
		"""

		conn = sqlite3.connect("mhw.db")
		data = conn.execute(sql, (self.currentlySelectedQuestID,))
		data = data.fetchall()

		items = []
		for row in data:
			items.append(q.QuestReward(row))

		for item in items:
			img = self.il.Add(wx.Bitmap(f"images/items-24/{item.iconName}{item.iconColor}.png"))
			index = self.materialsRequiredList.InsertItem(self.materialsRequiredList.GetItemCount(), item.name, img)
			self.materialsRequiredList.SetItem(index, 1, f"{item.stack} x {item.percentage}%")
			self.materialsRequiredList.SetItem(index, 2, f"{item.rewardGroup}")
			self.materialsRequiredList.SetItem(index, 3, f"item,{item.id},{item.category}")


	def onQuestSelection(self, event):
		pass


	def onQuestTypeSelection(self, event):
		pass


	def onListDoubleClick(self, event):
		pass


	def onSize(self, event):
		try:
			self.questDetailList.SetColSize(0, self.questDetailPanel.GetSize()[0] * 0.66)
			self.questDetailList.SetColSize(1, self.questDetailPanel.GetSize()[0] * 0.34 - 20)
			self.questMonstersList.SetColumnWidth(0, self.questDetailPanel.GetSize()[0] * 0.56)
			self.questMonstersList.SetColumnWidth(1, self.questDetailPanel.GetSize()[0] * 0.17)
			self.questMonstersList.SetColumnWidth(2, self.questDetailPanel.GetSize()[0] * 0.27 - 40)
			self.materialsRequiredList.SetColumnWidth(0, self.questDetailPanel.GetSize()[0] * 0.56)
			self.materialsRequiredList.SetColumnWidth(1, self.questDetailPanel.GetSize()[0] * 0.17)
			self.materialsRequiredList.SetColumnWidth(2, self.questDetailPanel.GetSize()[0] * 0.27 - 40)
		except:
			pass


	def onScroll(self, event):
		if event.GetWheelRotation() > 0:
			if self.questDetailPanel.GetViewStart()[1] < 3:
				self.questDetailPanel.Scroll(0, self.questDetailPanel.GetViewStart()[1] + 1 * -1)
			else:
				self.questDetailPanel.Scroll(0, self.questDetailPanel.GetViewStart()[1] + 3 * -1)
		else:
			if self.questDetailPanel.GetViewStart()[1] < 3:
				self.questDetailPanel.Scroll(0, self.questDetailPanel.GetViewStart()[1] + 1)
			else:
				self.questDetailPanel.Scroll(0, self.questDetailPanel.GetViewStart()[1] + 3)

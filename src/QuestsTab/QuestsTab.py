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
import Links as link

wxTreeListItem = NewType('wxTreeListItem', None)

class QuestsTab:

	def __init__(self, root, mainNotebook, link):
		self.root = root
		self.mainNotebook = mainNotebook
		self.link = link
		self.init = True

		self.currentlySelectedQuestID = 101
		self.currentQuestTree = "optional"
		self.testIcon = wx.Bitmap("images/unknown.png", wx.BITMAP_TYPE_ANY)

		self.rankColors = {
			"lr": "#7cd3de",
			"hr": "#ffae47",
			"mr": "#ffef66",
		}

		self.initQuestsTab()


	def initQuestsTab(self):
		self.questPanel = wx.Panel(self.mainNotebook)
		self.mainNotebook.AddPage(self.questPanel, "Quests")
		self.questSizer = wx.BoxSizer(wx.HORIZONTAL)

		self.questTreeSizer = wx.BoxSizer(wx.VERTICAL) 
		
		self.questDetailedSizer = wx.BoxSizer(wx.VERTICAL)
		questImage = wx.Bitmap("images/hunter-rank-160.png", wx.BITMAP_TYPE_ANY)
		self.questImageLabel = wx.StaticBitmap(self.questPanel, bitmap=questImage, size=(160, 160))

		self.questDetailsNotebook = wx.Notebook(self.questPanel)
		self.questDetailPanel = wx.ScrolledWindow(self.questDetailsNotebook)
		
		self.questDetailSizer = wx.BoxSizer(wx.VERTICAL)
		self.questDetailsNotebook.AddPage(self.questDetailPanel, "Detail")
		self.questDetailPanel.SetSizer(self.questDetailSizer)

		self.questDetailedImagesSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.questDetailedImagesSizer.Add(self.questImageLabel, 1, wx.ALIGN_CENTER)
		
		self.questDetailedSizer.Add(self.questDetailedImagesSizer, 1, wx.EXPAND)
		self.questDetailedSizer.Add(self.questDetailsNotebook, 5, wx.EXPAND)

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
			self.questButtonsSizer.Add(button)
			button.Bind(wx.EVT_BUTTON, self.onQuestTypeSelection)

		self.questTreeSizer.Add(self.questButtonsSizer, 0, wx.EXPAND)


	def initSearch(self):
		self.searchName = wx.TextCtrl(self.questPanel, name="byName", style=wx.TE_PROCESS_ENTER)
		self.searchName.SetHint("search by name")
		self.searchName.Bind(wx.EVT_TEXT_ENTER, self.onSearchTextEnter)

		self.searchMonster = wx.TextCtrl(self.questPanel, name="byMonster", style=wx.TE_PROCESS_ENTER)
		self.searchMonster.SetHint("search by monster")
		self.searchMonster.Bind(wx.EVT_TEXT_ENTER, self.onSearchTextEnter)

		self.currentSearch = self.searchName

		self.questButtonsSizer.Add(self.searchName, 1, wx.EXPAND)
		self.questButtonsSizer.Add(self.searchMonster, 1, wx.EXPAND)


	def onSearchTextEnter(self, event):
		self.currentSearch = event.GetEventObject()
		self.loadQuestTree()


	def initQuestTree(self):
		self.questTree = cgr.HeaderBitmapGrid(self.questPanel)
		self.questTree.EnableEditing(False)
		self.questTree.EnableDragRowSize(False)
		self.questTree.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.onQuestSelection)
		self.questTreeSizer.Add(self.questTree, 1, wx.EXPAND)

		questTreeColumns = {
			"Name": [425, None],
			"Location": [185, None],
			"Zenny": [70, wx.Bitmap("images/zenny.png")],
			"id": [0,  None],
		}

		self.questTree.CreateGrid(1, len(questTreeColumns))
		self.questTree.SetDefaultRowSize(27, resizeExistingRows=True)
		self.questTree.SetRowLabelSize(1)
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

		searchText = self.currentSearch.GetValue().replace("'", "''")

		if len(searchText) == 0 or searchText == " ":
			sql = """
				SELECT q.id, q.name, q.description, q.objective, q.quest_type, q.category, q.location, q.stars, q.zenny
				FROM quest q
				WHERE q.category = :questCat
				ORDER BY q.stars
			"""
		else:
			if self.currentSearch.GetName() == "byMonster":
				sql = f"""
					SELECT q.id, q.name, q.description, q.objective, q.quest_type, q.category, q.location, q.stars, q.zenny
					FROM quest q
					JOIN quest_monsters qm
						ON qm.id = q.id
					WHERE q.category = :questCat
						AND qm.monster_name LIKE '%{searchText}%'
						AND qm.is_objective = 1
					ORDER BY q.stars
				"""
			else:
				sql = f"""
					SELECT q.id, q.name, q.description, q.objective, q.quest_type, q.category, q.location, q.stars, q.zenny
					FROM quest q
					WHERE q.category = :questCat
						AND q.name LIKE '%{searchText}%'
					ORDER BY q.stars
				"""

		conn = sqlite3.connect("mhw.db")
		data = conn.execute(sql, (self.currentQuestTree,))
		data = data.fetchall()

		quests = []
		for row in data:
			quests.append(q.Quest(row))

		starRanks = {
			1: "lr",
			2: "lr",
			3: "lr",
			4: "lr",
			5: "lr",
			6: "hr",
			7: "hr",
			8: "hr",
			9: "hr"
		}

		lastStar = 0
		for quest in quests:
			self.populateQuestTree(quest, lastStar, starRanks[quest.stars])
			lastStar = quest.stars

		self.init = False


	def populateQuestTree(self, quest, lastStar, starIcon):
		self.questTree.AppendRows() 
		row = self.questTree.GetNumberRows() - 1

		if lastStar != quest.stars:
			img = wx.Bitmap(f"images/rank-stars-24/{starIcon}.png")
			self.questTree.SetCellRenderer(row, 0, cgr.ImageTextCellRenderer(
				img, f"{quest.stars}", imageOffset=20, colour=util.hexToRGB(self.rankColors[starIcon]), font=wx.Font(wx.FontInfo(9).Bold())))
			self.questTree.SetCellBackgroundColour(row, 1, util.hexToRGB(self.rankColors[starIcon]))
			self.questTree.SetCellBackgroundColour(row, 2, util.hexToRGB(self.rankColors[starIcon]))
			self.questTree.AppendRows() 
			row = self.questTree.GetNumberRows() - 1

		img = wx.Bitmap(f"images/quests-24/{quest.questType}.png")
		self.questTree.SetCellRenderer(row, 0, cgr.ImageTextCellRenderer(
			img, f"{quest.name}", imageOffset=140))
		if os.path.exists(f"images/locations-24/{quest.location}.png"):
			img = wx.Bitmap(f"images/locations-24/{quest.location}.png")
		else:
			img = wx.Bitmap(f"images/unknown.png")
		self.questTree.SetCellRenderer(row, 1, cgr.ImageTextCellRenderer(
			img, f"{quest.location}", imageOffset=80))
		self.questTree.SetCellValue(row, 2, str(quest.zenny))
		self.questTree.SetCellValue(row, 3, str(quest.id))


	def initQuestDetail(self):
		self.questObjectiveLabel = wx.StaticText(self.questDetailPanel, label="Objective:\n")
		self.questNameLabel = wx.StaticText(self.questDetailPanel, label="Name:\n")
		self.questDescriptionLabel = wx.StaticText(self.questDetailPanel, label="Description")
		self.questDetailSizer.Add(self.questObjectiveLabel, 0.1, wx.EXPAND)
		self.questDetailSizer.Add(self.questNameLabel, 0.1, wx.EXPAND)
		self.questDetailSizer.Add(self.questDescriptionLabel, 0.1, wx.EXPAND)

		self.questDetailList = cgr.HeaderBitmapGrid(self.questDetailPanel)
		self.questDetailList.Bind(wx.EVT_MOUSEWHEEL, self.onScroll)
		self.questDetailList.EnableEditing(False)
		self.questDetailList.EnableDragRowSize(False)
		self.questDetailSizer.Add(self.questDetailList, 0.1, wx.EXPAND)

		self.questDetailList.CreateGrid(6, 2)
		self.questDetailList.SetDefaultRowSize(24, resizeExistingRows=True)
		self.questDetailList.SetColSize(0, 302)
		self.questDetailList.SetColSize(1, 155 - 20)
		self.questDetailList.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
		self.questDetailList.SetColLabelSize(2)
		self.questDetailList.SetRowLabelSize(1)

		self.questMonstersList = wx.ListCtrl(self.questDetailPanel, style=wx.LC_REPORT
																			| wx.LC_VRULES
																			| wx.LC_HRULES
																			)
		self.questMonstersList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onListDoubleClick)
		self.il = wx.ImageList(24, 24)
		self.questMonstersList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
		self.questDetailSizer.Add(self.questMonstersList, 0.1, wx.EXPAND|wx.TOP, 5)

		self.materialsRequiredList = wx.ListCtrl(self.questDetailPanel, style=wx.LC_REPORT
																			| wx.LC_VRULES
																			| wx.LC_HRULES
																			)
		self.materialsRequiredList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onListDoubleClick)
		self.materialsRequiredList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
		self.questDetailSizer.Add(self.materialsRequiredList, 2, wx.EXPAND|wx.TOP, 5)

		self.loadQuestDetail()


	def loadQuestDetail(self):
		self.root.Freeze()

		self.questMonstersList.ClearAll()
		self.materialsRequiredList.ClearAll()
		self.il.RemoveAll()

		sql = """
			SELECT q.id, q.name, q.description, q.objective, q.quest_type, q.category, q.location, q.stars, q.zenny
			FROM quest q
			WHERE q.id = :questID
		"""

		conn = sqlite3.connect("mhw.db")
		data = conn.execute(sql, (self.currentlySelectedQuestID,))
		data = data.fetchone()

		quest = q.Quest(data)

		starRanks = {
			1: "lr",
			2: "lr",
			3: "lr",
			4: "lr",
			5: "lr",
			6: "hr",
			7: "hr",
			8: "hr",
			9: "hr"
		}

		questDetail = {
			"Stars": [f"images/rank-stars-24/{starRanks[quest.stars]}.png", str(quest.stars)],
			"Quest Type": [f"images/quests-24/{quest.questType}.png", str(quest.questType.capitalize())],
			"Category": [None, str(quest.category.capitalize())],
			"Location": [f"images/locations-24/{quest.location}.png", str(quest.location)],
			"Zenny": ["images/zenny.png", str(quest.zenny)],
		}

		self.questObjectiveLabel.SetFont(self.questObjectiveLabel.GetFont().Bold())
		self.questNameLabel.SetFont(self.questNameLabel.GetFont().Bold())

		self.questObjectiveLabel.SetLabel(f"{quest.objective}\n")
		self.questNameLabel.SetLabel(f"{quest.name}:")
		self.questDescriptionLabel.SetLabel(f"{quest.description}\n")
		self.questDescriptionLabel.Wrap(600)

		self.questDetailList.DeleteRows(0, self.questDetailList.GetNumberRows())
		self.questDetailList.AppendRows(len(questDetail))

		for i, (k, v) in enumerate(questDetail.items()):
			self.questDetailList.SetCellValue(i, 0, k)
			if v[0] != None:
				padding = " " * 8
				if os.path.exists(v[0]):
					img = wx.Bitmap(v[0])
				else:
					img = wx.Bitmap("images/unknown.png")
				self.questDetailList.SetCellRenderer(i, 1, cgr.ImageTextCellRenderer(
						img, f"{v[1]}", imageOffset=80))
			else:
				self.questDetailList.SetCellValue(i, 1, v[1])


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
			SELECT qm.monster_id, qm.monster_name, qm.quantity, qm.is_objective 
			FROM quest q
			JOIN quest_monsters qm
				ON qm.id = q.id
			WHERE q.id = :questID
		"""

		conn = sqlite3.connect("mhw.db")
		data = conn.execute(sql, (self.currentlySelectedQuestID,))
		data = data.fetchall()

		monsters = []
		for row in data:
			monsters.append(q.QuestMonster(row))

		for mon in monsters:
			if mon.name == "Kestodon":
				img = self.il.Add(wx.Bitmap(f"images/monsters/24/Kestodon Male.png"))
			else:
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
			if os.path.exists(f"images/items-24/{item.iconName}{item.iconColor}.png"):
				img = self.il.Add(wx.Bitmap(f"images/items-24/{item.iconName}{item.iconColor}.png"))
			else:
				img = self.il.Add(wx.Bitmap(f"images/unknown.png"))
			index = self.materialsRequiredList.InsertItem(self.materialsRequiredList.GetItemCount(), item.name, img)
			self.materialsRequiredList.SetItem(index, 1, f"{item.stack} x {item.percentage}%")
			self.materialsRequiredList.SetItem(index, 2, f"{item.rewardGroup}")
			self.materialsRequiredList.SetItem(index, 3, f"item,{item.id},{item.category}")


	def onQuestSelection(self, event):
		if not self.init:
			self.currentlySelectedQuestID = self.questTree.GetCellValue(event.GetRow(), 3)
			if self.currentlySelectedQuestID != "":
				self.loadQuestDetail()


	def onQuestTypeSelection(self, event):
		self.currentQuestTree = event.GetEventObject().GetName()
		self.loadQuestTree()


	def onListDoubleClick(self, event):
		materialInfo = event.GetEventObject().GetItemText(event.GetEventObject().GetFirstSelected(), 3).split(",")
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

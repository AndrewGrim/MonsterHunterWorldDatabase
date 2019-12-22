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
import PalicoTab as p
import Utilities as util
import Links as link

wxTreeListItem = NewType('wxTreeListItem', None)
dbObject = NewType('dbObject', None)

class PalicoTab:

	def __init__(self, root, mainNotebook, link):
		self.root = root
		self.mainNotebook = mainNotebook
		self.link = link

		self.currentEquipmentTree = "HR"
		self.currentEquipmentID = 78
		self.currentEquipmentCategory = "weapon"
		self.currentGadgetID = 0
		self.testIcon = wx.Bitmap("images/unknown.png", wx.BITMAP_TYPE_ANY)

		self.rarityColors = {
			1: "#C2BFBF",
			2: "#F3F3F3",
			3: "#aac44b",
			4: "#57ac4c",
			5: "#75b8c2",
			6: "#6764d7",
			7: "#895edc",
			8: "#c47c5e",
			9: "#cb7793",
			10: "#4fd1f5",
			11: "#f5d569",
			12: "#d5edfa",
		}

		self.weaponDetail = {
			1: ["images/unknown.png", "Rarity"],
			2: ["images/weapon-detail-24/attack.png", "Melee Attack"],
			3: ["images/weapon-detail-24/attack.png", "Ranged Attack"],
			4: ["images/weapon-detail-24/attacktype.png", "Attack Type"],
			5: ["images/weapon-detail-24/element.png", "Element"],
			6: ["images/weapon-detail-24/elderseal.png", "Elderseal"],
			7: ["images/weapon-detail-24/affinity.png", "Affinity"],
			8: ["images/weapon-detail-24/defense.png", "Defense"],
			9: ["images/points.png", "Buy"]
		}

		self.armorDetail = {
			1: ["images/unknown.png", "Rarity"],
			2: ["images/weapon-detail-24/defense.png", "Defense"],
			3: ["images/damage-types-24/fire.png", "Fire"],
			4: ["images/damage-types-24/water.png", "Water"],
			5: ["images/damage-types-24/ice.png", "Ice"],
			6: [ "images/damage-types-24/thunder.png", "Thunder"],
			7: [ "images/damage-types-24/dragon.png", "Dragon"],
			8: ["images/points.png", "Buy"]
		}

		self.elementColors = {
			"Fire": "EF5350",
			"Water": "2196F3",
			"Ice": "90CAF9",
			"Thunder": "FFEE58",
			"Dragon": "7E57C2",
			"Poison": "AB47BC",
			"Paralysis": "FFCA28",
			"Blast": "8D6E63",
			"Sleep": "78909C",
		}	

		self.initArmorTab()


	def initArmorTab(self):
		self.palicoPanel = wx.Panel(self.mainNotebook)
		self.mainNotebook.AddPage(self.palicoPanel, "Palico")
		self.palicoSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.palicoNotebook = wx.Notebook(self.palicoPanel)
		self.palicoSizer.Add(self.palicoNotebook, 1, wx.EXPAND)

		self.palicoPanel.SetSizer(self.palicoSizer)

		self.initEquipmentPanel()
		self.initGadgetPanel()		

		self.initEquipmentButtons()
		self.initSearch()
		self.initEquipmentTree()
		self.loadEquipmentTree()
		self.initEquipmentDetailTab()
		self.loadEquipmentDetailTab()

		il = wx.ImageList(24, 24)
		eq = il.Add(wx.Bitmap("images/palico/armorset-rarity-24/0.png"))
		gadget = il.Add(wx.Bitmap("images/palico/gadgets/24/0.png"))
		self.palicoNotebook.AssignImageList(il)
		self.palicoNotebook.SetPageImage(0, eq)
		self.palicoNotebook.SetPageImage(1, gadget)
		
		self.equipmentDetailList.Bind(wx.EVT_SIZE, self.onSize)

		self.equipmentDetailPanel.SetScrollRate(20, 20)

	
	def initEquipmentPanel(self):
		self.equipmentPanel = wx.Panel(self.palicoNotebook)
		self.palicoNotebook.AddPage(self.equipmentPanel, "Equipment")
		self.equipmentSizer = wx.BoxSizer(wx.HORIZONTAL)

		self.equipmentTreeSizer = wx.BoxSizer(wx.VERTICAL) 
		
		self.equipmentDetailedSizer = wx.BoxSizer(wx.VERTICAL)
		equipmentImage = wx.Bitmap("images/palico/Felyne Acorn Spade α.jpg", wx.BITMAP_TYPE_ANY)
		self.palicoEquipmentImageLabel = wx.StaticBitmap(self.equipmentPanel, bitmap=equipmentImage, size=(230, 230))
		self.palicoEquipmentImageLabel.SetBackgroundColour((0, 0, 0))

		self.equipmentDetailesNotebook = wx.Notebook(self.equipmentPanel)
		self.equipmentDetailPanel = wx.ScrolledWindow(self.equipmentDetailesNotebook)
		
		self.equipmentDetailSizer = wx.BoxSizer(wx.VERTICAL)
		self.equipmentDetailesNotebook.AddPage(self.equipmentDetailPanel, "Detail")
		self.equipmentDetailPanel.SetSizer(self.equipmentDetailSizer)
		
		self.equipmentDetailedImagesSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.equipmentDetailedImagesSizer.Add(self.palicoEquipmentImageLabel, 1, wx.ALIGN_CENTER)

		self.equipmentDetailedSizer.Add(self.equipmentDetailedImagesSizer, 1, wx.EXPAND)
		self.equipmentDetailedSizer.Add(self.equipmentDetailesNotebook, 3, wx.EXPAND)

		self.equipmentSizer.Add(self.equipmentTreeSizer, 0, wx.EXPAND)
		self.equipmentSizer.Add(self.equipmentDetailedSizer, 1, wx.EXPAND)

		self.equipmentPanel.SetSizer(self.equipmentSizer)

	
	def initGadgetPanel(self):
		self.gadgetPanel = wx.Panel(self.palicoNotebook)
		self.gadgetSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.gadgetDetailSizer = wx.BoxSizer(wx.VERTICAL)

		self.gadgetList = wx.ListCtrl(self.gadgetPanel, style=wx.LC_REPORT
														| wx.LC_VRULES
														| wx.LC_HRULES
														| wx.LC_NO_HEADER
														)
		self.gadgetList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onGadgetSelected)
		self.ilGadgets = wx.ImageList(24, 24)
		self.gadgetList.SetImageList(self.ilGadgets, wx.IMAGE_LIST_SMALL)
		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = ""
		self.gadgetList.InsertColumn(0, info)
		self.gadgetList.SetColumnWidth(0, 690)

		self.gadgetList.InsertColumn(1, info)
		self.gadgetList.SetColumnWidth(1, 0)

		conn = sqlite3.connect("mhw.db")
		data = conn.execute("SELECT * FROM palico_gadget")
		data = data.fetchall()

		gadgets = []
		for row in data:
			gadgets.append(p.PalicoGadget(row))

		for g in gadgets:
			img = self.ilGadgets.Add(wx.Bitmap(f"images/palico/gadgets/24/{g.name}.png"))
			index = self.gadgetList.InsertItem(self.gadgetList.GetItemCount(), g.name, img)
			self.gadgetList.SetItem(index, 1, str(g.id))
		self.gadgetSizer.Add(self.gadgetList, 1, wx.EXPAND)

		self.gadgetSizer.Add(self.gadgetDetailSizer, 1, wx.EXPAND)
		gadget = wx.Bitmap("images/palico/gadgets/180/Vigorwasp Spray.jpg", wx.BITMAP_TYPE_ANY)
		self.palicoGadgetImageLabel = wx.StaticBitmap(self.gadgetPanel, bitmap=gadget, size=(180, 180))
		self.palicoGadgetImageLabel.SetBackgroundColour((0, 0, 0))
		self.gadgetDetailSizer.Add(self.palicoGadgetImageLabel, 1, wx.EXPAND)

		self.gadgetDetailesNotebook = wx.Notebook(self.gadgetPanel)
		self.gadgetDetailPanel = wx.Panel(self.gadgetDetailesNotebook)
		self.gadgetDetailesNotebook.AddPage(self.gadgetDetailPanel, "Detail")
		self.gadgetDetailSizer.Add(self.gadgetDetailesNotebook, 3, wx.EXPAND)

		self.gadgetDetailNotebookSizer = wx.BoxSizer(wx.VERTICAL)
		self.gadgetNameLabel = wx.StaticText(self.gadgetDetailPanel, label="Name:")
		self.gadgetNameLabel.SetFont(self.gadgetNameLabel.GetFont().Bold())
		self.gadgetDetailNotebookSizer.Add(self.gadgetNameLabel, 0.1, wx.EXPAND)
		self.gadgetDescriptionLabel = wx.StaticText(self.gadgetDetailPanel, label="Description")
		self.gadgetDetailNotebookSizer.Add(self.gadgetDescriptionLabel, 0.5, wx.EXPAND)

		self.gadgetUnlockConditionLabel = wx.StaticText(self.gadgetDetailPanel, label="Unlock Condition:")
		self.gadgetUnlockConditionLabel.SetFont(self.gadgetUnlockConditionLabel.GetFont().Bold())
		self.gadgetDetailNotebookSizer.Add(self.gadgetUnlockConditionLabel, 0.1, wx.EXPAND)

		self.gadgetUnlockConditionDescriptionLabel = wx.StaticText(self.gadgetDetailPanel, label="Description")
		self.gadgetUnlockConditionDescriptionLabel.SetFont(self.gadgetUnlockConditionDescriptionLabel.GetFont())
		self.gadgetDetailNotebookSizer.Add(self.gadgetUnlockConditionDescriptionLabel, 0.5, wx.EXPAND)

		self.level1Label = wx.StaticText(self.gadgetDetailPanel, label="Level 1:")
		self.level1Label.SetFont(self.level1Label.GetFont().Bold())
		self.gadgetDetailNotebookSizer.Add(self.level1Label, 0.1, wx.EXPAND)

		self.level1DescriptionLabel = wx.StaticText(self.gadgetDetailPanel, label="Description")
		self.gadgetDetailNotebookSizer.Add(self.level1DescriptionLabel, 0.5, wx.EXPAND)

		self.level2Label = wx.StaticText(self.gadgetDetailPanel, label="Level 2:")
		self.level2Label.SetFont(self.level2Label.GetFont().Bold())
		self.gadgetDetailNotebookSizer.Add(self.level2Label, 0.1, wx.EXPAND)

		self.level2DescriptionLabel = wx.StaticText(self.gadgetDetailPanel, label="Description")
		self.gadgetDetailNotebookSizer.Add(self.level2DescriptionLabel, 0.5, wx.EXPAND)

		self.level3Label = wx.StaticText(self.gadgetDetailPanel, label="Level 3:")
		self.level3Label.SetFont(self.level3Label.GetFont().Bold())
		self.gadgetDetailNotebookSizer.Add(self.level3Label, 0.1, wx.EXPAND)

		self.level3DescriptionLabel = wx.StaticText(self.gadgetDetailPanel, label="Description")
		self.gadgetDetailNotebookSizer.Add(self.level3DescriptionLabel, 0.5, wx.EXPAND)

		self.gadgetDetailPanel.SetSizer(self.gadgetDetailNotebookSizer)
		self.gadgetPanel.SetSizer(self.gadgetSizer)
		self.palicoNotebook.AddPage(self.gadgetPanel, "Gadgets")

		self.loadGadgetDetail()


	def loadGadgetDetail(self):
		self.root.Freeze()
		conn = sqlite3.connect("mhw.db")
		data = conn.execute("SELECT * FROM palico_gadget WHERE id = :gadgetID", (self.currentGadgetID,))
		data = data.fetchone()

		g = p.PalicoGadget(data)

		self.palicoGadgetImageLabel.SetBitmap(wx.Bitmap(f"images/palico/gadgets/180/{g.name}.jpg"))

		self.gadgetNameLabel.SetLabel(f"{g.name}:")
		self.gadgetDescriptionLabel.SetLabel(f"{g.description}\n")
		self.gadgetDescriptionLabel.Wrap(600)

		self.gadgetUnlockConditionLabel.SetLabel("Unlock Condition:")
		self.gadgetUnlockConditionDescriptionLabel.SetLabel(f"{g.unlockCondition}\n")
		self.gadgetUnlockConditionDescriptionLabel.Wrap(600)

		conn = sqlite3.connect("mhw.db")
		data = conn.execute("SELECT * FROM palico_gadget_level WHERE id = :gadgetID", (self.currentGadgetID,))
		data = data.fetchall()

		self.level1Label.SetLabel("Level 1:")
		self.level1DescriptionLabel.SetLabel(f"{data[0][2]} - {data[0][3]}\n\n")
		self.level1DescriptionLabel.Wrap(600)

		self.level2Label.SetLabel("Level 5:")
		self.level2DescriptionLabel.SetLabel(f"{data[1][2]} - {data[1][3]}\n\n{data[2][2]} - {data[2][3]}\n\n")
		self.level2DescriptionLabel.Wrap(600)

		self.level3Label.SetLabel("Level 10:")
		self.level3DescriptionLabel.SetLabel(f"{data[3][2]} - {data[3][3]}\n\n")
		self.level3DescriptionLabel.Wrap(600)

		width, height = self.gadgetPanel.GetSize()
		self.gadgetPanel.SetSize(width + 1, height + 1)
		self.gadgetPanel.SetSize(width, height)
		self.root.Thaw()

	
	def onGadgetSelected(self, event):
		self.currentGadgetID = str(self.gadgetList.GetItemText(event.GetEventObject().GetFirstSelected(), 1))
		self.loadGadgetDetail()


	def initEquipmentButtons(self):
		self.lowRankButton = wx.Button(self.equipmentPanel, label="Low Rank", name="LR")
		self.lowRankButton.SetBitmap(wx.Bitmap("images/rank-stars-24/lr.png"))
		self.highRankButton = wx.Button(self.equipmentPanel, label="High Rank", name="HR")
		self.highRankButton.SetBitmap(wx.Bitmap("images/rank-stars-24/hr.png"))
		#self.masterRankButton = wx.Button(self.equipmentPanel, label="Master Rank", name="MR")
		#self.masterRankButton.SetBitmap(wx.Bitmap("images/rank-stars-24/mr.png"))

		self.lowRankButton.Bind(wx.EVT_BUTTON, self.onEquipmentRankSelection)
		self.highRankButton.Bind(wx.EVT_BUTTON, self.onEquipmentRankSelection)
		#self.masterRankButton.Bind(wx.EVT_BUTTON, self.onEquipmentRankSelection)
	
		self.equipmentButtonsSizer = wx.BoxSizer(wx.HORIZONTAL)

		self.equipmentButtonsSizer.Add(self.lowRankButton)
		self.equipmentButtonsSizer.Add(self.highRankButton)
		#self.equipmentButtonsSizer.Add(self.masterRankButton)

		self.equipmentTreeSizer.Add(self.equipmentButtonsSizer)

	
	def initSearch(self):
		self.search = wx.TextCtrl(self.equipmentPanel)
		self.search.SetHint("  search by name")
		self.search.Bind(wx.EVT_TEXT, self.onSearchTextEnter)
		self.equipmentButtonsSizer.Add(380, 0, 0)
		self.equipmentButtonsSizer.Add(self.search, 0, wx.ALIGN_CENTER_VERTICAL)


	def onSearchTextEnter(self, event):
		self.loadEquipmentTree()


	def initEquipmentTree(self):
		self.armorTree = cgr.HeaderBitmapGrid(self.equipmentPanel)
		self.armorTree.EnableEditing(False)
		self.armorTree.EnableDragRowSize(False)
		self.armorTree.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.onEquipmentSelection)
		self.equipmentTreeSizer.Add(self.armorTree, 1, wx.EXPAND)

		armorTreeColumns = {
			"Name": [685, wx.Bitmap("images/noImage24.png")],
			"id": [0,  wx.Bitmap("images/noImage24.png")],
		}

		self.armorTree.CreateGrid(1, len(armorTreeColumns))
		self.armorTree.SetDefaultRowSize(24, resizeExistingRows=True)
		self.armorTree.HideRowLabels()
		self.armorTree.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
		

		for col, (k, v) in enumerate(armorTreeColumns.items()):
			if col == 0:
				self.armorTree.SetColLabelRenderer(col, cgr.HeaderBitmapColLabelRenderer(v[1], k))
			else:
				self.armorTree.SetColLabelRenderer(col, cgr.HeaderBitmapColLabelRenderer(v[1], ""))
			self.armorTree.SetColSize(col, v[0])


	def loadEquipmentTree(self):
		try:
			self.armorTree.DeleteRows(0, self.armorTree.GetNumberRows())
		except:
			pass

		searchText = self.search.GetValue().replace("'", "''").replace("'", "''")
		conn = sqlite3.connect("mhw.db")

		sql = """
			SELECT
				(SELECT count(*) FROM palico_weapon) +
				(SELECT count(*) FROM palico_armor)
		"""

		data = conn.execute(sql, ())
		data = data.fetchone()
		rowCount = int(data[0])

		equipmentList = []
		if len(searchText) == 0 or searchText == " ":
			for num in range(rowCount):
				if num % 3 == 0 or num == 0:
					data = conn.execute(f"SELECT * FROM palico_weapon WHERE id = {num} AND rank = '{self.currentEquipmentTree}'")
					data = data.fetchone()
					if data != None:
						equipmentList.append(p.PalicoWeapon(data))
				else:
					data = conn.execute(f"SELECT * FROM palico_armor WHERE id = {num} AND rank = '{self.currentEquipmentTree}'")
					data = data.fetchone()
					if data != None:
						equipmentList.append(p.PalicoArmor(data))
		else:
			data = conn.execute(f"SELECT * FROM palico_weapon WHERE rank = '{self.currentEquipmentTree}' AND name LIKE '%{searchText}%' OR rank = '{self.currentEquipmentTree}' AND set_name LIKE '%{searchText}%'")
			data = data.fetchall()
			if len(data) != 0:
				for eq in data:
					equipmentList.append(p.PalicoWeapon(eq))
			data = conn.execute(f"SELECT * FROM palico_armor WHERE rank = '{self.currentEquipmentTree}' AND name LIKE '%{searchText}%' OR rank = '{self.currentEquipmentTree}' AND set_name LIKE '%{searchText}%'")
			data = data.fetchall()
			if len(data) != 0:
				for eq in data:
					equipmentList.append(p.PalicoArmor(eq))

		self.populateArmorTree(equipmentList)


	def populateArmorTree(self, equipmentList: List[dbObject]) -> None:
		"""
		equipmentList = The list of all the queried Equipment objects, which contain the data pertaining to the individual equipment pieces.
		"""

		equipmentSet = "" 
		row = 0
		if self.root.pref.unicodeSymbols:
			piecePadding = "┗━━━" + (12 * " ")
		else:
			piecePadding = " " * 20
		setPadding = " " * 8
		for eq in equipmentList:
			self.armorTree.AppendRows()
			if eq.setName != equipmentSet:
				img = wx.Bitmap(f"images/palico/armorset-rarity-24/{eq.rarity}.png")
				self.armorTree.SetCellRenderer(row, 0, cgr.ImageTextCellRenderer(
					img, f"{setPadding}{eq.setName}", hAlign=wx.ALIGN_LEFT, imageOffset=330))
				self.armorTree.AppendRows()
				row += 1
			equipmentSet = eq.setName
			if eq.id % 3 == 0 or eq.id == 0:
				img = wx.Bitmap(f"images/palico/{eq.attackType.lower()}-rarity-24/{eq.rarity}.png")
			elif eq.id % 3 == 2:
				img = wx.Bitmap(f"images/palico/chest-rarity-24/{eq.rarity}.png")
			else:
				img = wx.Bitmap(f"images/palico/head-rarity-24/{eq.rarity}.png")
			self.armorTree.SetCellRenderer(row, 0, cgr.ImageTextCellRenderer(
				img, f"{piecePadding}{eq.name}", hAlign=wx.ALIGN_LEFT, imageOffset=295))
			self.armorTree.SetCellValue(row, 1, str(eq.id))

			row += 1


	def initEquipmentDetailTab(self):
		self.equipmentDetailList = cgr.HeaderBitmapGrid(self.equipmentDetailPanel)
		self.equipmentDetailList.Bind(wx.EVT_MOUSEWHEEL, self.onScroll)
		self.equipmentDetailList.EnableEditing(False)
		self.equipmentDetailList.EnableDragRowSize(False)
		self.equipmentDetailSizer.Add(self.equipmentDetailList, 1, wx.EXPAND)

		self.equipmentDetailList.CreateGrid(len(self.weaponDetail) + 1, 2)
		self.equipmentDetailList.SetDefaultRowSize(24, resizeExistingRows=True)
		self.equipmentDetailList.SetColSize(0, 302)
		self.equipmentDetailList.SetColSize(1, 155 - 20)
		self.equipmentDetailList.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
		self.equipmentDetailList.SetColLabelSize(2)
		self.equipmentDetailList.SetRowLabelSize(1)

		self.equipmentMaterialsList = wx.ListCtrl(self.equipmentDetailPanel, style=wx.LC_REPORT
																	| wx.LC_VRULES
																	| wx.LC_HRULES
																	)
		self.equipmentMaterialsList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onMaterialDoubleClick)
		self.il = wx.ImageList(24, 24)
		self.equipmentMaterialsList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
		self.equipmentDetailSizer.Add(self.equipmentMaterialsList, 1, wx.EXPAND)


	def loadEquipmentDetailTab(self):
		self.root.Freeze()
		self.loadEquipmentDetail()
		width, height = self.equipmentPanel.GetSize()
		self.equipmentPanel.SetSize(width + 1, height + 1)
		self.equipmentPanel.SetSize(width, height)
		self.root.Thaw()


	def loadEquipmentDetail(self):
		self.equipmentDetailList.DeleteRows(0, self.equipmentDetailList.GetNumberRows())
		self.equipmentDetailList.AppendRows(len(self.weaponDetail) + 1)

		self.il.RemoveAll()

		if self.currentEquipmentCategory == "weapon":
			sql = "SELECT * FROM palico_weapon WHERE id = :id"

			conn = sqlite3.Connection("mhw.db")
			data = conn.execute(sql, (self.currentEquipmentID,))
			data = data.fetchone()

			weapon = p.PalicoWeapon(data)

			noLog = wx.LogNull()
			try:
				self.palicoEquipmentImageLabel.SetBitmap(wx.Bitmap(f"images/palico/{weapon.name}.jpg"))
			except:
				self.palicoEquipmentImageLabel.SetBitmap(wx.Bitmap(f"images/noImage.png"))
			del noLog
			
			weaponDetail = {
				0: str(weapon.name),
				1: str(weapon.rarity),
				2: str(weapon.attackMelee),
				3: str(weapon.attackRanged),
				4: str(weapon.attackType),
				5: str(weapon.elementAttack),
				6: str(weapon.elderseal),
				7: str(weapon.affinity),
				8: str(weapon.defense),
				9: str(weapon.price)
			}

			imageOffset = 55
			rarityIcon = wx.Bitmap(f"images/palico/{weapon.attackType.lower()}-rarity-24/{weapon.rarity}.png")
			if weapon.element != "None":
				element = wx.Bitmap(f"images/damage-types-24/{weapon.element.lower()}.png")

			self.equipmentDetailList.SetCellValue(0, 0, "Name")
			self.equipmentDetailList.SetCellValue(0, 1, weapon.name)
			for num in range(1, len(weaponDetail)):
				if num == 1:
					self.equipmentDetailList.SetCellRenderer(num, 0,
										cgr.ImageTextCellRenderer(
																	rarityIcon,
																	self.weaponDetail[num][1],
																	imageOffset=imageOffset,
																))
					self.equipmentDetailList.SetCellBackgroundColour(num, 1, util.hexToRGB(self.rarityColors[weapon.rarity]))
				else:
					self.equipmentDetailList.SetCellRenderer(num, 0,
										cgr.ImageTextCellRenderer(
											wx.Bitmap(self.weaponDetail[num][0]), 
											self.weaponDetail[num][1], 
											imageOffset=imageOffset
											))

				if weaponDetail[num] == "None":
					self.equipmentDetailList.SetCellValue(num, 1, "-")
				else:
					if num == 5:
						if weapon.element != "None":
							self.equipmentDetailList.SetCellRenderer(num, 1,
											cgr.ImageTextCellRenderer(
																		element,
																		weaponDetail[num],
																		imageOffset=imageOffset - 25,
																		colour=util.hexToRGB(self.elementColors[weapon.element]),
																	))
						else:
							self.equipmentDetailList.SetCellValue(num, 1, "-")
					elif num == 6:
						if weapon.elderseal != None:
							self.equipmentDetailList.SetCellBackgroundColour(num, 1, util.hexToRGB("#D1C4E9"))
							self.equipmentDetailList.SetCellValue(num, 1, weaponDetail[num])
					elif num == 7:
						if weapon.affinity.find("+") != -1:
							self.equipmentDetailList.SetCellBackgroundColour(num, 1, util.hexToRGB("#C8E6C9"))
							self.equipmentDetailList.SetCellValue(num, 1, weaponDetail[num])
						elif weapon.affinity.find("-") != -1:
							self.equipmentDetailList.SetCellBackgroundColour(num, 1, util.hexToRGB("#FFCDD2"))
							self.equipmentDetailList.SetCellValue(num, 1, weaponDetail[num])
						else:
							self.equipmentDetailList.SetCellValue(num, 1, "-")
					elif num == 8:
						if weapon.defense != None:
							self.equipmentDetailList.SetCellBackgroundColour(num, 1, util.hexToRGB("#D7CCC8"))
							self.equipmentDetailList.SetCellValue(num, 1, weaponDetail[num])
						else:
							self.equipmentDetailList.SetCellValue(num, 1, "-")
					else:
						self.equipmentDetailList.SetCellValue(num, 1, weaponDetail[num])
		else:
			sql = "SELECT * FROM palico_armor WHERE id = :id"

			conn = sqlite3.Connection("mhw.db")
			data = conn.execute(sql, (self.currentEquipmentID,))
			data = data.fetchone()

			armor = p.PalicoArmor(data)

			noLog = wx.LogNull()
			try:
				self.palicoEquipmentImageLabel.SetBitmap(wx.Bitmap(f"images/palico/{armor.name}.jpg"))
			except:
				self.palicoEquipmentImageLabel.SetBitmap(wx.Bitmap(f"images/noImage.png"))
			del noLog
			
			armorDetail = {
				0: str(armor.name),
				1: str(armor.rarity),
				2: str(armor.defense),
				3: str(armor.fire),
				4: str(armor.water),
				5: str(armor.thunder),
				6: str(armor.ice),
				7: str(armor.dragon),
				8: str(armor.price)
			}

			colorLevel = 0
			imageOffset = 55
			if armor.fullArmorSet == 1:
				rarityIcon = wx.Bitmap(f"images/palico/armorset-rarity-24/{armor.rarity}.png")
			elif armor.id % 3 == 2:
				rarityIcon = wx.Bitmap(f"images/palico/chest-rarity-24/{armor.rarity}.png")
			else:
				rarityIcon = wx.Bitmap(f"images/palico/head-rarity-24/{armor.rarity}.png")

			self.equipmentDetailList.SetCellValue(0, 0, "Name")
			self.equipmentDetailList.SetCellValue(0, 1, armor.name)
			for num in range(1, len(armorDetail)):
				if num == 3:
					self.equipmentDetailList.SetCellBackgroundColour(num, 1, util.hexToRGB(util.damageColors["fire"][colorLevel]))
				elif num == 4:
					self.equipmentDetailList.SetCellBackgroundColour(num, 1, util.hexToRGB(util.damageColors["water"][colorLevel]))
				elif num == 5:
					self.equipmentDetailList.SetCellBackgroundColour(num, 1, util.hexToRGB(util.damageColors["thunder"][colorLevel]))
				elif num == 6:
					self.equipmentDetailList.SetCellBackgroundColour(num, 1, util.hexToRGB(util.damageColors["ice"][colorLevel]))
				elif num == 7:
					self.equipmentDetailList.SetCellBackgroundColour(num, 1, util.hexToRGB(util.damageColors["dragon"][colorLevel]))

				if num == 1:
					self.equipmentDetailList.SetCellRenderer(num, 0,
										cgr.ImageTextCellRenderer(
																	rarityIcon,
																	self.armorDetail[num][1],
																	imageOffset=imageOffset,
																))
					self.equipmentDetailList.SetCellBackgroundColour(num, 1, util.hexToRGB(self.rarityColors[armor.rarity]))
				else:
					self.equipmentDetailList.SetCellRenderer(num, 0,
										cgr.ImageTextCellRenderer(
											wx.Bitmap(self.armorDetail[num][0]), 
											self.armorDetail[num][1], 
											imageOffset=imageOffset
											))

				if armorDetail[num] in ["None", "None 0"]:
					self.equipmentDetailList.SetCellValue(num, 1, "-")
				else:
					self.equipmentDetailList.SetCellValue(num, 1, armorDetail[num])
		
		self.loadEquipmentMaterials()


	def loadEquipmentMaterials(self):
		self.equipmentMaterialsList.ClearAll()

		sql = f"""
			SELECT i.id item_id, it.name item_name, i.icon_name item_icon_name,
				i.category item_category, i.icon_color item_icon_color, w.quantity
			FROM palico_{self.currentEquipmentCategory}_recipe w
				JOIN item i
					ON w.item_id = i.id
				JOIN item_text it
					ON it.id = i.id
					AND it.lang_id = 'en'
			WHERE it.lang_id = 'en'
			AND w.id = :equipmentID
			ORDER BY i.id
		"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, (self.currentEquipmentID,))
		data = data.fetchall()

		if data != None:
			equipmentMaterials = []
			for row in data:
				equipmentMaterials.append(p.PalicoEquipmentMaterial(row))

			info = wx.ListItem()
			info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
			info.Image = -1
			info.Align = wx.LIST_FORMAT_LEFT
			info.Text = "Req. Materials"
			self.equipmentMaterialsList.InsertColumn(0, info)
			self.equipmentMaterialsList.SetColumnWidth(0, self.equipmentDetailPanel.GetSize()[0] * 0.66)

			info = wx.ListItem()
			info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
			info.Image = -1
			info.Align = wx.LIST_FORMAT_CENTER
			info.Text = ""
			self.equipmentMaterialsList.InsertColumn(1, info)
			self.equipmentMaterialsList.SetColumnWidth(1, self.equipmentDetailPanel.GetSize()[0] * 0.34 - 40)

			self.equipmentMaterialsList.InsertColumn(2, info)
			self.equipmentMaterialsList.SetColumnWidth(2, 0)

			for material in equipmentMaterials:
				try:
					img = self.il.Add(wx.Bitmap(f"images/items-24/{material.iconName}{material.iconColor}.png"))
				except:
					img = self.il.Add(wx.Bitmap(f"images/unknown.png"))
				index = self.equipmentMaterialsList.InsertItem(self.equipmentMaterialsList.GetItemCount(), material.name, img)
				self.equipmentMaterialsList.SetItem(index, 1, str(material.quantity))
				self.equipmentMaterialsList.SetItem(index, 2, f"{material.id},{material.category}")


	def onEquipmentRankSelection(self, event):
		"""
		When an equipment rank button at the top of the screen is pressed the equipment tree is reloaded with the new equipment rank information.
		"""

		self.currentEquipmentTree = event.GetEventObject().GetName()
		self.loadEquipmentTree()


	def onEquipmentSelection(self, event):
		"""
		When a specific equipment piece is selected in the tree, the detail view gets populated with the information from the database.
		"""

		if self.armorTree.GetCellValue(event.GetRow(), 1) != "":
			self.currentEquipmentID = int(self.armorTree.GetCellValue(event.GetRow(), 1))
			r = self.currentEquipmentID % 3
			if r == 0:
				self.currentEquipmentCategory = "weapon"
			else:
				self.currentEquipmentCategory = "armor"

			self.loadEquipmentDetailTab()


	def onMaterialDoubleClick(self, event):
		materialInfo = event.GetEventObject().GetItemText(event.GetEventObject().GetFirstSelected(), 2)
		materialInfo = materialInfo.split(",")
		self.link.event = True
		self.link.eventType = "item"
		self.link.info =  link.GenericDoubleLink(materialInfo)
		self.root.followLink()
		self.link.reset()


	def onSize(self, event):
		"""
		When the application window is resized some columns's width gets readjusted.
		"""

		try:
			self.equipmentDetailList.SetColSize(0, self.equipmentDetailPanel.GetSize()[0] * 0.66)
			self.equipmentDetailList.SetColSize(1, self.equipmentDetailPanel.GetSize()[0] * 0.34 - 20)
			self.equipmentMaterialsList.SetColumnWidth(0, self.equipmentDetailPanel.GetSize()[0] * 0.66)
			self.equipmentMaterialsList.SetColumnWidth(1, self.equipmentDetailPanel.GetSize()[0] * 0.34 - 40)
		except:
			pass


	def onScroll(self, event):
		"""
		On every scroll event in armorDetail, scrolls the parent ScrolledWindow by 3 in the appropriate direction.
		"""

		if event.GetWheelRotation() > 0:
			if self.equipmentDetailPanel.GetViewStart()[1] < 3:
				self.equipmentDetailPanel.Scroll(0, self.equipmentDetailPanel.GetViewStart()[1] + 1 * -1)
			else:
				self.equipmentDetailPanel.Scroll(0, self.equipmentDetailPanel.GetViewStart()[1] + 3 * -1)
		else:
			if self.equipmentDetailPanel.GetViewStart()[1] < 3:
				self.equipmentDetailPanel.Scroll(0, self.equipmentDetailPanel.GetViewStart()[1] + 1)
			else:
				self.equipmentDetailPanel.Scroll(0, self.equipmentDetailPanel.GetViewStart()[1] + 3)
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

import ArmorTab as a
import Utilities as util
import Links as link

wxTreeListItem = NewType('wxTreeListItem', None)
dbArmor = NewType('Armor', None)

class PalicoTab:

	def __init__(self, root, mainNotebook, link):
		self.root = root
		self.mainNotebook = mainNotebook
		self.link = link

		self.currentArmorTree = "HR"
		self.currentlySelectedArmorID = 159
		self.currentlySelectedArmorSetID = 39
		self.testIcon = wx.Bitmap("images/unknown.png", wx.BITMAP_TYPE_ANY)

		self.rarityColors = {
			1: "C2BFBF",
			2: "F3F3F3",
			3: "A9B978",
			4: "6AAC85",
			5: "55D1F0",
			6: "5e8efc",
			7: "9D93E7",
			8: "B58377",
		}

		self.weaponDetail = {
			# TODO might need an extra column here, will need to double check screenshots/in-game data
			# damage type ??? slash/blunt
			1: ["images/unknown.png", "Rarity"],
			2: ["images/weapon-detail-24/attack.png", "Attack"],
			8: ["images/weapon-detail-24/element.png", "Element"],
			9: ["images/weapon-detail-24/affinity.png", "Affinity"],
			10: ["images/weapon-detail-24/defense.png", "Defense"],
		}

		self.armorDetail = {
			1: ["images/unknown.png", "Rarity"],
			2: ["images/weapon-detail-24/defense.png", "Defense"],
			8: ["images/damage-types-24/fire.png", "Fire"],
			9: ["images/damage-types-24/water.png", "Water"],
			10: ["images/damage-types-24/ice.png", "Ice"],
			11: [ "images/damage-types-24/thunder.png", "Thunder"],
			12: [ "images/damage-types-24/dragon.png", "Dragon"],
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

		self.initArmorButtons()
		self.initSearch()
		self.initArmorTree()
		self.loadArmorTree()
		self.initArmorDetailTab()
		#self.loadArmorDetailAll()
		
		self.armorDetailList.Bind(wx.EVT_SIZE, self.onSize)

		self.armorDetailPanel.SetScrollRate(20, 20)

	
	def initEquipmentPanel(self):
		self.equipmentPanel = wx.Panel(self.palicoNotebook)
		self.palicoNotebook.AddPage(self.equipmentPanel, "Equipment")
		self.armorSizer = wx.BoxSizer(wx.HORIZONTAL)

		self.armorTreeSizer = wx.BoxSizer(wx.VERTICAL) 
		
		self.armorDetailedSizer = wx.BoxSizer(wx.VERTICAL)
		armorImage = wx.Bitmap("images/armor/male/Leather Headgear.jpg", wx.BITMAP_TYPE_ANY)
		self.armorMaleImageLabel = wx.StaticBitmap(self.equipmentPanel, bitmap=armorImage, size=(230, 230))
		self.armorFemaleImageLabel = wx.StaticBitmap(self.equipmentPanel, bitmap=armorImage, size=(230, 230))
		self.armorMaleImageLabel.SetBackgroundColour((0, 0, 0))
		self.armorFemaleImageLabel.SetBackgroundColour((0, 0, 0))

		self.armorDetailsNotebook = wx.Notebook(self.equipmentPanel)
		self.armorDetailPanel = wx.ScrolledWindow(self.armorDetailsNotebook)
		
		self.armorDetailSizer = wx.BoxSizer(wx.VERTICAL)
		self.armorDetailsNotebook.AddPage(self.armorDetailPanel, "Detail")
		self.armorDetailPanel.SetSizer(self.armorDetailSizer)
		
		self.armorDetailedImagesSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.armorDetailedImagesSizer.Add(self.armorMaleImageLabel, 1, wx.ALIGN_CENTER)
		self.armorDetailedImagesSizer.Add(self.armorFemaleImageLabel, 1, wx.ALIGN_CENTER)

		self.armorDetailedSizer.Add(self.armorDetailedImagesSizer, 1, wx.EXPAND)
		self.armorDetailedSizer.Add(self.armorDetailsNotebook, 3, wx.EXPAND)

		self.armorSizer.Add(self.armorTreeSizer, 0, wx.EXPAND)
		self.armorSizer.Add(self.armorDetailedSizer, 1, wx.EXPAND)

		self.equipmentPanel.SetSizer(self.armorSizer)

	
	def initGadgetPanel(self):
		# TODO gagdet panel for palicos
		self.gadgetPanel = wx.Panel(self.palicoNotebook)
		self.gadgetSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.gadgetPanel.SetSizer(self.gadgetSizer)
		self.palicoNotebook.AddPage(self.gadgetPanel, "Gadgets")


	def initArmorButtons(self):
		self.lowRankButton = wx.Button(self.equipmentPanel, label="Low Rank", name="LR")
		self.lowRankButton.SetBitmap(wx.Bitmap("images/rank-stars-24/lr.png"))
		self.highRankButton = wx.Button(self.equipmentPanel, label="High Rank", name="HR")
		self.highRankButton.SetBitmap(wx.Bitmap("images/rank-stars-24/hr.png"))
		#self.masterRankButton = wx.Button(self.equipmentPanel, label="Master Rank", name="MR")
		#self.masterRankButton.SetBitmap(wx.Bitmap("images/rank-stars-24/mr.png"))

		self.lowRankButton.Bind(wx.EVT_BUTTON, self.onArmorTypeSelection)
		self.highRankButton.Bind(wx.EVT_BUTTON, self.onArmorTypeSelection)
		#self.masterRankButton.Bind(wx.EVT_BUTTON, self.onArmorTypeSelection)
	
		self.armorButtonsSizer = wx.BoxSizer(wx.HORIZONTAL)

		self.armorButtonsSizer.Add(self.lowRankButton)
		self.armorButtonsSizer.Add(self.highRankButton)
		#self.armorButtonsSizer.Add(self.masterRankButton)

		self.armorTreeSizer.Add(self.armorButtonsSizer)

	
	def initSearch(self):
		self.search = wx.TextCtrl(self.equipmentPanel)
		self.search.SetHint("  search by name")
		self.search.Bind(wx.EVT_TEXT, self.onSearchTextEnter)
		self.armorButtonsSizer.Add(380, 0, 0)
		self.armorButtonsSizer.Add(self.search, 0, wx.ALIGN_CENTER_VERTICAL)


	def onSearchTextEnter(self, event):
		self.loadArmorTree()


	def initArmorTree(self):
		self.armorTree = cgr.HeaderBitmapGrid(self.equipmentPanel)
		self.armorTree.EnableEditing(False)
		self.armorTree.EnableDragRowSize(False)
		self.armorTree.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.onArmorSelection)
		self.armorTreeSizer.Add(self.armorTree, 1, wx.EXPAND)

		armorTreeColumns = {
			"Name": [324, wx.Bitmap("images/noImage24.png")],
			"Defense": [32, wx.Bitmap("images/weapon-detail-24/defense.png")],
			"Fire": [32, wx.Bitmap("images/damage-types-24/fire.png")],
			"Water": [32, wx.Bitmap("images/damage-types-24/water.png")],
			"Ice": [32, wx.Bitmap("images/damage-types-24/ice.png")],
			"Thunder": [32, wx.Bitmap("images/damage-types-24/thunder.png")],
			"Dragon": [32, wx.Bitmap("images/damage-types-24/dragon.png")],
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


	def loadArmorTree(self):
		try:
			self.armorTree.DeleteRows(0, self.armorTree.GetNumberRows())
		except:
			pass

		searchText = self.search.GetValue().replace("'", "''").replace("'", "''")

		if len(searchText) == 0 or searchText == " ":
			sql = """
				SELECT a.*, at.name, ast.name armorset_name
				FROM armor a
					JOIN armor_text at USING (id)
					JOIN armorset_text ast
						ON ast.id = a.armorset_id
						AND ast.lang_id = at.lang_id
				WHERE at.lang_id = :langId
				AND (:rank IS NULL OR a.rank = :rank)
			"""
		else:
			sql = f"""
				SELECT a.*, at.name, ast.name armorset_name
				FROM armor a
					JOIN armor_text at USING (id)
					JOIN armorset_text ast
						ON ast.id = a.armorset_id
						AND ast.lang_id = at.lang_id
				WHERE at.lang_id = :langId
				AND (:rank IS NULL OR a.rank = :rank)
				AND at.name LIKE '%{searchText}%'
			"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, ("en", self.currentArmorTree))
		data = data.fetchall()

		armorList = []
		
		for row in data:
			armorList.append(a.Armor(row))
		#self.populateArmorTree(armorList)


	def populateArmorTree(self, armorList: List[dbArmor]) -> None:
		"""
		armorList = The list of all the queried Armor objects, which contain the data pertaining to the individual armor pieces.
		"""

		armorSet = "" 
		row = 0
		if self.root.pref.unicodeSymbols:
			piecePadding = "┗━━━            "
		else:
			piecePadding = "                    "
		setPadding = "        "
		for a in armorList:
			self.armorTree.AppendRows()
			if a.armorSetName != armorSet:
				img = wx.Bitmap(f"images/armor/armorset/rarity-24/{a.rarity}.png")
				if a.armorSetName[0:11] == "King Beetle":
					name = a.name.replace("King", "King / Queen")
					self.armorTree.SetCellRenderer(row, 0, cgr.ImageTextCellRenderer(
						img, f"{setPadding}{name}", hAlign=wx.ALIGN_LEFT, imageOffset=150))
				else:
					self.armorTree.SetCellRenderer(row, 0, cgr.ImageTextCellRenderer(
						img, f"{setPadding}{a.armorSetName}", hAlign=wx.ALIGN_LEFT, imageOffset=150))
				self.armorTree.AppendRows()
				row += 1
			armorSet = a.armorSetName
			img = wx.Bitmap(f"images/armor/{a.armorType}/rarity-24/{a.rarity}.png")
			if a.name[0:11] == "King Beetle":
				name = a.name.replace("King", "King / Queen")
				self.armorTree.SetCellRenderer(row, 0, cgr.ImageTextCellRenderer(
					img, f"{piecePadding}{name}", hAlign=wx.ALIGN_LEFT, imageOffset=115))
			else:
				self.armorTree.SetCellRenderer(row, 0, cgr.ImageTextCellRenderer(
					img, f"{piecePadding}{a.name}", hAlign=wx.ALIGN_LEFT, imageOffset=115))
			self.armorTree.SetCellValue(row, 4, str(a.defenseBase))
			self.armorTree.SetCellValue(row, 5, str(a.defenseMax))
			self.armorTree.SetCellValue(row, 6, str(a.defenseAugmentedMax))
			self.armorTree.SetCellValue(row, 7, str(a.fire))
			self.armorTree.SetCellValue(row, 8, str(a.water))
			self.armorTree.SetCellValue(row, 9, str(a.ice))
			self.armorTree.SetCellValue(row, 10, str(a.thunder))
			self.armorTree.SetCellValue(row, 11, str(a.dragon))
			self.armorTree.SetCellValue(row, 12, str(a.id))
			self.armorTree.SetCellValue(row, 13, str(a.armorSetID))

			if a.slot1 != 0:
				self.armorTree.SetCellRenderer(row, 1,  cgr.ImageCellRenderer(
					wx.Bitmap(f"images/decoration-slots-24/{a.slot1}.png")))
			if a.slot2 != 0:
				self.armorTree.SetCellRenderer(row, 2, cgr.ImageCellRenderer(
					wx.Bitmap(f"images/decoration-slots-24/{a.slot2}.png")))
			if a.slot3 != 0:
				self.armorTree.SetCellRenderer(row, 3,  cgr.ImageCellRenderer(
					wx.Bitmap(f"images/decoration-slots-24/{a.slot3}.png")))
			row += 1


	def initArmorDetailTab(self):
		self.armorDetailList = cgr.HeaderBitmapGrid(self.armorDetailPanel)
		self.armorDetailList.Bind(wx.EVT_MOUSEWHEEL, self.onScroll)
		self.armorDetailList.EnableEditing(False)
		self.armorDetailList.EnableDragRowSize(False)
		self.armorDetailSizer.Add(self.armorDetailList, 1, wx.EXPAND)

		self.armorDetailList.CreateGrid(13, 2)
		self.armorDetailList.SetDefaultRowSize(24, resizeExistingRows=True)
		self.armorDetailList.SetColSize(0, 302)
		self.armorDetailList.SetColSize(1, 155 - 20)
		self.armorDetailList.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
		self.armorDetailList.SetColLabelSize(2)
		self.armorDetailList.SetRowLabelSize(1)

		self.armorMaterialsList = wx.ListCtrl(self.armorDetailPanel, style=wx.LC_REPORT
																	| wx.LC_VRULES
																	| wx.LC_HRULES
																	)
		self.armorMaterialsList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onMaterialDoubleClick)
		self.il = wx.ImageList(24, 24)
		self.armorMaterialsList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
		self.armorDetailSizer.Add(self.armorMaterialsList, 0.9, wx.EXPAND)


	def loadArmorDetailAll(self):
		self.root.Freeze()
		self.loadArmorDetail()
		width, height = self.equipmentPanel.GetSize()
		self.equipmentPanel.SetSize(width + 1, height + 1)
		self.equipmentPanel.SetSize(width, height)
		self.root.Thaw()


	def loadArmorDetail(self):
		self.armorDetailList.DeleteRows(0, self.armorDetailList.GetNumberRows())
		self.armorDetailList.AppendRows(13)

		self.il.RemoveAll()

		sql = """
			SELECT a.*, at.name, ast.name armorset_name
			FROM armor a
				JOIN armor_text at USING (id)
				JOIN armorset_text ast
					ON ast.id = a.armorset_id
					AND ast.lang_id = at.lang_id
			WHERE at.lang_id = :langId
			AND a.id = :armorId
		"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, ("en", self.currentlySelectedArmorID))
		data = data.fetchone()

		armor = a.Armor(data)

		noLog = wx.LogNull()
		try:
			self.armorMaleImageLabel.SetBitmap(wx.Bitmap(f"images/armor/male/{armor.name}.jpg"))
		except:
			self.armorMaleImageLabel.SetBitmap(wx.Bitmap(f"images/noImage.png"))
		try:
			self.armorFemaleImageLabel.SetBitmap(wx.Bitmap(f"images/armor/female/{armor.name}.jpg"))
		except:
			self.armorFemaleImageLabel.SetBitmap(wx.Bitmap(f"images/noImage.png"))
		del noLog
		
		armorDetail = {
			0:  str(armor.name),
			1:  str(armor.rarity),
			2:  str(armor.defenseBase),
			3:  str(armor.defenseMax),
			4:  str(armor.defenseAugmentedMax),
			5:  str(armor.slot1),
			6:  str(armor.slot2),
			7:  str(armor.slot3),
			8:  str(armor.fire),
			9:  str(armor.water),
			10:  str(armor.ice),
			11: str(armor.thunder),
			12: str(armor.dragon),
		}

		imageOffset = 85
		rarityIcon = self.il.Add(wx.Bitmap(f"images/armor/{armor.armorType}/rarity-24/{armor.rarity}"))

		self.armorDetailList.SetCellValue(0, 0, "Name")
		self.armorDetailList.SetCellValue(0, 1, armor.name)
		for num in range(1, 13):
			if num == 1:
				self.armorDetailList.SetCellRenderer(num, 0,
									cgr.ImageTextCellRenderer(
																rarityIcon,
																self.armorDetail[num][1],
																imageOffset=imageOffset,
															))
			else:
				self.armorDetailList.SetCellRenderer(num, 0,
									cgr.ImageTextCellRenderer(
										wx.Bitmap(self.armorDetail[num][0]), 
										self.armorDetail[num][1], 
										imageOffset=imageOffset
										))
			if num not in [5, 6, 7]:
				self.armorDetailList.SetCellValue(num, 1, armorDetail[num])
			else:
				if armorDetail[num] != "0":
					self.armorDetailList.SetCellRenderer(num, 1,
										cgr.ImageTextCellRenderer(
											wx.Bitmap(f"images/decoration-slots-24/{armorDetail[num]}.png"), 
											armorDetail[num], 
											imageOffset=30
											))
				else:
					self.armorDetailList.SetCellRenderer(num, 1, wx.grid.GridCellStringRenderer())
					self.armorDetailList.SetCellValue(num, 1, "-")

		self.loadArmorMaterials()


	def loadArmorMaterials(self):
		self.armorMaterialsList.ClearAll()

		sql = """
			SELECT i.id item_id, it.name item_name, i.icon_name item_icon_name,
				i.category item_category, i.icon_color item_icon_color, a.quantity
			FROM armor_recipe a
				JOIN item i
					ON a.item_id = i.id
				JOIN item_text it
					ON it.id = i.id
					AND it.lang_id = :langId
			WHERE it.lang_id = :langId
			AND a.armor_id= :armorId
			ORDER BY i.id
		"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, ("en", self.currentlySelectedArmorID))
		data = data.fetchall()

		if data != None:
			armorMaterials = []
			for row in data:
				armorMaterials.append(a.ArmorMaterial(row))

			info = wx.ListItem()
			info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
			info.Image = -1
			info.Align = wx.LIST_FORMAT_LEFT
			info.Text = "Req. Materials"
			self.armorMaterialsList.InsertColumn(0, info)
			self.armorMaterialsList.SetColumnWidth(0, self.armorDetailPanel.GetSize()[0] * 0.66)

			info = wx.ListItem()
			info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
			info.Image = -1
			info.Align = wx.LIST_FORMAT_CENTER
			info.Text = ""
			self.armorMaterialsList.InsertColumn(1, info)
			self.armorMaterialsList.SetColumnWidth(1, self.armorDetailPanel.GetSize()[0] * 0.34 - 40)

			self.armorMaterialsList.InsertColumn(2, info)
			self.armorMaterialsList.SetColumnWidth(2, 0)

			for material in armorMaterials:
				try:
					img = self.il.Add(wx.Bitmap(f"images/items-24/{material.iconName}{material.iconColor}.png"))
				except:
					img = self.il.Add(wx.Bitmap(f"images/unknown.png"))
				index = self.armorMaterialsList.InsertItem(self.armorMaterialsList.GetItemCount(), material.name, img)
				self.armorMaterialsList.SetItem(index, 1, str(material.quantity))
				self.armorMaterialsList.SetItem(index, 2, f"{material.id},{material.category}")


	def onArmorTypeSelection(self, event):
		"""
		When an armor rank button at the top of the screen is pressed the armor tree is reloaded with the new armor rank information.
		"""

		self.currentArmorTree = event.GetEventObject().GetName()
		self.loadArmorTree()


	def onArmorSelection(self, event):
		"""
		When a specific armor piece is selected in the tree, the detail view gets populated with the information from the database.
		"""

		if self.armorTree.GetCellValue(event.GetRow(), 12) != "":
			self.currentlySelectedArmorID = self.armorTree.GetCellValue(event.GetRow(), 12)
			self.currentlySelectedArmorSetID = self.armorTree.GetCellValue(event.GetRow(), 13)
			self.loadArmorDetailAll()


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
			self.armorDetailList.SetColSize(0, self.armorDetailPanel.GetSize()[0] * 0.66)
			self.armorDetailList.SetColSize(1, self.armorDetailPanel.GetSize()[0] * 0.34 - 20)
			self.armorMaterialsList.SetColumnWidth(0, self.armorDetailPanel.GetSize()[0] * 0.66)
			self.armorMaterialsList.SetColumnWidth(1, self.armorDetailPanel.GetSize()[0] * 0.34 - 40)
		except:
			pass


	def onScroll(self, event):
		"""
		On every scroll event in armorDetail, scrolls the parent ScrolledWindow by 3 in the appropriate direction.
		"""

		if event.GetWheelRotation() > 0:
			if self.armorDetailPanel.GetViewStart()[1] < 3:
				self.armorDetailPanel.Scroll(0, self.armorDetailPanel.GetViewStart()[1] + 1 * -1)
			else:
				self.armorDetailPanel.Scroll(0, self.armorDetailPanel.GetViewStart()[1] + 3 * -1)
		else:
			if self.armorDetailPanel.GetViewStart()[1] < 3:
				self.armorDetailPanel.Scroll(0, self.armorDetailPanel.GetViewStart()[1] + 1)
			else:
				self.armorDetailPanel.Scroll(0, self.armorDetailPanel.GetViewStart()[1] + 3)
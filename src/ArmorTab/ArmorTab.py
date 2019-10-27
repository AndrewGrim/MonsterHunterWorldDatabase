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
from Utilities import debug
import Links as link

wxTreeListItem = NewType('wxTreeListItem', None)
Armor = NewType('Armor', None)

class ArmorTab:

	def __init__(self, root, mainNotebook, link):
		self.root = root
		self.mainNotebook = mainNotebook
		self.link = link

		self.currentArmorTree = "HR"
		self.currentlySelectedArmorID = 159
		self.currentlySelectedArmorSetID = 39
		self.testIcon = wx.Bitmap("images/unknown.png", wx.BITMAP_TYPE_ANY) # REMOVE since youll be using specific icons

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

		self.armorDetail = {
			0: ["images/unknown.png", "Rarity"],
			1: ["images/weapon-detail-24/defense.png", "Defense"],
			2: ["images/weapon-detail-24/defense.png", "Defense Max"],
			3: ["images/weapon-detail-24/defense.png", "Defense Augmented Max"],
			4: ["images/weapon-detail-24/slots.png", "Slot I"],
			5: ["images/weapon-detail-24/slots.png", "Slot II"],
			6: ["images/weapon-detail-24/slots.png", "Slot III"],
			7: ["images/damage-types-24/fire.png", "Fire"],
			8: ["images/damage-types-24/water.png", "Water"],
			9: ["images/damage-types-24/ice.png", "Ice"],
			10: [ "images/damage-types-24/thunder.png", "Thunder"],
			11: [ "images/damage-types-24/dragon.png", "Dragon"],
		}

		self.armorSetDetail = {
			0: ["images/unknown.png", "Rarity"],
			1: ["images/weapon-detail-24/defense.png", "Defense"],
			2: ["images/weapon-detail-24/defense.png", "Defense Max"],
			3: ["images/weapon-detail-24/defense.png", "Defense Augmented Max"],
			4: ["images/decoration-slots-24/1.png", "Slots"],
			5: ["images/decoration-slots-24/2.png", "Slots"],
			6: ["images/decoration-slots-24/3.png", "Slots"],
			7: ["images/damage-types-24/fire.png", "Fire"],
			8: ["images/damage-types-24/water.png", "Water"],
			9: ["images/damage-types-24/ice.png", "Ice"],
			10: [ "images/damage-types-24/thunder.png", "Thunder"],
			11: [ "images/damage-types-24/dragon.png", "Dragon"],
		}

		self.initArmorTab()

		self.init = True


	def initArmorTab(self):
		self.armorPanel = wx.Panel(self.mainNotebook)
		self.mainNotebook.AddPage(self.armorPanel, "Armor")
		self.armorSizer = wx.BoxSizer(wx.HORIZONTAL)

		self.armorTreeSizer = wx.BoxSizer(wx.VERTICAL) 
		
		self.armorDetailedSizer = wx.BoxSizer(wx.VERTICAL)
		armorImage = wx.Bitmap("images/armor/male/Leather Headgear.png", wx.BITMAP_TYPE_ANY)
		self.armorMaleImageLabel = wx.StaticBitmap(self.armorPanel, bitmap=armorImage, size=(160, 160))
		self.armorFemaleImageLabel = wx.StaticBitmap(self.armorPanel, bitmap=armorImage, size=(160, 160))

		self.armorDetailsNotebook = wx.Notebook(self.armorPanel)
		self.armorDetailPanel = wx.Panel(self.armorDetailsNotebook)
		self.armorSetPanel = wx.Panel(self.armorDetailsNotebook)
		
		self.armorDetailSizer = wx.BoxSizer(wx.VERTICAL)
		self.armorDetailsNotebook.AddPage(self.armorDetailPanel, "Detail")
		self.armorDetailPanel.SetSizer(self.armorDetailSizer)

		self.armorSetSizer = wx.BoxSizer(wx.VERTICAL)
		self.armorDetailsNotebook.AddPage(self.armorSetPanel, "Armor Set Detail")
		self.armorSetPanel.SetSizer(self.armorSetSizer)
		
		self.armorDetailedImagesSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.armorDetailedImagesSizer.Add(self.armorMaleImageLabel, 1, wx.ALIGN_CENTER)
		self.armorDetailedImagesSizer.Add(self.armorFemaleImageLabel, 1, wx.ALIGN_CENTER)

		self.armorDetailedSizer.Add(self.armorDetailedImagesSizer, 1, wx.EXPAND)
		self.armorDetailedSizer.Add(self.armorDetailsNotebook, 3, wx.EXPAND)

		self.armorSizer.Add(self.armorTreeSizer, 1, wx.EXPAND)
		self.armorSizer.Add(self.armorDetailedSizer, 1, wx.EXPAND)

		self.armorPanel.SetSizer(self.armorSizer)
		
		self.initArmorButtons()
		self.initSearch()
		self.initArmorTree()
		self.loadArmorTree()
		self.initArmorDetailTab()
		self.initArmorSetDetails()
		self.armorDetailList.Bind(wx.EVT_SIZE, self.onSize)


	def initArmorButtons(self):
		self.lowRankButton = wx.Button(self.armorPanel, label="Low Rank", name="LR")
		self.lowRankButton.SetBitmap(wx.Bitmap("images/rank-stars-24/lr.png"))
		self.highRankButton = wx.Button(self.armorPanel, label="High Rank", name="HR")
		self.highRankButton.SetBitmap(wx.Bitmap("images/rank-stars-24/hr.png"))
		#self.masterRankButton = wx.Button(self.armorPanel, label="Master Rank", name="MR")
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
		self.search = wx.TextCtrl(self.armorPanel)
		self.search.SetHint("  search by name")
		self.search.Bind(wx.EVT_TEXT, self.onSearchTextEnter)
		self.armorButtonsSizer.Add(380, 0, 0)
		self.armorButtonsSizer.Add(self.search, 0, wx.TOP, 4)


	def onSearchTextEnter(self, event):
		self.loadArmorTree()


	def initArmorTree(self):
		self.armorTree = cgr.HeaderBitmapGrid(self.armorPanel)
		self.armorTree.EnableEditing(False)
		self.armorTree.EnableDragRowSize(False)
		self.armorTree.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.onArmorSelection)
		self.armorTreeSizer.Add(self.armorTree, 1, wx.EXPAND)
		self.init = False

		armorTreeColumns = {
			"Name": [324, wx.Bitmap("images/noImage24.png")],
			"Slot I": [32, wx.Bitmap("images/weapon-detail-24/slots.png")],
			"Slot II": [32, wx.Bitmap("images/weapon-detail-24/slots.png")],
			"Slot III": [32, wx.Bitmap("images/weapon-detail-24/slots.png")],
			"Defense": [32, wx.Bitmap("images/weapon-detail-24/defense.png")],
			"Defense Max": [32, wx.Bitmap("images/weapon-detail-24/defense.png")],
			"Defense Augmented Max": [32, wx.Bitmap("images/weapon-detail-24/defense.png")],
			"Fire": [32, wx.Bitmap("images/damage-types-24/fire.png")],
			"Water": [32, wx.Bitmap("images/damage-types-24/water.png")],
			"Ice": [32, wx.Bitmap("images/damage-types-24/ice.png")],
			"Thunder": [32, wx.Bitmap("images/damage-types-24/thunder.png")],
			"Dragon": [32, wx.Bitmap("images/damage-types-24/dragon.png")],
			"id": [0,  wx.Bitmap("images/noImage24.png")],
			"armorSetID": [0, wx.Bitmap("images/noImage24.png")],
		}

		self.armorTree.CreateGrid(1, 14)
		self.armorTree.SetDefaultRowSize(24, resizeExistingRows=True)
		self.armorTree.HideRowLabels()
		self.armorTree.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
		

		for col, (k, v) in enumerate(armorTreeColumns.items()):
			if col == 0:
				self.armorTree.SetColLabelRenderer(col, cgr.HeaderBitmapColLabelRenderer(v[1], k))
			else:
				self.armorTree.SetColLabelRenderer(col, cgr.HeaderBitmapColLabelRenderer(v[1], ""))
			self.armorTree.SetColSize(col, v[0])

		self.il = a.ArmorImageList()

	def loadArmorTree(self):
		try:
			pass
			self.armorTree.DeleteRows(0, self.armorTree.GetNumberRows())
		except:
			pass

		searchText = self.search.GetValue()

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
		self.populateArmorTree(armorList)


	def populateArmorTree(self, armorList: List[Armor]) -> None:
		"""
		armorList = The list of all the queried Armor objects, which contain the data pertaining to the individual armor pieces.
		"""

		armorSet = "" 
		row = 0
		for a in armorList:
			self.armorTree.AppendRows()
			if a.armorSetName != armorSet:
				img = wx.Bitmap(f"images/armor/armorset/rarity-24/{a.rarity}.png")
				if a.armorSetName[0:11] == "King Beetle":
					name = a.name.replace("King", "King / Queen")
					self.armorTree.SetCellRenderer(row, 0, cgr.ImageTextCellRenderer(
						img, f"        {name}", hAlign=wx.ALIGN_LEFT, imageOffset=150))
				else:
					self.armorTree.SetCellRenderer(row, 0, cgr.ImageTextCellRenderer(
						img, f"        {a.armorSetName}", hAlign=wx.ALIGN_LEFT, imageOffset=150))
				self.armorTree.AppendRows()
				row += 1
			armorSet = a.armorSetName
			img = wx.Bitmap(f"images/armor/{a.armorType}/rarity-24/{a.rarity}.png")
			if a.name[0:11] == "King Beetle":
				name = a.name.replace("King", "King / Queen")
				self.armorTree.SetCellRenderer(row, 0, cgr.ImageTextCellRenderer(
					img, f"┗ ━━━           {name}", hAlign=wx.ALIGN_LEFT, imageOffset=115))
			else:
				self.armorTree.SetCellRenderer(row, 0, cgr.ImageTextCellRenderer(
					img, f"┗ ━━━           {a.name}", hAlign=wx.ALIGN_LEFT, imageOffset=115))
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
					wx.Bitmap("images/decoration-slots-24/1.png")))
			if a.slot2 != 0:
				self.armorTree.SetCellRenderer(row, 2, cgr.ImageCellRenderer(
					wx.Bitmap("images/decoration-slots-24/2.png")))
			if a.slot3 != 0:
				self.armorTree.SetCellRenderer(row, 3,  cgr.ImageCellRenderer(
					wx.Bitmap("images/decoration-slots-24/3.png")))
			row += 1


	def initArmorDetailTab(self):
		self.armorDetailList = cgr.HeaderBitmapGrid(self.armorDetailPanel)
		self.armorDetailList.EnableEditing(False)
		self.armorDetailList.EnableDragRowSize(False)
		self.armorDetailSizer.Add(self.armorDetailList, 1, wx.EXPAND)

		self.armorDetailList.CreateGrid(12, 2)
		self.armorDetailList.SetDefaultRowSize(24, resizeExistingRows=True)
		self.armorDetailList.SetColSize(0, 302)
		self.armorDetailList.SetColSize(1, 155 - 20)
		self.armorDetailList.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
		self.armorDetailList.SetColLabelSize(2)
		self.armorDetailList.SetRowLabelSize(1)

		self.armorSkillList = wx.ListCtrl(self.armorDetailPanel, style=wx.LC_REPORT
																	| wx.LC_VRULES
																	| wx.LC_HRULES
																	)
		self.ilSkills = wx.ImageList(24, 24)
		self.armorSkillList.SetImageList(self.ilSkills, wx.IMAGE_LIST_SMALL)
		self.armorDetailSizer.Add(self.armorSkillList, 1, wx.EXPAND)

		self.armorMaterialsList = wx.ListCtrl(self.armorDetailPanel, style=wx.LC_REPORT
																	| wx.LC_VRULES
																	| wx.LC_HRULES
																	)
		self.armorMaterialsList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onMaterialDoubleClick)
		self.ilMats = wx.ImageList(24, 24)
		self.armorMaterialsList.SetImageList(self.ilMats, wx.IMAGE_LIST_SMALL)
		self.armorDetailSizer.Add(self.armorMaterialsList, 1, wx.EXPAND)

		self.loadArmorDetails()
		self.loadArmorSkills()
		self.loadArmorMaterials()


	def loadArmorDetails(self):
		if int(self.currentlySelectedArmorID) > 0:
			self.armorDetailList.DeleteRows(0, self.armorDetailList.GetNumberRows())
			self.armorDetailList.AppendRows(12)

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
				self.armorMaleImageLabel.SetBitmap(wx.Bitmap(f"images/armor/male/{armor.name}.png"))
			except:
				self.armorMaleImageLabel.SetBitmap(wx.Bitmap(f"images/noImage.png"))
			try:
				self.armorFemaleImageLabel.SetBitmap(wx.Bitmap(f"images/armor/female/{armor.name}.png"))
			except:
				self.armorFemaleImageLabel.SetBitmap(wx.Bitmap(f"images/noImage.png"))
			del noLog
			self.root.SetSize(self.root.windowWidth + 3, self.root.windowHeight)
			self.root.SetSize(self.root.windowWidth, self.root.windowHeight)
			
			armorDetail = {
				0:  str(armor.rarity),
				1:  str(armor.defenseBase),
				2:  str(armor.defenseMax),
				3:  str(armor.defenseAugmentedMax),
				4:  str(armor.slot1),
				5:  str(armor.slot2),
				6:  str(armor.slot3),
				7:  str(armor.fire),
				8:  str(armor.water),
				9:  str(armor.ice),
				10: str(armor.thunder),
				11: str(armor.dragon),
			}

			imageOffset = 85
			rarityIcon = self.il.il.GetBitmap(self.il.armorIcons[armor.armorType][armor.rarity])

			for num in range(12):
				if num == 0:
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
				if num not in [4, 5, 6]:
					self.armorDetailList.SetCellValue(num, 1, armorDetail[num])
				else:
					if armorDetail[num] != "0":
						self.armorDetailList.SetCellRenderer(num, 1,
											cgr.ImageTextCellRenderer(
												self.il.decorationSize[int(armorDetail[num])], 
												armorDetail[num], 
												imageOffset=30
												))
					else:
						self.armorDetailList.SetCellRenderer(num, 1, wx.grid.GridCellStringRenderer())
						self.armorDetailList.SetCellValue(num, 1, "-")


	def loadArmorSkills(self):
		if int(self.currentlySelectedArmorID) > 0:
			self.ilSkills.RemoveAll()

			sql = """
				SELECT s.id skill_id, stt.name skill_name, s.max_level skill_max_level, s.icon_color skill_icon_color,
					askill.level level
				FROM armor_skill askill
					JOIN armor a
						ON askill.armor_id = a.id
					JOIN skilltree s
						ON askill.skilltree_id = s.id
					JOIN skilltree_text stt
						ON askill.skilltree_id = stt.id
					WHERE stt.lang_id = :langId
						AND askill.armor_id = :armorId
					ORDER BY askill.skilltree_id ASC
			"""

			conn = sqlite3.Connection("mhw.db")
			data = conn.execute(sql, ("en", self.currentlySelectedArmorID))
			data = data.fetchall()

			if data != None:
				armorSkills = []
				for row in data:
					armorSkills.append(a.ArmorSkill(row))

				info = wx.ListItem()
				info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
				info.Image = -1
				info.Align = wx.LIST_FORMAT_LEFT
				info.Text = "Skills"
				self.armorSkillList.InsertColumn(0, info)

				info = wx.ListItem()
				info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
				info.Image = -1
				info.Align = wx.LIST_FORMAT_CENTER
				info.Text = ""
				self.armorSkillList.InsertColumn(1, info)

				self.armorSkillList.SetColumnWidth(0, 302)
				self.armorSkillList.SetColumnWidth(1, 155 - 21)

				for skill in armorSkills:
					lvl = skill.skillLevel * "◈"
					maxLvl = (skill.skillMaxLevel - skill.skillLevel) * "◇"
					if skill.iconColor is not None:
						img = self.ilSkills.Add(wx.Bitmap(f"images/skills-24/Skill{skill.iconColor}.png"))
						index = self.armorSkillList.InsertItem(self.armorSkillList.GetItemCount(), skill.name, img)
						self.armorSkillList.SetItem(index, 1, f"{lvl}{maxLvl}")


	def loadArmorMaterials(self):
		if int(self.currentlySelectedArmorID) > 0:
			self.ilMats.RemoveAll()

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
				self.armorMaterialsList.SetColumnWidth(0, 302)

				info = wx.ListItem()
				info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
				info.Image = -1
				info.Align = wx.LIST_FORMAT_CENTER
				info.Text = ""
				self.armorMaterialsList.InsertColumn(1, info)
				self.armorMaterialsList.SetColumnWidth(1, 155 - 21)

				self.armorMaterialsList.InsertColumn(2, info)
				self.armorMaterialsList.SetColumnWidth(2, 0)

				for material in armorMaterials:
					try:
						img = self.ilMats.Add(wx.Bitmap(f"images/materials-24/{material.iconName}{material.iconColor}.png"))
					except:
						img = self.ilMats.Add(wx.Bitmap(f"images/unknown.png"))
					index = self.armorMaterialsList.InsertItem(self.armorMaterialsList.GetItemCount(), material.name, img)
					self.armorMaterialsList.SetItem(index, 1, str(material.quantity))
					self.armorMaterialsList.SetItem(index, 2, f"{material.id},{material.category}")


	def initArmorSetDetails(self):
		self.armorSetDetailList = cgr.HeaderBitmapGrid(self.armorSetPanel)
		self.armorSetSizer.Add(self.armorSetDetailList, 1, wx.EXPAND)

		self.armorSetDetailList.CreateGrid(12, 2)
		self.armorSetDetailList.SetDefaultRowSize(24, resizeExistingRows=True)
		self.armorSetDetailList.SetColSize(0, 302)
		self.armorSetDetailList.SetColSize(1, 155 - 20)
		self.armorSetDetailList.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
		self.armorSetDetailList.SetColLabelSize(2)
		self.armorSetDetailList.SetRowLabelSize(1)

		self.armorSetSkillList = wx.ListCtrl(self.armorSetPanel, style=wx.LC_REPORT
																	| wx.LC_VRULES
																	| wx.LC_HRULES
																	)
		self.armorSetSkillList.SetImageList(self.ilSkills, wx.IMAGE_LIST_SMALL)
		self.armorSetSizer.Add(self.armorSetSkillList, 1, wx.EXPAND)

		self.armorSetMaterialList = wx.ListCtrl(self.armorSetPanel, style=wx.LC_REPORT
																	| wx.LC_VRULES
																	| wx.LC_HRULES
																	)
		self.armorSetMaterialList.SetImageList(self.ilMats, wx.IMAGE_LIST_SMALL)
		self.armorSetSizer.Add(self.armorSetMaterialList, 1, wx.EXPAND)

		self.loadArmorSetDetails()


	def loadArmorSetDetails(self):
		sql = """
			SELECT a.*, at.name, ast.name armorset_name
			FROM armor a
				JOIN armor_text at USING (id)
				JOIN armorset_text ast
					ON ast.id = a.armorset_id
					AND ast.lang_id = at.lang_id
			WHERE at.lang_id = :langId
			AND (a.armorset_id = :armorSetId)
		"""
		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, ("en", self.currentlySelectedArmorSetID))
		data = data.fetchall()

		armorSet = []
		for row in data:
			armorSet.append(a.Armor(row))

		defenseBase = 0
		defenseMax = 0
		defenseAugmentedMax = 0
		lvl1Slots = 0
		lvl2Slots = 0
		lvl3Slots = 0
		fire = 0
		water = 0
		ice = 0
		thunder = 0
		dragon = 0

		armorSetSkills = {}
		skillIcons = {}
		armorSetMaterials = {}
		materialIcons = {}
		armorSetBonus = False
		armorSetBonusID = 0

		for i, armor in enumerate(armorSet):
			defenseBase += armor.defenseBase
			defenseMax += armor.defenseMax
			defenseAugmentedMax += armor.defenseAugmentedMax

			if armor.slot1 == 1:
				lvl1Slots += 1
			if armor.slot2 == 1:
				lvl1Slots += 1
			if armor.slot3 == 1:
				lvl1Slots += 1

			if armor.slot1 == 2:
				lvl2Slots += 1
			if armor.slot2 == 2:
				lvl2Slots += 1
			if armor.slot3 == 2:
				lvl2Slots += 1

			if armor.slot1 == 3:
				lvl3Slots += 1
			if armor.slot2 == 3:
				lvl3Slots += 1
			if armor.slot3 == 3:
				lvl3Slots += 1

			fire += armor.fire
			water += armor.water
			ice += armor.ice
			thunder += armor.thunder
			dragon += armor.dragon

			if armor.armorSetBonusID != None:
				armorSetBonus = True
				armorSetBonusID = armor.armorSetBonusID

			sql = """
				SELECT s.id skill_id, stt.name skill_name, s.max_level skill_max_level, s.icon_color skill_icon_color,
					askill.level level
				FROM armor_skill askill
					JOIN armor a
						ON askill.armor_id = a.id
					JOIN skilltree s
						ON askill.skilltree_id = s.id
					JOIN skilltree_text stt
						ON askill.skilltree_id = stt.id
					WHERE stt.lang_id = :langId
						AND askill.armor_id = :armorId
					ORDER BY askill.skilltree_id ASC
			"""

			conn = sqlite3.Connection("mhw.db")
			data = conn.execute(sql, ("en", armor.id))
			data = data.fetchall()

			armorPieceSkills = {}
			if data != None:
				armorSkills = []
				for row in data:
					armorSkills.append(a.ArmorSkill(row))

				for skill in armorSkills:
					armorPieceSkills[skill.name] = [0, skill.skillMaxLevel]
					if skill.iconColor is not None:
						skillIcons[skill.name] = f"images/skills-24/Skill{skill.iconColor}.png"

				for skill in armorSkills:
					armorPieceSkills[skill.name][0] += skill.skillLevel

				for k, v in armorPieceSkills.items():
					if k in armorSetSkills.keys():
						armorSetSkills[k][0] += v[0]
					else:
						armorSetSkills[k] = [v[0], v[1]]

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
			data = conn.execute(sql, ("en", armor.id))
			data = data.fetchall()

			armorPieceMaterials = {}
			if data != None:
				armorMaterials = []
				for row in data:
					armorMaterials.append(a.ArmorMaterial(row))

				for mat in armorMaterials:
					armorPieceMaterials[mat.name] = 0
					materialIcons[mat.name] = f"images/materials-24/{mat.iconName}{mat.iconColor}.png"

				for mat in armorMaterials:
					armorPieceMaterials[mat.name] += mat.quantity

				for k, v in armorPieceMaterials.items():
					if k in armorSetMaterials.keys():
						armorSetMaterials[k] += v
					else:
						armorSetMaterials[k] = v

		if int(self.currentlySelectedArmorID) > 0:
			self.armorSetDetailList.DeleteRows(0, self.armorSetDetailList.GetNumberRows())
			self.armorSetDetailList.AppendRows(12)
			
			armorDetail = {
				0:  str(armor.rarity),
				1:  str(defenseBase),
				2:  str(defenseMax),
				3:  str(defenseAugmentedMax),
				4:  str(lvl1Slots),
				5:  str(lvl2Slots),
				6:  str(lvl3Slots),
				7:  str(fire),
				8:  str(water),
				9:  str(ice),
				10: str(thunder),
				11: str(dragon),
			}

			imageOffset = 85
			rarityIcon = self.il.il.GetBitmap(self.il.armorIcons["armorset"][armor.rarity])

			for num in range(12):
				if num == 0:
					self.armorSetDetailList.SetCellRenderer(num, 0,
										cgr.ImageTextCellRenderer(
																	rarityIcon,
																	self.armorSetDetail[num][1],
																	imageOffset=imageOffset,
																))
				else:
					self.armorSetDetailList.SetCellRenderer(num, 0,
										cgr.ImageTextCellRenderer(
											wx.Bitmap(self.armorSetDetail[num][0]), 
											self.armorSetDetail[num][1], 
											imageOffset=imageOffset
											))
				if num not in [4, 5, 6]:
					self.armorSetDetailList.SetCellValue(num, 1, armorDetail[num])
				else:
					if armorDetail[num] != "0":
						self.armorSetDetailList.SetCellRenderer(num, 1, wx.grid.GridCellStringRenderer())
						self.armorSetDetailList.SetCellValue(num, 1, armorDetail[num])
					else:
						self.armorSetDetailList.SetCellRenderer(num, 1, wx.grid.GridCellStringRenderer())
						self.armorSetDetailList.SetCellValue(num, 1, "-")

			info = wx.ListItem()
			info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
			info.Image = -1
			info.Align = wx.LIST_FORMAT_LEFT
			info.Text = "Skills"
			self.armorSetSkillList.InsertColumn(0, info)

			info = wx.ListItem()
			info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
			info.Image = -1
			info.Align = wx.LIST_FORMAT_CENTER
			info.Text = ""
			self.armorSetSkillList.InsertColumn(1, info)

			self.armorSetSkillList.SetColumnWidth(0, 302)
			self.armorSetSkillList.SetColumnWidth(1, 155 - 22)

			for k, v in armorSetSkills.items():
				lvl = v[0] * "◈"
				maxLvl = (v[1] - v[0]) * "◇"
				img = self.ilSkills.Add(wx.Bitmap(skillIcons[k]))
				index = self.armorSetSkillList.InsertItem(self.armorSetSkillList.GetItemCount(), k, img)
				self.armorSetSkillList.SetItem(index, 1, f"{lvl}{maxLvl}")
			if armorSetBonus:
				sql = """
					SELECT st.id as skilltree_id, stt.name as skilltree_name, st.max_level skilltree_max_level,
						st.icon_color as skilltree_icon_color,
						abs.setbonus_id as id, abt.name, abs.required
					FROM armorset_bonus_skill abs
						JOIN armorset_bonus_text abt
							ON abt.id = abs.setbonus_id
						JOIN skilltree st
							ON abs.skilltree_id = st.id
						JOIN skilltree_text stt
							ON abs.skilltree_id = stt.id
							AND abt.lang_id = stt.lang_id
					WHERE abt.lang_id = :langId
					AND abs.setbonus_id= :setBonusId
				"""

				conn = sqlite3.Connection("mhw.db")
				data = conn.execute(sql, ("en", armorSetBonusID))
				data = data.fetchall()

				setBonuses = []
				if data != None:
					for row in data:
						setBonuses.append(a.ArmorSetBonus(row))
					for b in setBonuses:
						img = self.ilSkills.Add(wx.Bitmap(f"images/skills-24/{util.setBonusColors[b.setBonusName]}"))
						index = self.armorSetSkillList.InsertItem(
							self.armorSetSkillList.GetItemCount(), f"{b.name} / {b.setBonusName}",
							img)
						self.armorSetSkillList.SetItem(index, 1, "Req. " + str(b.setBonusAmtRequired))

			info = wx.ListItem()
			info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
			info.Image = -1
			info.Align = wx.LIST_FORMAT_LEFT
			info.Text = "Req. Materials"
			self.armorSetMaterialList.InsertColumn(0, info)

			info = wx.ListItem()
			info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
			info.Image = -1
			info.Align = wx.LIST_FORMAT_CENTER
			info.Text = ""
			self.armorSetMaterialList.InsertColumn(1, info)

			self.armorSetMaterialList.SetColumnWidth(0, 302)
			self.armorSetMaterialList.SetColumnWidth(1, 155 - 22)

			for k, v in armorSetMaterials.items():
				try:
					img = self.ilMats.Add(wx.Bitmap(materialIcons[k]))
				except:
					img = self.ilMats.Add(wx.Bitmap("images/unknown.png"))
				index = self.armorSetMaterialList.InsertItem(self.armorSetMaterialList.GetItemCount(), k, img)
				self.armorSetMaterialList.SetItem(index, 1, str(v))


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

		if self.init:
			self.currentlySelectedArmorID = self.armorTree.GetCellValue(event.GetRow(), 12)
			self.currentlySelectedArmorSetID = self.armorTree.GetCellValue(event.GetRow(), 13)

			if self.currentlySelectedArmorID != "":
				self.armorDetailList.ClearGrid()
				self.armorSkillList.ClearAll()
				self.armorMaterialsList.ClearAll()
				self.armorSetDetailList.ClearGrid()
				self.armorSetSkillList.ClearAll()
				self.armorSetMaterialList.ClearAll()
			
				self.loadArmorDetails()
				self.loadArmorSkills()
				self.loadArmorMaterials()
				self.loadArmorSetDetails()
				width, height = self.armorDetailPanel.GetSize()
				self.armorDetailPanel.SetSize(width + 1, height + 1)
				self.armorDetailPanel.SetSize(width, height)
				width, height = self.armorSetPanel.GetSize()
				self.armorSetPanel.SetSize(width + 1, height + 1)
				self.armorSetPanel.SetSize(width, height)


	def onMaterialDoubleClick(self, event):
		materialInfo = self.armorMaterialsList.GetItemText(event.GetEventObject().GetFirstSelected(), 2)
		materialInfo = materialInfo.split(",")
		self.link.event = True
		self.link.eventType = "item"
		self.link.item =  link.ItemLink(materialInfo)
		self.root.followLink()
		self.link.reset()


	def onSize(self, event):
		"""
		When the application window is resized some columns's width gets readjusted.
		"""
		self.armorDetailList.SetColSize(0, self.armorDetailPanel.GetSize()[0] * 0.66)
		self.armorDetailList.SetColSize(1, self.armorDetailPanel.GetSize()[0] * 0.34 - 20)
		self.armorSkillList.SetColumnWidth(0, self.armorDetailPanel.GetSize()[0] * 0.66)
		self.armorSkillList.SetColumnWidth(1, self.armorDetailPanel.GetSize()[0] * 0.34 - 21)
		self.armorMaterialsList.SetColumnWidth(0, self.armorDetailPanel.GetSize()[0] * 0.66)
		self.armorMaterialsList.SetColumnWidth(1, self.armorDetailPanel.GetSize()[0] * 0.34 - 21)
		self.armorSetDetailList.SetColSize(0, self.armorSetPanel.GetSize()[0] * 0.66)
		self.armorSetDetailList.SetColSize(1, self.armorSetPanel.GetSize()[0] * 0.34 - 20)
		self.armorSetSkillList.SetColumnWidth(0, self.armorSetPanel.GetSize()[0] * 0.66)
		self.armorSetSkillList.SetColumnWidth(1, self.armorSetPanel.GetSize()[0] * 0.34 - 21)
		self.armorSetMaterialList.SetColumnWidth(0, self.armorSetPanel.GetSize()[0] * 0.66)
		self.armorSetMaterialList.SetColumnWidth(1, self.armorSetPanel.GetSize()[0] * 0.34 - 21)
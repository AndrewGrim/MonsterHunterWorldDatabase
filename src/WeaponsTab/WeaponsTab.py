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
import Links as link
import WeaponsTab as w
from Debug.debug import debug

wxTreeListItem = NewType('wxTreeListItem', None)

class WeaponsTab:

	def __init__(self, root, mainNotebook, link):
		self.root = root
		self.mainNotebook = mainNotebook
		self.link = link
		self.c = wx.ColourDatabase()
		self.skip = False
		self.init = True

		self.currentlySelectedWeaponID = 1
		self.currentWeaponTree = "great-sword"
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

		self.weaponDetailIcons = {
			"Attack": "images/weapon-detail-24/attack.png",
			"Attack (True)": "images/weapon-detail-24/attack.png",
			"Affinity": "images/weapon-detail-24/affinity.png",
			"Element I": "images/weapon-detail-24/element.png",
			"Element II": "images/weapon-detail-24/element.png",
			"Slot I": "images/weapon-detail-24/slots.png",
			"Slot II": "images/weapon-detail-24/slots.png",
			"Slot III": "images/weapon-detail-24/slots.png",
			"Elderseal": "images/weapon-detail-24/elderseal.png",
			"Defense": "images/weapon-detail-24/defense.png",
		}

		self.weaponRowNumbers = {
			"great-sword": 12,
			"long-sword": 12,
			"sword-and-shield": 12,
			"dual-blades": 12,
			"hammer": 12,
			"hunting-horn": 15,
			"lance": 12,
			"gunlance": 13,
			"switch-axe": 13,
			"charge-blade": 13,
			"insect-glaive": 13,
			"light-bowgun": 14,
			"heavy-bowgun": 14,
			"bow": 18,
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

		self.noteColors = {
			"W": "White",
			"R": "Red",
			"C": "Cyan",
			"B": "Blue",
			"G": "Green",
			"O": "Orange",
			"Y": "Yellow",
			"P": "Purple",
		}

		self.initWeaponsTab()


	def initWeaponsTab(self):
		self.weaponPanel = wx.Panel(self.mainNotebook)
		self.mainNotebook.AddPage(self.weaponPanel, "Weapons")
		self.weaponsSizer = wx.BoxSizer(wx.HORIZONTAL)

		self.weaponTreeSizer = wx.BoxSizer(wx.VERTICAL) 
		
		self.weaponsDetailedSizer = wx.BoxSizer(wx.VERTICAL)
		self.weaponImage = wx.Bitmap("images/weapons/great-sword/Buster Sword I.jpg", wx.BITMAP_TYPE_ANY)
		self.weaponImageLabel = wx.StaticBitmap(self.weaponPanel, bitmap=self.weaponImage, size=(230, 230))
		self.weaponImageLabel.SetBackgroundColour((0, 0, 0))

		self.weaponDetailsNotebook = wx.Notebook(self.weaponPanel)
		il = wx.ImageList(24, 24)
		self.ammo = il.Add(wx.Bitmap("images/items-24/AmmoWhite.png"))
		self.notes = il.Add(wx.Bitmap("images/weapon-detail-24/notes.png"))
		self.weaponDetailsNotebook.AssignImageList(il)
		self.weaponDetailPanel = wx.ScrolledWindow(self.weaponDetailsNotebook)
		self.weaponMelodiesPanel = wx.Panel(self.weaponDetailsNotebook)
		self.weaponAmmoPanel = wx.Panel(self.weaponDetailsNotebook)
		
		self.weaponDetailSizer = wx.BoxSizer(wx.VERTICAL)
		self.weaponDetailsNotebook.AddPage(self.weaponDetailPanel, "Detail")
		self.weaponDetailPanel.SetSizer(self.weaponDetailSizer)

		self.weaponMelodiesSizer = wx.BoxSizer(wx.VERTICAL)
		self.weaponDetailsNotebook.AddPage(self.weaponMelodiesPanel, "Melodies")
		self.weaponMelodiesPanel.SetSizer(self.weaponMelodiesSizer)

		self.weaponAmmoSizer = wx.BoxSizer(wx.VERTICAL)
		self.weaponDetailsNotebook.AddPage(self.weaponAmmoPanel, "Ammo")
		self.weaponAmmoPanel.SetSizer(self.weaponAmmoSizer)
		
		self.weaponsDetailedSizer.Add(self.weaponImageLabel, 1, wx.EXPAND)
		self.weaponsDetailedSizer.Add(self.weaponDetailsNotebook, 3, wx.EXPAND)

		self.weaponsSizer.Add(self.weaponTreeSizer, 0, wx.EXPAND)
		self.weaponsSizer.Add(self.weaponsDetailedSizer, 1, wx.EXPAND)

		self.weaponPanel.SetSizer(self.weaponsSizer)
		
		self.initWeaponButtons()
		self.initSearch()
		self.initweaponTree()
		self.initWeaponDetailTab()

		self.weaponDetailList.Bind(wx.EVT_SIZE, self.onSize)

		self.weaponDetailPanel.SetScrollRate(20, 20)


	def initWeaponButtons(self):
		weapons = ["great-sword", "long-sword", "sword-and-shield", "dual-blades", "hammer",
					"hunting-horn", "lance", "gunlance", "switch-axe", "charge-blade",
					"insect-glaive", "light-bowgun", "heavy-bowgun", "bow"
		]

		self.weaponButtonsSizer = wx.BoxSizer(wx.HORIZONTAL)
		for i, item in enumerate(weapons):
			button = wx.BitmapButton(self.weaponPanel, bitmap=wx.Bitmap(f"images/weapons/{item}/rarity-24/0.png"), name=item)
			self.weaponButtonsSizer.Add(button)
			button.Bind(wx.EVT_BUTTON, self.onWeaponTypeSelection)

		self.weaponTreeSizer.Add(self.weaponButtonsSizer)


	def initSearch(self):
		self.search = wx.TextCtrl(self.weaponPanel, style=wx.TE_PROCESS_ENTER, size=(123, -1))
		self.search.SetHint("  search by name")
		self.search.Bind(wx.EVT_TEXT_ENTER, self.onSearchTextEnter)
		self.weaponButtonsSizer.Add(200, 0, 0)
		self.weaponButtonsSizer.Add(self.search, 0, wx.ALIGN_CENTER_VERTICAL)


	def onSearchTextEnter(self, event):
		self.loadWeaponTree()


	def initweaponTree(self):
		self.weaponTree = cgr.HeaderBitmapGrid(self.weaponPanel)
		self.weaponTree.EnableEditing(False)
		self.weaponTree.EnableDragRowSize(False)
		self.weaponTree.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.onWeaponSelection)
		self.weaponTreeSizer.Add(self.weaponTree, 1, wx.EXPAND)

		weaponTreeColumns = {
			"Name": [472, None],
			"Attack": [35, wx.Bitmap("images/weapon-detail-24/attack.png")],
			"Element": [75, wx.Bitmap("images/weapon-detail-24/element.png")],
			"Affinity": [35, wx.Bitmap("images/weapon-detail-24/affinity.png")],
			"Defense": [35, wx.Bitmap("images/weapon-detail-24/defense.png")],
			"Slot I": [29, wx.Bitmap("images/weapon-detail-24/slots.png")],
			"Slot II": [29, wx.Bitmap("images/weapon-detail-24/slots.png")],
			"Slot III": [29, wx.Bitmap("images/weapon-detail-24/slots.png")],
			"Sharpness": [171, None],
			"id": [0,  wx.Bitmap("images/noImage24.png")],
		}

		self.weaponTree.CreateGrid(1, 10)
		self.weaponTree.SetDefaultRowSize(27, resizeExistingRows=True)
		self.weaponTree.HideRowLabels()
		self.weaponTree.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
		

		for col, (k, v) in enumerate(weaponTreeColumns.items()):
			if v[1] == None:
				self.weaponTree.SetColLabelValue(col, k)
			else:
				self.weaponTree.SetColLabelRenderer(col, cgr.HeaderBitmapColLabelRenderer(v[1], ""))
			self.weaponTree.SetColSize(col, v[0])

		self.loadWeaponTree()


	def loadWeaponTree(self):
		self.init = True
		try:
			self.weaponTree.DeleteRows(0, self.weaponTree.GetNumberRows())
		except:
			pass

		searchText = self.search.GetValue().replace("'", "''")

		if len(searchText) == 0 or searchText == " ":
			sql = """
				SELECT w.id, w.weapon_type, w.category, w.rarity, w.attack, w.attack_true, w.affinity, w.defense, w.slot_1, w.slot_2, w.slot_3, w.element1, w.element1_attack,
					w.element2, w.element2_attack, w.element_hidden, w.sharpness, w.sharpness_maxed, w.previous_weapon_id, w.craftable, w.kinsect_bonus,
					w.elderseal, w.phial, w.phial_power, w.shelling, w.shelling_level, w.coating_close, w.coating_power, w.coating_poison, w.coating_paralysis, w.coating_sleep, w.coating_blast,
					w.notes, wa.special_ammo, wa.deviation, wt.name
				FROM weapon w
					JOIN weapon_text wt USING (id)
					LEFT JOIN weapon_ammo wa ON w.ammo_id = wa.id
				WHERE wt.lang_id = :langId
					AND w.weapon_type = :weaponType
				ORDER BY w.id ASC
			"""
		else:
			sql = f"""
				SELECT w.id, w.weapon_type, w.category, w.rarity, w.attack, w.attack_true, w.affinity, w.defense, w.slot_1, w.slot_2, w.slot_3, w.element1, w.element1_attack,
					w.element2, w.element2_attack, w.element_hidden, w.sharpness, w.sharpness_maxed, w.previous_weapon_id, w.craftable, w.kinsect_bonus,
					w.elderseal, w.phial, w.phial_power, w.shelling, w.shelling_level, w.coating_close, w.coating_power, w.coating_poison, w.coating_paralysis, w.coating_sleep, w.coating_blast,
					w.notes, wa.special_ammo, wa.deviation, wt.name
				FROM weapon w
					JOIN weapon_text wt USING (id)
					LEFT JOIN weapon_ammo wa ON w.ammo_id = wa.id
				WHERE wt.lang_id = :langId
					AND w.weapon_type = :weaponType
					AND wt.name LIKE '%{searchText}%'
				ORDER BY w.id ASC
			"""

		conn = sqlite3.connect("mhw.db")
		data = conn.execute(sql, ("en", self.currentWeaponTree, ))
		data = data.fetchall()

		weaponNodes = {}

		self.offset = {
			0: 0,
			1: 223,
			2: 198,
			3: 176,
			4: 151,
			5: 127,
			6: 103,
			7: 78,
			8: 55,
			9: 30,
			10: 0,
			11: -25,
			12: -50,
			13: -75,
		}

		weapons = []
		for row in data:
			weapons.append(w.Weapon(row))

		normal = True
		kulve = True
		for wep in weapons:
			if len(searchText) != 0:
				self.populateweaponTree(1, wep, None)
			elif wep.category != "Kulve":
				if normal:
					normal = False
					self.weaponTree.AppendRows()
					self.weaponTree.SetCellValue(0, 0, "Normal")
					self.weaponTree.SetCellFont(0, 0, self.weaponTree.GetCellFont(0, 0).Bold())
					for i in range(9):
						self.weaponTree.SetCellBackgroundColour(0, i, util.hexToRGB("#C2BFBF"))
				if wep.previous_weapon_id == None:
					self.populateweaponTree(1, wep, weaponNodes)
				else:
					self.populateweaponTree(weaponNodes[wep.previous_weapon_id], wep, weaponNodes)
			else:
				if kulve:
					kulve = False
					self.weaponTree.AppendRows()
					row = self.weaponTree.GetNumberRows() - 1
					self.weaponTree.SetCellValue(row, 0, "Kulve")
					self.weaponTree.SetCellFont(row, 0, self.weaponTree.GetCellFont(row, 0).Bold())
					for i in range(9):
						self.weaponTree.SetCellBackgroundColour(row, i, util.hexToRGB("#EFCD1E"))
				self.populateweaponTree(1, wep, weaponNodes)

		self.init = False


	def populateweaponTree(self, indent:int, wep: Tuple[str], weaponNodes: Dict[int, int]) -> None:
		self.weaponTree.AppendRows()
		row = self.weaponTree.GetNumberRows() - 1

		if bool(wep.craftable):
			if self.root.pref.unicodeSymbols:
				name = str(wep.name) + " 🔨" 
			else:
				name = str(wep.name) + " (Craftable)"
		else:
			name = str(wep.name)

		padding = "        " * indent
		staticPadding = " " * 8
		img = wx.Bitmap(f"images/weapons/{self.currentWeaponTree}/rarity-24/{wep.rarity}.png")
		self.weaponTree.SetCellRenderer(row, 0, cgr.ImageTextCellRenderer(
						img, f"{padding}{name}", hAlign=wx.ALIGN_LEFT, imageOffset=self.offset[indent]))		
		self.weaponTree.SetCellValue(row, 0, name)
		self.weaponTree.SetCellValue(row, 1, str(wep.attack))

		if wep.element_hidden == 0 and wep.element1_attack == None:
			element = ""
		elif wep.element_hidden == 1:
			element = "(" + str(wep.element1_attack) + ")"
		else:
			element = str(wep.element1_attack)
		try:
			img = wx.Bitmap(f"images/damage-types-24/{wep.element1.lower()}.png")
			self.weaponTree.SetCellRenderer(row, 2, cgr.ImageTextCellRenderer(
						img, f"{staticPadding}{element}", imageOffset=15))
		except:
			pass
		if wep.element2_attack != None:
			img = wx.Bitmap(f"images/damage-types-24/ice-blast.png")
			self.weaponTree.SetCellRenderer(row, 2, cgr.ImageTextCellRenderer(
						img, f"{staticPadding}{wep.element2_attack}", imageOffset=15))
		if wep.affinity == 0:
			affinity = ""
		else:
			if wep.affinity > 0:
				affinity = f"+{wep.affinity}%"
			else:
				affinity = f"{wep.affinity}%"
		if wep.defense == 0:
			defense = ""
		else:
			defense = "+" + str(wep.defense)

		self.weaponTree.SetCellValue(row, 2, element)
		self.weaponTree.SetCellValue(row, 3, affinity)
		self.weaponTree.SetCellValue(row, 4, defense)

		if wep.slot_1 != 0:
			img = wx.Bitmap(f"images/decoration-slots-24/{wep.slot_1}.png")
			self.weaponTree.SetCellRenderer(row, 5, cgr.ImageCellRenderer(img))
		if wep.slot_2 != 0:
			img = wx.Bitmap(f"images/decoration-slots-24/{wep.slot_2}.png")
			self.weaponTree.SetCellRenderer(row, 6, cgr.ImageCellRenderer(img))
		if wep.slot_3 != 0:
			img = wx.Bitmap(f"images/decoration-slots-24/{wep.slot_3}.png")
			self.weaponTree.SetCellRenderer(row, 7, cgr.ImageCellRenderer(img))
		
		if self.currentWeaponTree not in ["light-bowgun", "heavy-bowgun", "bow"]:
			weaponName = wep.name.replace('"', "'") + ".png"
			img = wx.Bitmap(f"images/weapons/{self.currentWeaponTree}/sharpness-168-24/{weaponName}")
			self.weaponTree.SetCellRenderer(row, 8, cgr.ImageCellRenderer(img))
		
		self.weaponTree.SetCellValue(row, 9, str(wep.id))

		if len(self.search.GetValue()) == 0:
			weaponNodes[wep.id] = indent + 1


	def initWeaponDetailTab(self):
		self.weaponDetailList = cgr.HeaderBitmapGrid(self.weaponDetailPanel)
		self.weaponDetailList.Bind(wx.EVT_MOUSEWHEEL, self.onScroll)
		self.weaponDetailList.EnableEditing(False)
		self.weaponDetailList.EnableDragRowSize(False)
		self.weaponDetailSizer.Add(self.weaponDetailList, 1, wx.EXPAND)

		self.weaponDetailList.CreateGrid(18, 2)
		self.weaponDetailList.SetDefaultRowSize(24, resizeExistingRows=True)
		self.weaponDetailList.SetColSize(0, 302)
		self.weaponDetailList.SetColSize(1, 155 - 20)
		self.weaponDetailList.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
		self.weaponDetailList.SetColLabelSize(0)
		self.weaponDetailList.SetRowLabelSize(0)

		self.weaponSharpnessTable = cgr.HeaderBitmapGrid(self.weaponDetailPanel)
		self.weaponSharpnessTable.Bind(wx.EVT_MOUSEWHEEL, self.onScroll)
		self.weaponSharpnessTable.CreateGrid(6, 7)
		self.weaponSharpnessTable.EnableEditing(False)
		self.weaponSharpnessTable.EnableDragRowSize(False)
		self.weaponDetailSizer.Add(self.weaponSharpnessTable, 1, wx.EXPAND|wx.TOP, 5)

		self.materialsRequiredList = wx.ListCtrl(self.weaponDetailPanel, style=wx.LC_REPORT
																			| wx.LC_VRULES
																			| wx.LC_HRULES
																			)
		self.materialsRequiredList.Bind(wx.EVT_MOUSEWHEEL, self.onScroll)
		self.materialsRequiredList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onMaterialDoubleClick)
		self.ilMats = wx.ImageList(24, 24)
		self.materialsRequiredList.SetImageList(self.ilMats, wx.IMAGE_LIST_SMALL)
		self.weaponDetailSizer.Add(self.materialsRequiredList, 1, wx.EXPAND|wx.TOP, 5)

		self.weaponMelodiesList = cgr.HeaderBitmapGrid(self.weaponMelodiesPanel)
		self.weaponMelodiesList.EnableEditing(False)
		self.weaponMelodiesList.EnableDragRowSize(False)
		self.weaponMelodiesList.CreateGrid(15, 7)

		self.weaponMelodiesList.SetColLabelSize(0)
		self.weaponMelodiesList.SetRowLabelSize(0)
		self.weaponMelodiesList.SetColLabelValue(0, "")
		self.weaponMelodiesList.SetColLabelValue(1, "")
		self.weaponMelodiesList.SetColLabelValue(2, "")
		self.weaponMelodiesList.SetColLabelValue(3, "")
		self.weaponMelodiesList.SetColLabelValue(4, "Duration")
		self.weaponMelodiesList.SetColLabelValue(5, "Extension")
		self.weaponMelodiesList.SetColLabelValue(6, "Effects")

		self.weaponMelodiesList.SetColSize(0, 26)
		self.weaponMelodiesList.SetColSize(1, 26)
		self.weaponMelodiesList.SetColSize(2, 26)
		self.weaponMelodiesList.SetColSize(3, 26)
		self.weaponMelodiesList.SetColSize(4, 55)
		self.weaponMelodiesList.SetColSize(5, 75)

		self.weaponMelodiesList.SetDefaultRowSize(32, resizeExistingRows=True)
		self.weaponMelodiesList.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
		self.weaponMelodiesSizer.Add(self.weaponMelodiesList, 1, wx.EXPAND)

		self.weaponAmmoList = wx.ListCtrl(self.weaponAmmoPanel, style=wx.LC_REPORT
																	#| wx.LC_NO_HEADER
																	| wx.LC_VRULES
																	| wx.LC_HRULES
																	)
		self.ilAmmo = wx.ImageList(24, 24)
		self.weaponAmmoList.SetImageList(self.ilAmmo, wx.IMAGE_LIST_SMALL)
		self.weaponAmmoSizer.Add(self.weaponAmmoList, 1, wx.EXPAND)

		self.loadWeaponDetailAll()

		if self.weaponSharpnessTable.IsShown():
				self.weaponSharpnessTable.Hide()
				self.weaponDetailSizer.Remove(1)
		if not self.weaponSharpnessTable.IsShown():
			self.weaponSharpnessTable.Show()
			self.weaponDetailSizer.Insert(1, self.weaponSharpnessTable, 0.5, wx.EXPAND|wx.TOP, 5)
			self.weaponDetailSizer.SetDimension(self.weaponDetailPanel.GetPosition(), self.weaponDetailPanel.GetSize())


	def loadWeaponDetailAll(self):
		self.root.Freeze()
		self.loadWeaponDetail()
		width, height = self.weaponPanel.GetSize()
		self.weaponPanel.SetSize(width + 5, height + 20)
		self.weaponPanel.SetSize(width, height)
		self.root.Thaw()


	def loadWeaponDetail(self):
		self.weaponDetailList.DeleteRows(0, self.weaponDetailList.GetNumberRows())
		self.weaponDetailList.AppendRows(self.weaponRowNumbers[self.currentWeaponTree])

		sql = """
			SELECT w.id, w.weapon_type, w.category, w.rarity, w.attack, w.attack_true, w.affinity, w.defense, w.slot_1, w.slot_2, w.slot_3, w.element1, w.element1_attack,
				w.element2, w.element2_attack, w.element_hidden, w.sharpness, w.sharpness_maxed, w.previous_weapon_id, w.craftable, w.kinsect_bonus,
				w.elderseal, w.phial, w.phial_power, w.shelling, w.shelling_level, w.coating_close, w.coating_power, w.coating_poison, w.coating_paralysis, w.coating_sleep, w.coating_blast,
				w.notes, wa.special_ammo, wa.deviation, wt.name
			FROM weapon w
				JOIN weapon_text wt USING (id)
				LEFT OUTER JOIN weapon_ammo wa ON w.ammo_id = wa.id
			WHERE w.id = :weaponId
			AND wt.lang_id = :langId
		"""

		conn = sqlite3.connect("mhw.db")
		data = conn.execute(sql, (self.currentlySelectedWeaponID, "en"))
		data = data.fetchone()

		wep = w.Weapon(data)

		weaponName = wep.name.replace('"', "'")
		weaponType = self.currentWeaponTree
		placeholder = "noImage"
		if os.path.isfile(f"images/weapons/{weaponType}/{weaponName}.jpg"):
			self.weaponImage = wx.Bitmap(f"images/weapons/{weaponType}/{weaponName}.jpg", wx.BITMAP_TYPE_ANY)
		else:
			self.weaponImage = wx.Bitmap(f"images/{placeholder}.png", wx.BITMAP_TYPE_ANY)
		self.weaponImageLabel.SetBitmap(self.weaponImage)

		affinity = "-"
		if wep.affinity != 0:
			affinity = f"{wep.affinity}%"

		element1 = "-"
		if wep.element1 == None:
			pass
		elif wep.element_hidden == 0:
			element1 = f"{wep.element1} {wep.element1_attack}"
		elif wep.element_hidden == 1:
			element1 = f"{wep.element1} ({wep.element1_attack})"

		element2 = "-"
		if wep.element2 == None:
			pass
		else:
			element2 = f"{wep.element2} {wep.element2_attack}"

		elderseal = "-"
		if wep.elderseal != None:
			elderseal = wep.elderseal.capitalize()

		defense = "-"
		if wep.defense > 0:
			defense = f"+{wep.defense}"

		phial = "-"
		if wep.phial != None:
			phial = wep.phial

		close = ""
		power = ""
		paralysis = ""
		poison = ""
		sleep = ""
		blast = ""
		if self.root.pref.unicodeSymbols:
			if wep.coating_close == 1:
				close = "✓"
			if wep.coating_power == 1:
				power = "✓"
			if wep.coating_poison == 1:
				paralysis = "✓"
			if wep.coating_paralysis == 1:
				poison = "✓"
			if wep.coating_sleep == 1:
				sleep = "✓"
			if wep.coating_blast == 1:
				blast = "✓"
		else:
			if wep.coating_close == 1:
				close = "Yes"
			if wep.coating_power == 1:
				power = "Yes"
			if wep.coating_poison == 1:
				paralysis = "Yes"
			if wep.coating_paralysis == 1:
				poison = "Yes"
			if wep.coating_sleep == 1:
				sleep = "Yes"
			if wep.coating_blast == 1:
				blast = "Yes"

		weaponDetail = {
			"Name": (wep.name, None),
			"Rarity": (wep.rarity, wx.Bitmap(f"images/weapons/{self.currentWeaponTree}/rarity-24/{wep.rarity}.png")),
			"Attack": (wep.attack, wx.Bitmap(f"images/weapon-detail-24/attack.png")),
			"Attack (True)": (wep.attack_true, wx.Bitmap(f"images/weapon-detail-24/attack.png")),
			"Affinity": (affinity, wx.Bitmap(f"images/weapon-detail-24/affinity.png")),
			"Element I": (element1, wx.Bitmap(f"images/weapon-detail-24/element.png")),
			"Element II": (element2, wx.Bitmap(f"images/weapon-detail-24/element.png")),
			"Slot I": (wep.slot_1, wx.Bitmap(f"images/weapon-detail-24/slots.png")),
			"Slot II": (wep.slot_2, wx.Bitmap(f"images/weapon-detail-24/slots.png")),
			"Slot III": (wep.slot_3, wx.Bitmap(f"images/weapon-detail-24/slots.png")),
			"Elderseal": (elderseal, wx.Bitmap(f"images/weapon-detail-24/elderseal.png")),
			"Defense": (defense, wx.Bitmap(f"images/weapon-detail-24/defense.png")),
		}

		slots = {
			0: -1,
			1: wx.Bitmap(f"images/decoration-slots-24/1.png"),
			2: wx.Bitmap(f"images/decoration-slots-24/2.png"),
			3: wx.Bitmap(f"images/decoration-slots-24/3.png"),
		}

		note1 = str(wep.notes)[0]
		note2 = str(wep.notes)[1]
		note3 = str(wep.notes)[2]

		shelling = f"{str(wep.shelling).capitalize()} Lv {wep.shelling_level}"

		additionalDetails = {
			"switch-axe": ["Phial Type", str(wep.phial).capitalize(), wx.Bitmap(f"images/weapon-detail-24/phials.png")],
			"charge-blade": ["Phial Type", str(wep.phial).capitalize(), wx.Bitmap(f"images/weapon-detail-24/phials.png")],
			"gunlance": ["Shelling", shelling, wx.Bitmap(f"images/weapon-detail-24/shelling.png")],
			"insect-glaive": ["Kinsect Bonus", str(wep.kinsect_bonus).capitalize(), wx.Bitmap(f"images/damage-types-24/kinsect.png")],

			"hunting-horn": ["Notes", wx.Bitmap(f"images/weapon-detail-24/notes.png"),
							"Note I", note1, wx.Bitmap(f"images/weapon-detail-24/note1.png"),
							"Note II", note2, wx.Bitmap(f"images/weapon-detail-24/note2.png"),
							"Note III", note3, wx.Bitmap(f"images/weapon-detail-24/note3.png"),],

			"light-bowgun": ["Special Ammo", wep.special_ammo, wx.Bitmap(f"images/weapon-detail-24/specialammo.png"),
							"Deviation", wep.name, wx.Bitmap(f"images/weapon-detail-24/deviation.png"),],

			"heavy-bowgun": ["Special Ammo", wep.special_ammo, wx.Bitmap(f"images/weapon-detail-24/specialammo.png"),
							"Deviation", wep.name, wx.Bitmap(f"images/weapon-detail-24/deviation.png")],

			"bow": ["Close", close, wx.Bitmap(f"images/items-24/BottleWhite.png"),
					"Power", power, wx.Bitmap(f"images/items-24/BottleRed.png"),
					"Paralysis", paralysis, wx.Bitmap(f"images/items-24/BottleGold.png"),
					"Poison", poison, wx.Bitmap(f"images/items-24/BottleViolet.png"),
					"Sleep", sleep, wx.Bitmap(f"images/items-24/BottleCyan.png"),
					"Blast", blast, wx.Bitmap(f"images/items-24/BottleLime.png"),],
		}

		coatingIconColors = {
			0: "White",
			3: "Red",
			6: "Gold",
			9: "Violet",
			12: "Cyan",
			15: "Lime",
		} 

		for num in range(self.weaponRowNumbers[self.currentWeaponTree]):
			self.weaponDetailList.SetCellRenderer(num, 0, wx.grid.GridCellStringRenderer())
			self.weaponDetailList.SetCellRenderer(num, 1, wx.grid.GridCellStringRenderer())
			self.weaponDetailList.SetCellValue(num, 0, "-")
			self.weaponDetailList.SetCellValue(num, 1, "-")

		for row, (key, value) in enumerate(weaponDetail.items()):
			if key == "Rarity":
				self.weaponDetailList.SetCellBackgroundColour(row, 0, util.hexToRGB(self.rarityColors[wep.rarity]))
				self.weaponDetailList.SetCellBackgroundColour(row, 1, util.hexToRGB(self.rarityColors[wep.rarity]))
			elif key == "Affinity":
				try:
					if int(affinity.replace("%", "")) > 0:
						self.weaponDetailList.SetCellBackgroundColour(row, 0, util.hexToRGB("#C8E6C9")) # REMOVE because its using cgr this doesnt do anything
						self.weaponDetailList.SetCellBackgroundColour(row, 1, util.hexToRGB("#C8E6C9"))
					elif int(affinity.replace("%", "")) < 0:
						self.weaponDetailList.SetCellBackgroundColour(row, 0, util.hexToRGB("#FFCDD2")) # REMOVE because its using cgr this doesnt do anything
						self.weaponDetailList.SetCellBackgroundColour(row, 1, util.hexToRGB("#FFCDD2"))
				except:
					pass
			elif key == "Element I":
				try:
					self.weaponDetailList.SetCellBackgroundColour(row, 0, util.hexToRGB(self.elementColors[wep.element1])) # REMOVE because its using cgr this doesnt do anything
					self.weaponDetailList.SetCellBackgroundColour(row, 1, util.hexToRGB(self.elementColors[wep.element1])) # REMOVE because its using cgr this doesnt do anything
				except:
					pass
			elif key == "Element II":
				try:
					self.weaponDetailList.SetCellBackgroundColour(row, 0, util.hexToRGB(self.elementColors[wep.element2])) # REMOVE because its using cgr this doesnt do anything
					self.weaponDetailList.SetCellBackgroundColour(row, 1, util.hexToRGB(self.elementColors[wep.element2])) # REMOVE because its using cgr this doesnt do anything
				except:
					pass
			elif key == "Elderseal" and elderseal != "-":
				self.weaponDetailList.SetCellBackgroundColour(row, 0, util.hexToRGB("#D1C4E9"))
				self.weaponDetailList.SetCellBackgroundColour(row, 1, util.hexToRGB("#D1C4E9"))
			elif key == "Defense" and defense != "-":
				self.weaponDetailList.SetCellBackgroundColour(row, 0, util.hexToRGB("#D7CCC8"))
				self.weaponDetailList.SetCellBackgroundColour(row, 1, util.hexToRGB("#D7CCC8"))

			if key in ["Slot I", "Slot II", "Slot III"]:
				self.weaponDetailList.SetCellRenderer(row, 0, cgr.ImageTextCellRenderer(
					wx.Bitmap("images/weapon-detail-24/slots.png"), key))	
				if value[0] != 0:
					self.weaponDetailList.SetCellRenderer(row, 1, cgr.ImageTextCellRenderer(
						wx.Bitmap(f"images/decoration-slots-24/{value[0]}.png"), str(value[0])))
				else:
					self.weaponDetailList.SetCellValue(row, 1, str(value[0]))
			if key in ["Element I", "Element II"]:
				try:
					if str(value[0].split(" ")[0]) != "-":
						self.weaponDetailList.SetCellRenderer(row, 0,
							cgr.ImageTextCellRenderer(wx.Bitmap("images/weapon-detail-24/element.png"),
								key,util.hexToRGB(self.elementColors[value[0].split(" ")[0]])))
						self.weaponDetailList.SetCellRenderer(row, 1,
							cgr.ImageTextCellRenderer(wx.Bitmap(f"images/damage-types-24/{str(value[0].split(' ')[0].lower())}.png"),
								value[0], util.hexToRGB(self.elementColors[value[0].split(" ")[0]])))
				except:
					self.weaponDetailList.SetCellValue(row, 1, "-")
			else:
				if value[0] == 0:
					self.weaponDetailList.SetCellValue(row, 1, "-")
				else:
					self.weaponDetailList.SetCellValue(row, 1, str(value[0]))
			try:
				if key == "Name":
					self.weaponDetailList.SetCellValue(row, 0, key)
				elif key == "Rarity":
					self.weaponDetailList.SetCellRenderer(row, 0, cgr.ImageTextCellRenderer(
						wx.Bitmap(f"images/weapons/{self.currentWeaponTree}/rarity-24/{value[0]}.png"), key))
				else:
					self.weaponDetailList.SetCellRenderer(row, 0, cgr.ImageTextCellRenderer(
						wx.Bitmap(self.weaponDetailIcons[key]), key))
			except:
				pass

		pageCount = self.weaponDetailsNotebook.GetPageCount()
		if pageCount != 1:
			for i in range(pageCount - 1):
				self.weaponDetailsNotebook.RemovePage(1)


		row = len(weaponDetail.items())
		if self.currentWeaponTree in ["charge-blade", "switch-axe", "gunlance", "insect-glaive"]:
			if self.currentWeaponTree in ["charge-blade", "switch-axe"] :
				self.weaponDetailList.SetCellRenderer(row, 0, cgr.ImageTextCellRenderer(wx.Bitmap( 
							"images/weapon-detail-24/phials.png") 
							, additionalDetails[self.currentWeaponTree][0]))
			elif self.currentWeaponTree == "gunlance":
				self.weaponDetailList.SetCellRenderer(row, 0, cgr.ImageTextCellRenderer(wx.Bitmap( 
							"images/weapon-detail-24/shelling.png") 
							, additionalDetails[self.currentWeaponTree][0]))
			elif self.currentWeaponTree == "insect-glaive":
				self.weaponDetailList.SetCellRenderer(row, 0, cgr.ImageTextCellRenderer(wx.Bitmap( 
							"images/damage-types-24/kinsect.png") 
							, additionalDetails[self.currentWeaponTree][0]))
			self.weaponDetailList.SetCellValue(row, 1, str(additionalDetails[self.currentWeaponTree][1]))
		elif self.currentWeaponTree in ["light-bowgun", "heavy-bowgun"]:
			self.weaponDetailList.SetCellRenderer(row, 0, cgr.ImageTextCellRenderer(wx.Bitmap( 
							"images/weapon-detail-24/specialammo.png") 
							, additionalDetails[self.currentWeaponTree][0]))
			self.weaponDetailList.SetCellValue(row, 1, str(additionalDetails[self.currentWeaponTree][1]))

			self.weaponDetailList.SetCellRenderer(row + 1, 0, cgr.ImageTextCellRenderer(wx.Bitmap( 
							"images/weapon-detail-24/deviation.png") 
							, additionalDetails[self.currentWeaponTree][3]))
			self.weaponDetailList.SetCellValue(row + 1, 1, str(additionalDetails[self.currentWeaponTree][4]))

			self.weaponDetailsNotebook.AddPage(self.weaponAmmoPanel, "Ammo")
			self.weaponDetailsNotebook.SetPageImage(1, self.ammo)
			self.loadBowgunAmmo()

		elif self.currentWeaponTree == "bow":
			for num in range(0, 17, 3):
				self.weaponDetailList.SetCellRenderer(row, 0, cgr.ImageTextCellRenderer(wx.Bitmap( 
							f"images/items-24/Bottle{coatingIconColors[num]}.png") 
							, additionalDetails[self.currentWeaponTree][num]))
				self.weaponDetailList.SetCellValue(row, 0, additionalDetails[self.currentWeaponTree][num])
				self.weaponDetailList.SetCellValue(row, 1, str(additionalDetails[self.currentWeaponTree][num + 1]))
				row += 1
		elif self.currentWeaponTree == "hunting-horn":
			noteNum = 1
			for num in range(0, 9, 3):
				self.weaponDetailList.SetCellRenderer(row, 0, cgr.ImageTextCellRenderer(wx.Bitmap(
							"images/weapon-detail-24/notes.png")
							, additionalDetails[self.currentWeaponTree][num + 2]))
				noteColor = self.noteColors[additionalDetails[self.currentWeaponTree][num + 3]]
				self.weaponDetailList.SetCellRenderer(row, 1, cgr.ImageTextCellRenderer(wx.Bitmap( 
							f"images/notes-24/Note{noteNum}{noteColor}.png")
							, f"{noteColor}",
							imageOffset=40))
				noteNum += 1
				row += 1

			self.weaponDetailsNotebook.AddPage(self.weaponMelodiesPanel, "Melodies")
			self.weaponDetailsNotebook.SetPageImage(1, self.notes)
			self.loadHuntingHornMelodies([additionalDetails[self.currentWeaponTree][3], additionalDetails[self.currentWeaponTree][6], additionalDetails[self.currentWeaponTree][9]])

		if self.currentWeaponTree not in ["light-bowgun", "heavy-bowgun", "bow"]:
			if not self.weaponSharpnessTable.IsShown():
				self.weaponSharpnessTable.Show()
				self.weaponDetailSizer.Insert(1, self.weaponSharpnessTable, 0.5, wx.EXPAND|wx.TOP, 5)
				self.weaponDetailSizer.SetDimension(self.weaponDetailPanel.GetPosition(), self.weaponDetailPanel.GetSize())

			sharpnessMaxed = bool(wep.sharpness_maxed)
			sharpnessLevels = {}
			for num in (5, 4, 3, 2, 1, 0):
				sharpnessLevels[num] = self.adjustSharpness(num, sharpnessMaxed, data)	

			self.weaponSharpnessTable.SetColLabelSize(0)
			self.weaponSharpnessTable.SetRowLabelSize(0)

			extraPixels = 20
			self.weaponSharpnessTable.SetColSize(0, 40)
			self.weaponSharpnessTable.SetColSize(1, (int(sharpnessLevels[5][0]) / 2 + extraPixels))
			self.weaponSharpnessTable.SetColSize(2, (int(sharpnessLevels[5][1]) / 2 + extraPixels))
			self.weaponSharpnessTable.SetColSize(3, (int(sharpnessLevels[5][2]) / 2 + extraPixels))
			self.weaponSharpnessTable.SetColSize(4, (int(sharpnessLevels[5][3]) / 2 + extraPixels))
			self.weaponSharpnessTable.SetColSize(5, (int(sharpnessLevels[5][4]) / 2 + extraPixels))
			self.weaponSharpnessTable.SetColSize(6, (int(sharpnessLevels[5][5]) / 2 + extraPixels))

			for row in range(6):
				self.weaponSharpnessTable.SetCellValue(row, 0, "+" + str(row))

				self.weaponSharpnessTable.SetCellValue(row, 1, str(sharpnessLevels[row][0]))
				self.weaponSharpnessTable.SetCellBackgroundColour(row, 1, util.hexToRGB("#d92c2c"))

				self.weaponSharpnessTable.SetCellValue(row, 2, str(sharpnessLevels[row][1]))
				self.weaponSharpnessTable.SetCellBackgroundColour(row, 2, util.hexToRGB("#d9662c"))

				self.weaponSharpnessTable.SetCellValue(row, 3, str(sharpnessLevels[row][2]))
				self.weaponSharpnessTable.SetCellBackgroundColour(row, 3, util.hexToRGB("#d9d12c"))

				self.weaponSharpnessTable.SetCellValue(row, 4, str(sharpnessLevels[row][3]))
				self.weaponSharpnessTable.SetCellBackgroundColour(row, 4, util.hexToRGB("#70d92c"))

				self.weaponSharpnessTable.SetCellValue(row, 5, str(sharpnessLevels[row][4]))
				self.weaponSharpnessTable.SetCellBackgroundColour(row, 5, util.hexToRGB("#2c86d9"))

				self.weaponSharpnessTable.SetCellValue(row, 6, str(sharpnessLevels[row][5]))
				self.weaponSharpnessTable.SetCellBackgroundColour(row, 6, util.hexToRGB("#ffffff"))
		else:
			if self.weaponSharpnessTable.IsShown():
				self.weaponSharpnessTable.Hide()
				self.weaponDetailSizer.Remove(1)
				self.weaponDetailSizer.SetDimension(self.weaponDetailPanel.GetPosition(), self.weaponDetailPanel.GetSize())

		self.loadWeaponMaterials()

	def loadBowgunAmmo(self):
		self.ilAmmo.RemoveAll()
		self.weaponAmmoList.ClearAll()

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_CENTER
		info.Text = "Ammo Types"
		self.weaponAmmoList.InsertColumn(0, info)

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_CENTER
		info.Text = "Capacity"
		self.weaponAmmoList.InsertColumn(1, info)

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_CENTER
		info.Text = "Type+Recoil"
		self.weaponAmmoList.InsertColumn(2, info)

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_CENTER
		info.Text = "Reload"
		self.weaponAmmoList.InsertColumn(3, info)

		self.weaponAmmoList.SetColumnWidth(0, 132 - 10)
		self.weaponAmmoList.SetColumnWidth(1, 102)
		self.weaponAmmoList.SetColumnWidth(2, 112)
		self.weaponAmmoList.SetColumnWidth(3, 102 - 0)

		sql = """
			SELECT wa.id AS ammo_id, wa.deviation, wa.special_ammo, wa.normal1_clip, wa.normal1_rapid, wa.normal1_recoil, wa.normal1_reload, wa.normal2_clip, wa.normal2_rapid,
			wa.normal2_recoil, wa.normal2_reload, wa.normal3_clip, wa.normal3_rapid, wa.normal3_recoil, wa.normal3_reload, wa.pierce1_clip, wa.pierce1_rapid, wa.pierce1_recoil, wa.pierce1_reload,
			wa.pierce2_clip, wa.pierce2_rapid, wa.pierce2_recoil, wa.pierce2_reload, wa.pierce3_clip, wa.pierce3_rapid, wa.pierce3_recoil, wa.pierce3_reload, wa.spread1_clip, wa.spread1_rapid,
			wa.spread1_recoil, wa.spread1_reload, wa.spread2_clip, wa.spread2_rapid, wa.spread2_recoil, wa.spread2_reload, wa.spread3_clip, wa.spread3_rapid, wa.spread3_recoil, wa.spread3_reload,
			wa.sticky1_clip, wa.sticky1_rapid, wa.sticky1_recoil, wa.sticky1_reload, wa.sticky2_clip, wa.sticky2_rapid, wa.sticky2_recoil, wa.sticky2_reload, wa.sticky3_clip, wa.sticky3_rapid, wa.sticky3_recoil, wa.sticky3_reload,
			wa.cluster1_clip, wa.cluster1_rapid, wa.cluster1_recoil, wa.cluster1_reload, wa.cluster2_clip, wa.cluster2_rapid, wa.cluster2_recoil, wa.cluster2_reload, wa.cluster3_clip, wa.cluster3_rapid, wa.cluster3_recoil, wa.cluster3_reload,
			wa.recover1_clip, wa.recover1_rapid, wa.recover1_recoil, wa.recover1_reload, wa.recover2_clip, wa.recover2_rapid, wa.recover2_recoil, wa.recover2_reload, wa.poison1_clip, wa.poison1_rapid, wa.poison1_recoil, wa.poison1_reload,
			wa.poison2_clip, wa.poison2_rapid, wa.poison2_recoil, wa.poison2_reload, wa.paralysis1_clip, wa.paralysis1_rapid, wa.paralysis1_recoil, wa.paralysis1_reload, wa.paralysis2_clip, wa.paralysis2_rapid, wa.paralysis2_recoil, wa.paralysis2_reload,
			wa.sleep1_clip, wa.sleep1_rapid, wa.sleep1_recoil, wa.sleep1_reload, wa.sleep2_clip, wa.sleep2_rapid, wa.sleep2_recoil, wa.sleep2_reload, wa.exhaust1_clip, wa.exhaust1_rapid, wa.exhaust1_recoil, wa.exhaust1_reload,
			wa.exhaust2_clip, wa.exhaust2_rapid, wa.exhaust2_recoil, wa.exhaust2_reload, wa.flaming_clip, wa.flaming_rapid, wa.flaming_recoil, wa.flaming_reload, wa.water_clip, wa.water_rapid, wa.water_recoil, wa.water_reload,
			wa.freeze_clip, wa.freeze_rapid, wa.freeze_recoil, wa.freeze_reload, wa.thunder_clip, wa.thunder_rapid, wa.thunder_recoil, wa.thunder_reload, wa.dragon_clip, wa.dragon_rapid, wa.dragon_recoil, wa.dragon_reload,
			wa.slicing_clip, wa.slicing_rapid, wa.slicing_recoil, wa.slicing_reload, wa.wyvern_clip, wa.wyvern_reload, wa.demon_clip, wa.demon_recoil, wa.demon_reload, wa.armor_clip, wa.armor_recoil, wa.armor_reload, wa.tranq_clip, wa.tranq_recoil, wa.tranq_reload

			FROM weapon w
				JOIN weapon_text wt USING (id)
				LEFT OUTER JOIN weapon_ammo wa ON w.ammo_id = wa.id
			WHERE w.id = :weaponId
			AND wt.lang_id = :langId
		"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, (self.currentlySelectedWeaponID, "en"))
		data = data.fetchone()
	
		ammoTypes = [
					"Normal 1", "Normal 2", "Normal 3",
					"Pierce 1", "Pierce 2", "Pierce 3",
					"Spread 1", "Spread 2", "Spread 3",
					"Sticky 1", "Sticky 2", "Sticky 3",
					"Cluster 1", "Cluster 2", "Cluster 3",
					"Recover 1", "Recover 2",
					"Poison 1", "Poison 2",
					"Paralysis 1", "Paralysis 2",
					"Sleep 1", "Sleep 2",
					"Exhaust 1", "Exhaust 2",
					"Flaming",
					"Water",
					"Freeze",
					"Thunder",
					"Dragon",
					"Slicing",
					"Wyvern",
					"Demon",
					"Armor",
					"Tranq",
					]

		ammoIcons = {
			"Normal 1": "AmmoWhite.png",
			"Normal 2": "AmmoWhite.png",
			"Normal 3": "AmmoWhite.png",
			"Pierce 1": "AmmoBlue.png",
			"Pierce 2": "AmmoBlue.png",
			"Pierce 3": "AmmoBlue.png",
			"Spread 1": "AmmoDarkGreen.png",
			"Spread 2": "AmmoDarkGreen.png",
			"Spread 3": "AmmoDarkGreen.png",
			"Sticky 1": "AmmoBeige.png",
			"Sticky 2": "AmmoBeige.png",
			"Sticky 3": "AmmoBeige.png",
			"Cluster 1": "AmmoDarkRed.png",
			"Cluster 2": "AmmoDarkRed.png",
			"Cluster 3": "AmmoDarkRed.png",
			"Recover 1": "AmmoGreen.png",
			"Recover 2": "AmmoGreen.png",
			"Poison 1": "AmmoViolet.png",
			"Poison 2": "AmmoViolet.png",
			"Paralysis 1": "AmmoGold.png",
			"Paralysis 2": "AmmoGold.png",
			"Sleep 1": "AmmoCyan.png",
			"Sleep 2": "AmmoCyan.png",
			"Exhaust 1": "AmmoDarkPurple.png",
			"Exhaust 2": "AmmoDarkPurple.png",
			"Flaming": "AmmoOrange.png",
			"Water": "AmmoDarkBlue.png",
			"Freeze": "AmmoWhite.png",
			"Thunder": "AmmoYellow.png",
			"Dragon": "AmmoDarkRed.png",
			"Slicing": "AmmoWhite.png",
			"Wyvern": "AmmoLightBeige.png",
			"Demon": "AmmoRed.png",
			"Armor": "AmmoDarkBeige.png",
			"Tranq": "AmmoPink.png",
		}

		col = 3
		# different checks are used avoid going out of bounds since not all ammo types have the same amount of columns
		for item in ammoTypes:
			img = self.ilAmmo.Add(wx.Bitmap(f"images/items-24/{ammoIcons[item]}"))
			if col == 127:
				if data[col] != 0 and data[col] != None:
					index = self.weaponAmmoList.InsertItem(self.weaponAmmoList.GetItemCount(), item, img)
					self.weaponAmmoList.SetItem(index, 1, str(data[col]))
					if self.currentWeaponTree == "heavy-bowgun":
						self.weaponAmmoList.SetItem(index, 2, "Rapid")
					self.weaponAmmoList.SetItem(index, 3, str(data[col + 1]).capitalize())
			elif col > 127:
				if data[col] != 0 and data[col] != None:
					index = self.weaponAmmoList.InsertItem(self.weaponAmmoList.GetItemCount(), item, img)
					self.weaponAmmoList.SetItem(index, 1, str(data[col]))
					self.weaponAmmoList.SetItem(index, 2, "Normal+" + str(data[col + 1]))
					self.weaponAmmoList.SetItem(index, 3, str(data[col + 2]).capitalize())
			else:
				if data[col] != 0 and data[col] != None:
					index = self.weaponAmmoList.InsertItem(self.weaponAmmoList.GetItemCount(), item, img)
					self.weaponAmmoList.SetItem(index, 1, str(data[col]))
					if data[col + 1] == 1:
						self.weaponAmmoList.SetItem(index, 2, f"Rapid+{data[col + 2]}")
					elif data[col + 2] == - 1:
						self.weaponAmmoList.SetItem(index, 2, "Auto Reload")
					else:
						self.weaponAmmoList.SetItem(index, 2, f"Normal+{data[col + 2]}")
					self.weaponAmmoList.SetItem(index, 3, str(data[col + 3]).capitalize())
			if col == 127:
				col += 2
			elif col > 127:
				col += 3
			else:
				col += 4


	def loadHuntingHornMelodies(self, notes: List[str]):
		if self.weaponMelodiesPanel.GetSize()[0] < 275:
			size = 275
		else:
			size = self.weaponMelodiesPanel.GetSize()[0] - 4 * 29 - 60 - 65 - 6 - 20 + 27
		self.weaponMelodiesList.SetColSize(6, size)
		noteNumbers = {
			notes[0]: "Note1",
			notes[1]: "Note2",
			notes[2]: "Note3",
		}

		sql = """
			SELECT wm.id, wm.notes, wmt.effect1, wmt.effect2, wm.duration, wm.extension
				FROM weapon_melody wm
					JOIN weapon_melody_text wmt
						ON  wm.id = wmt.id
			WHERE wmt.lang_id = :langId
			ORDER BY wm.id
		"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, ("en",))
		data = data.fetchall()

		melodies = []

		for row in data:
			melodies.append(w.Melody(row))

		addMelody = True
		melodyList = []
		for melody in melodies:
			melodyNotes = self.splitNotes(str(melody.notes))
			for note in melodyNotes:
				if note not in notes:
					addMelody = False
					break
				else:
					addMelody = True
			if addMelody:
				melodyList.append(melody)
	
		try:
			self.weaponMelodiesList.DeleteRows(len(melodyList), self.weaponMelodiesList.GetNumberRows())
		except:
			pass
		if self.weaponMelodiesList.GetNumberRows() < len(melodyList):
			self.weaponMelodiesList.AppendRows(len(melodyList) - self.weaponMelodiesList.GetNumberRows())
		for row, melody in enumerate(melodyList):
			for i in range(len(melody.notes)):
				self.weaponMelodiesList.SetCellRenderer(row, i, cgr.ImageCellRenderer(
					wx.Bitmap(f"images/notes-24/{noteNumbers[melody.notes[i]]}{self.noteColors[melody.notes[i]]}.png")))
			self.weaponMelodiesList.SetCellFont(row, 4, 
				wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False))
			self.weaponMelodiesList.SetCellValue(row, 4, str(melody.duration))
			self.weaponMelodiesList.SetCellFont(row, 5, 
				wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False))
			self.weaponMelodiesList.SetCellValue(row, 5, str(melody.extension))
			self.weaponMelodiesList.SetCellFont(row, 6, 
				wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False))
			self.weaponMelodiesList.SetCellValue(row, 6, f"{melody.effect1}\n{melody.effect2}")
			

	def splitNotes(self, notes: str) -> List[str]:
		return [note for note in notes]


	def loadWeaponMaterials(self):
		self.ilMats.RemoveAll()
		self.materialsRequiredList.ClearAll()
		test = self.ilMats.Add(self.testIcon)

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = "Req. Materials"
		self.materialsRequiredList.InsertColumn(0, info)
		self.materialsRequiredList.SetColumnWidth(0, 300)
		info = wx.ListItem()

		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_CENTER
		info.Text = ""
		self.materialsRequiredList.InsertColumn(1, info)
		self.materialsRequiredList.SetColumnWidth(1, 137)

		self.materialsRequiredList.InsertColumn(2, info)
		self.materialsRequiredList.SetColumnWidth(2, 0)

		sql = """
			SELECT i.id item_id, it.name item_name, i.icon_name item_icon_name,
				i.category item_category, i.icon_color item_icon_color, w.quantity, w.recipe_type
			FROM weapon_recipe w
				JOIN item i
					ON w.item_id = i.id
				JOIN item_text it
					ON it.id = i.id
					AND it.lang_id = :langId
			WHERE it.lang_id = :langId
				AND w.weapon_id= :weaponId
			ORDER BY 
				w.recipe_type ASC,
				i.id ASC
		"""
		
		conn = sqlite3.connect("mhw.db")
		data = conn.execute(sql, ("en", self.currentlySelectedWeaponID))
		data = data.fetchall()

		materials = []
		for row in data:
			materials.append(w.WeaponMaterial(row))

		for item in materials:
			img = self.ilMats.Add(wx.Bitmap(f"images/items-24/{item.iconName}{item.iconColor}.png"))
			if item.recipeType == "Create":
				try:
					index = self.materialsRequiredList.InsertItem(self.materialsRequiredList.GetItemCount(),
						f"Create:    {item.name}", img)
				except:
					index = self.materialsRequiredList.InsertItem(self.materialsRequiredList.GetItemCount(),
						f"Create:    {item.name}", test)
			else:
				try:
					index = self.materialsRequiredList.InsertItem(self.materialsRequiredList.GetItemCount(),
						f"Upgrade:    {item.name}", img)
				except:
					index = self.materialsRequiredList.InsertItem(self.materialsRequiredList.GetItemCount(),
						f"Upgrade:    {item.name}", test)
			self.materialsRequiredList.SetItem(index, 1, f"{item.quantity}")
			self.materialsRequiredList.SetItem(index, 2, f"{item.id},{item.category}")


	def adjustSharpness(self, handicraftLevel: int, sharpnessMaxed: bool, data: Tuple[str]) -> Union[List[str], List[int]]:
		"""
		handicraftLevel = The level of the handicraft weapon skill. From 0 to 5.

		sharpnessMaxed = Boolean indicating whether the weapon has reached its sharpness limit or not.

		data = Tuple containing all the information about the specific weapon retrieved from the database.

		returns:

			A list of the unmodified sharpness when sharpnessMaxed is True or
			A list of the readjusted sharpness values when sharpnessMaxed is False.
		"""

		assert handicraftLevel >= 0 and handicraftLevel <= 5, "Handicraft only goes from 0 to 5!"
		
		if sharpnessMaxed:
			return data[16].split(",")
		else:
			sharpnessAdjusted = data[16].split(",")
			index = len(sharpnessAdjusted) - 1
			handicraftReduction = 10 * (5 - handicraftLevel)
			for item in sharpnessAdjusted:
				toRemove = min(int(sharpnessAdjusted[index]), handicraftReduction)
				sharpnessAdjusted[index] = int(sharpnessAdjusted[index]) - toRemove
				handicraftReduction -= toRemove
				index -= 1

			return sharpnessAdjusted


	def onWeaponSelection(self, event):
		"""
		When a specific weapon is selected in the tree, the detail view gets populated with the information from the database.
		"""
		
		if not self.init:
			self.currentlySelectedWeaponID = self.weaponTree.GetCellValue(event.GetRow(), 9)
			if self.currentlySelectedWeaponID != "":
				try:
					self.weaponSharpnessTable.ClearGrid()
				except:
					pass
				self.loadWeaponDetailAll()

		
	def onWeaponTypeSelection(self, event):
		"""
		When a weapon button at the top of the screen is pressed the weapon tree is reloaded with the new weapon type information.
		"""

		self.currentWeaponTree = event.GetEventObject().GetName()
		self.loadWeaponTree()


	def onMaterialDoubleClick(self, event):
		materialInfo = self.materialsRequiredList.GetItemText(event.GetEventObject().GetFirstSelected(), 2)
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
			self.weaponDetailList.SetColSize(0, self.weaponDetailPanel.GetSize()[0] * 0.56)
			self.weaponDetailList.SetColSize(1, self.weaponDetailPanel.GetSize()[0] * 0.44 - 20)
			self.materialsRequiredList.SetColumnWidth(0, self.weaponDetailPanel.GetSize()[0] * 0.66)
			self.materialsRequiredList.SetColumnWidth(1, self.weaponDetailPanel.GetSize()[0] * 0.34 - 20)
		except:
			pass


	def onScroll(self, event):
		"""
		On every scroll event in weaponDetail, scrolls the parent ScrolledWindow by 3 in the appropriate direction.
		"""

		if event.GetWheelRotation() > 0:
			if self.weaponDetailPanel.GetViewStart()[1] < 3:
				self.weaponDetailPanel.Scroll(0, self.weaponDetailPanel.GetViewStart()[1] + 1 * -1)
			else:
				self.weaponDetailPanel.Scroll(0, self.weaponDetailPanel.GetViewStart()[1] + 3 * -1)
		else:
			if self.weaponDetailPanel.GetViewStart()[1] < 3:
				self.weaponDetailPanel.Scroll(0, self.weaponDetailPanel.GetViewStart()[1] + 1)
			else:
				self.weaponDetailPanel.Scroll(0, self.weaponDetailPanel.GetViewStart()[1] + 3)
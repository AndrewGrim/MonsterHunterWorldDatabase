import wx
import wx.grid
import wx.lib.gizmos as gizmos
import CustomGridRenderer as cgr
import wx.propgrid as wxpg
import sqlite3
import typing
from typing import List
from typing import Union
from typing import Tuple
from typing import Dict
from typing import NewType
import Utilities as util
import Links as link
import MonstersTab as m

wxColour = NewType("wxColour", None)
sqlite3Connection = NewType("sqlite3Connection", None)


class MonstersTab:

	def __init__(self, root, mainNotebook, link):
		self.root = root
		self.mainNotebook = mainNotebook
		self.link = link
		
		self.currentMonsterID = 17
		self.currentMonsterName = "Great Jagras"
		self.currentMonsterMaterialID = 212
		self.currentMonsterSize = "large"
		self.testIcon = wx.Bitmap("images/unknown.png", wx.BITMAP_TYPE_ANY) # REMOVE since youll be using specific icons
		self.ilMats = wx.ImageList(24, 24)
		self.ilMats.Add(self.testIcon) # to prevent crash on linux, gtk wants at least one image in image list before you set it

		self.initMonstersTab()
		self.initMonsterSizeButtons()
		self.initSearch()
		self.initMonsterList()
		self.loadMonsterList()
		self.initMonsterSummary() # TODO sort weaknesses from highest to low/none
		self.initMonsterDamage()
		self.initMonsterMaterials()

		# TEST defaults to materials tab
		# PREFERENCES make this customizable
		self.monsterDetailsNotebook.SetSelection(0)


	def initMonstersTab(self):
		# TODO sort columns on header click

		# the outermost panel for the monsters tab
		self.monstersPanel = wx.Panel(self.mainNotebook)
		# add page to notebook
		self.mainNotebook.AddPage(self.monstersPanel, "Monsters")
		# main sizer for the monsters tab
		self.monstersSizer = wx.BoxSizer(wx.HORIZONTAL)

		# left side
		# sizer containing the monsters table
		self.monsterSelectionSizer = wx.BoxSizer(wx.VERTICAL)
		self.monsterListSizer = wx.BoxSizer(wx.VERTICAL)
		self.monsterSizeButtonsSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.monsterSelectionSizer.Add(self.monsterListSizer)
		self.monsterSelectionSizer.Add(self.monsterSizeButtonsSizer)
		# create monsters table and add bindings on selection and on size change of the main window
		# add left side sizer to the main sizer of the monsters tab
		self.monstersSizer.Add(self.monsterSelectionSizer, 1, wx.EXPAND)

		# right side
		# sizer containing the monsters details
		self.monstersDetailedSizer = wx.BoxSizer(wx.VERTICAL)
		# create bitmap from image and load bitmap into a label
		self.monsterImage = wx.Bitmap("images/monsters/160/Great Jagras.png", wx.BITMAP_TYPE_ANY)
		self.monsterImageLabel = wx.StaticBitmap(self.monstersPanel, bitmap=self.monsterImage, size=(160, 160))
		# detailed view notebook
		self.monsterDetailsNotebook = wx.Notebook(self.monstersPanel)
		self.summaryPanel = wx.Panel(self.monsterDetailsNotebook)
		self.damagePanel = wx.ScrolledWindow(self.monsterDetailsNotebook)
		self.materialsPanel = wx.Panel(self.monsterDetailsNotebook)
		#
		self.monsterSummarySizer = wx.BoxSizer(wx.VERTICAL)
		self.monsterDetailsNotebook.AddPage(self.summaryPanel, "Summary")
		# 
		self.monsterDamageSizer = wx.BoxSizer(wx.VERTICAL)
		self.monsterDetailsNotebook.AddPage(self.damagePanel, "Damage")
		#
		self.monsterMaterialsSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.monsterDetailsNotebook.AddPage(self.materialsPanel, "Materials")
		# add the right side detailed view to the main size of the monsters notebook tab
		self.monstersSizer.Add(self.monstersDetailedSizer, 2, wx.EXPAND)
		# add widgets within to their parent sizer
		self.monstersDetailedSizer.Add(self.monsterImageLabel, 1, wx.ALIGN_CENTER_HORIZONTAL)
		self.monstersDetailedSizer.Add(self.monsterDetailsNotebook, 5, wx.EXPAND)

		# set sizer for the monsters notebook tab
		self.monstersPanel.SetSizer(self.monstersSizer)

		self.damagePanel.SetScrollRate(20, 20)


	def initMonsterSizeButtons(self):
		self.smallMonstersButton = wx.Button(self.monstersPanel, label="Small", name="small")
		self.largeMonstersButton = wx.Button(self.monstersPanel, label="Large", name="large")
		self.smallMonstersButton.SetBitmap(wx.Bitmap("images/monsters/24/Jagras.png"))
		self.largeMonstersButton.SetBitmap(wx.Bitmap("images/monsters/24/Great Jagras.png"))
		self.monsterSizeButtonsSizer.Add(self.smallMonstersButton)
		self.monsterSizeButtonsSizer.Add(self.largeMonstersButton)

		self.smallMonstersButton.Bind(wx.EVT_BUTTON, self.onMonsterSizeSelect)
		self.largeMonstersButton.Bind(wx.EVT_BUTTON, self.onMonsterSizeSelect)


	def initSearch(self):
		self.search = wx.TextCtrl(self.monstersPanel)
		self.search.SetHint("  search by name")
		self.search.Bind(wx.EVT_TEXT, self.onSearchTextEnter)
		self.monsterSizeButtonsSizer.Add(180, 0, 0)
		self.monsterSizeButtonsSizer.Add(self.search, 0, wx.TOP, 4)


	def onSearchTextEnter(self, event):
		self.loadMonsterList()


	def initMonsterList(self):
		self.monsterList = wx.ListCtrl(self.monstersPanel, style=wx.LC_REPORT
																| wx.LC_VRULES
																| wx.LC_HRULES
																| wx.LC_NO_HEADER
																)
		self.monsterList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onMonsterSelected)

		self.ilBig = wx.ImageList(56, 56)
		self.il = wx.ImageList(24, 24)
		self.monsterList.SetImageList(self.ilBig, wx.IMAGE_LIST_SMALL)
		self.test = self.il.Add(self.testIcon)

		self.monsterSelectionSizer.Add(self.monsterList, 1, wx.EXPAND)


	def loadMonsterList(self):
		try:
			self.monsterList.ClearAll()
		except:
			pass

		searchText = self.search.GetValue()

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = ""
		self.monsterList.InsertColumn(0, info)
		self.monsterList.SetColumnWidth(0, 443)
		self.monsterList.InsertColumn(1, info)
		self.monsterList.SetColumnWidth(1, 0)

		if len(searchText) == 0 or searchText == " ":
			sql = """
				SELECT m.id, m.size, mt.name
				FROM monster m
				JOIN monster_text mt
					ON m.id = mt.id
				WHERE size = :size
					AND mt.lang_id = :langId
			"""
		else:
			sql = f"""
				SELECT m.id, m.size, mt.name
				FROM monster m
				JOIN monster_text mt
					ON m.id = mt.id
				WHERE size = :size
					AND mt.lang_id = :langId
					AND mt.name like '%{searchText}%'
			"""

		conn = sqlite3.connect("mhw.db")
		data = conn.execute(sql, (self.currentMonsterSize, "en"))
		data = data.fetchall()

		monsters = []
		for row in data:
			monsters.append(m.Monster(row))

		self.ilBig.RemoveAll()

		for monster in monsters:
			img = self.ilBig.Add(wx.Bitmap(f"images/monsters/56/{monster.name}.png"))
			index = self.monsterList.InsertItem(self.monsterList.GetItemCount(), monster.name, img)
			self.monsterList.SetItem(index, 1, f"{monster.id}")



	def initMonsterSummary(self):
		self.monsterSummaryNameLabel = wx.StaticText(self.summaryPanel, label="Name:\nDescription")
		self.monsterSummarySizer.Add(self.monsterSummaryNameLabel, 1, wx.EXPAND)
		
		self.summaryTree = wx.lib.agw.hypertreelist.HyperTreeList(self.summaryPanel, -1, style=0, 
																	agwStyle=
																	gizmos.TR_DEFAULT_STYLE
																	| gizmos.TR_TWIST_BUTTONS
																	| gizmos.TR_ROW_LINES
																	| gizmos.TR_COLUMN_LINES
																	| gizmos.TR_NO_LINES
																	| gizmos.TR_FULL_ROW_HIGHLIGHT
																	| gizmos.TR_HIDE_ROOT
																	)
												
		self.monsterSummarySizer.Add(self.summaryTree, 12, wx.EXPAND)

		self.summaryTree.AddColumn("")
		self.summaryTree.AddColumn("")
		self.summaryTree.SetMainColumn(0)
		self.summaryTree.SetColumnWidth(0, (self.root.GetSize().width * 0.80) * 0.37)
		self.summaryTree.SetColumnWidth(1, (self.root.GetSize().width * 0.80) * 0.20)
		self.summaryTree.SetColumnAlignment(1, wx.ALIGN_CENTER)

		self.summaryTree.SetImageList(self.il)

		self.ancientForest = self.il.Add(wx.Bitmap("images/locations-24/Ancient Forest.png"))
		self.wildspireWaste = self.il.Add(wx.Bitmap("images/locations-24/Wildspire Waste.png"))
		self.coralHighlands = self.il.Add(wx.Bitmap("images/locations-24/Coral Highlands.png"))
		self.rottenVale = self.il.Add(wx.Bitmap("images/locations-24/Rotten Vale.png"))
		self.eldersRecess = self.il.Add(wx.Bitmap("images/locations-24/Elder's Recess.png"))

		self.locationIcons = {
			"Ancient Forest": self.ancientForest,
			"Wildspire Waste": self.wildspireWaste,
			"Coral Highlands": self.coralHighlands,
			"Rotten Vale": self.rottenVale,
			"Elder's Recess": self.eldersRecess,
		}

		self.fire = self.il.Add(wx.Bitmap("images/damage-types-24/fire.png"))
		self.water = self.il.Add(wx.Bitmap("images/damage-types-24/water.png"))
		self.ice = self.il.Add(wx.Bitmap("images/damage-types-24/ice.png"))
		self.thunder = self.il.Add(wx.Bitmap("images/damage-types-24/thunder.png"))
		self.dragon = self.il.Add(wx.Bitmap("images/damage-types-24/dragon.png"))

		self.poison = self.il.Add(wx.Bitmap("images/damage-types-24/poison.png"))
		self.sleep = self.il.Add(wx.Bitmap("images/damage-types-24/sleep.png"))
		self.paralysis = self.il.Add(wx.Bitmap("images/damage-types-24/paralysis.png"))
		self.blast = self.il.Add(wx.Bitmap("images/damage-types-24/blast.png"))
		self.stun = self.il.Add(wx.Bitmap("images/damage-types-24/stun.png"))

		self.damageTypes = {
			"Fire": self.fire,
			"Water": self.water,
			"Ice": self.ice,
			"Thunder": self.thunder,
			"Dragon": self.dragon,
			"Poison": self.poison,
			"Sleep": self.sleep,
			"Paralysis": self.paralysis,
			"Blast": self.blast,
			"Stun": self.stun,
		}

		self.summaryPanel.SetSizer(self.monsterSummarySizer)

		self.loadMonsterSummary(self.currentMonsterID)

	
	def loadMonsterSummary(self, monsterID: int) -> None:
		monster = """
			SELECT m.*, t.name, t.ecology, t.description, t.alt_state_description
			from monster m JOIN monster_text t USING (id)
			WHERE t.lang_id = :langId AND m.id = :id
			LIMIT 1
		"""

		conn = sqlite3.connect("mhw.db")
		data = conn.execute(monster, ("en", monsterID))
		data = data.fetchone()
	
		# 5 - has alt weakness
		# 6 - fire
		# 7 - water
		# 8 - ice
		# 9 - thunder
		# 10 - dragon
		# 11 - poison
		# 12 - sleep
		# 13 - paralysis
		# 14 - blast
		# 15 - stun
		# 16 - alt fire
		# 17 - alt water
		# 18 - alt ice
		# 19 - alt thunder
		# 20 - alt dragon
		# 21 - roar ailment
		# 22 - wind ailment
		# 23 - tremor ailment
		# -> 37 ailments
		
		monsterName = data[38]
		self.monsterSummaryNameLabel.SetLabelText(f"\n{monsterName}:\n{data[40]}") 
		self.monsterSummaryNameLabel.Wrap(700)

		weaknessElements = {
			"Fire": [6, 16],
			"Water": [7, 17],
			"Ice": [8, 18],
			"Thunder": [9, 19],
			"Dragon": [10, 20],
			}

		weaknessStatus = {
			"Poison": 11,
			"Sleep": 12, 
			"Paralysis": 13, 
			"Blast": 14, 
			"Stun": 15,
		}

		weaknessRating = {
			None: "",
			0: "☆☆☆",
			1: "★☆☆",
			2: "★★☆",
			3: "★★★",
		}

		root = self.summaryTree.AddRoot("Summary")
		# weaknesses
		self.monsterWeaknessNode = self.summaryTree.AppendItem(root, "Weakness")
		# ailments
		self.monsterAilmentsNode = self.summaryTree.AppendItem(root, "Ailments")
		# habitat
		self.monsterHabitatNode = self.summaryTree.AppendItem(root, "Habitat")

		if str(data[2]) != "small":
			for weakness, col in weaknessElements.items():
				if bool(data[5]):
					genericSummaryNode = self.summaryTree.AppendItem(self.monsterWeaknessNode, weakness)
					self.summaryTree.SetItemText(genericSummaryNode, weaknessRating[data[col[0]]] + " (" + str(weaknessRating[data[col[1]]]) + ")", 1)
					self.summaryTree.SetItemImage(genericSummaryNode, self.damageTypes[weakness], which=wx.TreeItemIcon_Normal) # IMAGES proper icons
					self.summaryTree.Expand(self.monsterWeaknessNode)
				else:
					genericSummaryNode = self.summaryTree.AppendItem(self.monsterWeaknessNode, weakness)
					self.summaryTree.SetItemText(genericSummaryNode, weaknessRating[data[col[0]]], 1)
					self.summaryTree.SetItemImage(genericSummaryNode, self.damageTypes[weakness], which=wx.TreeItemIcon_Normal) # IMAGES proper icons
					self.summaryTree.Expand(self.monsterWeaknessNode)

			for weakness, col in weaknessStatus.items():
				genericSummaryNode = self.summaryTree.AppendItem(self.monsterWeaknessNode, weakness)
				self.summaryTree.SetItemText(genericSummaryNode, weaknessRating[data[col]], 1)
				self.summaryTree.SetItemImage(genericSummaryNode, self.damageTypes[weakness], which=wx.TreeItemIcon_Normal) # TODIMAGESO proper icons
				self.summaryTree.Expand(self.monsterWeaknessNode)

			ailments = {
				"Roar": 21,
				"Wind": 22,
				"Tremor": 23,
				"Defense Down": 24,
				"Fire Blight": 25,
				"Water Blight":26,
				"Thunder Blight": 27,
				"Ice Blight": 28,
				"Dragon Blight": 29,
				"Blast Blight": 30,
				"Poison": 31,
				"Sleep": 32,
				"Paralysis": 33,
				"Bleed": 34,
				"Stun": 35,
				"Mud": 36,
				"Effluvia": 37,
			}

			textAilments = ["Roar", "Wind", "Tremor"]

			for ailment, col in ailments.items():
				if str(data[col]) == "None" or not bool(data[col]):
					pass
				else:
					genericSummaryNode = self.summaryTree.AppendItem(self.monsterAilmentsNode, ailment)
					if ailment not in textAilments:
						pass
					else:
						self.summaryTree.SetItemText(genericSummaryNode, data[col], 1)
					self.summaryTree.SetItemImage(genericSummaryNode, self.test, which = wx.TreeItemIcon_Normal) # IMAGES proper icons
			if self.summaryTree.GetChildrenCount(self.monsterAilmentsNode) == 0:
				genericSummaryNode = self.summaryTree.AppendItem(self.monsterAilmentsNode, "None")
			self.summaryTree.ExpandAll()

		habitats = """
			SELECT h.start_area, h.move_area, h.rest_area,
				lt.id location_id, lt.name location_name
			FROM monster_habitat h
				JOIN location_text lt
				ON lt.id = h.location_id
				AND lt.lang_id = :langId
			WHERE h.monster_id = :monsterId
			ORDER BY h.id
			"""

		data = conn.execute(habitats, ("en", monsterID))
		data = data.fetchall()
		# 0 - start area
		# 1 - move area
		# 2 - rest area
		# 3 - location id
		# 4 - location name

		for item in data:
			genericSummaryNode = self.summaryTree.AppendItem(self.monsterHabitatNode, str(item[4]))
			self.summaryTree.SetItemText(genericSummaryNode, str(item[0]) + " > " + str(item[1]) + " > " + str(item[2]), 1)
			try:
				self.summaryTree.SetItemImage(genericSummaryNode, self.locationIcons[item[4]], which = wx.TreeItemIcon_Normal)
			except:
				pass
			self.summaryTree.Expand(self.monsterHabitatNode)

	
	def initMonsterDamage(self):
		# physical damage grid
		self.physicalDamageTable = cgr.HeaderBitmapGrid(self.damagePanel)
		self.physicalDamageTable.CreateGrid(0, 5)
		self.physicalDamageTable.EnableEditing(False)
		self.physicalDamageTable.EnableDragRowSize(False)

		# element damage grid
		self.elementDamageTable = cgr.HeaderBitmapGrid(self.damagePanel)
		self.elementDamageTable.CreateGrid(0, 6)
		self.elementDamageTable.EnableEditing(False)
		self.elementDamageTable.EnableDragRowSize(False)

		# break damage grid
		self.breakDamageTable = cgr.HeaderBitmapGrid(self.damagePanel)
		self.breakDamageTable.CreateGrid(0, 5)
		self.breakDamageTable.EnableEditing(False)
		self.breakDamageTable.EnableDragRowSize(False)
		
		self.monsterDamageSizer.Add(self.physicalDamageTable, 1, wx.EXPAND)
		self.monsterDamageSizer.Add(self.elementDamageTable, 1, wx.EXPAND|wx.TOP, 5)
		self.monsterDamageSizer.Add(self.breakDamageTable, 1, wx.EXPAND|wx.TOP, 5)
		self.damagePanel.SetSizer(self.monsterDamageSizer)

		self.physicalDamageTable.SetColLabelValue(0, "Body Part")
		self.physicalDamageTable.SetColLabelAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
		self.physicalDamageTable.SetColLabelRenderer(1, cgr.HeaderBitmapColLabelRenderer(wx.Bitmap("images/damage-types-24/cut.png"), ""))
		self.physicalDamageTable.SetColLabelRenderer(2, cgr.HeaderBitmapColLabelRenderer(wx.Bitmap("images/damage-types-24/impact.png"), ""))
		self.physicalDamageTable.SetColLabelRenderer(3, cgr.HeaderBitmapColLabelRenderer(wx.Bitmap("images/damage-types-24/shot.png"), ""))
		self.physicalDamageTable.SetColLabelRenderer(4, cgr.HeaderBitmapColLabelRenderer(wx.Bitmap("images/damage-types-24/stun.png"), ""))
		self.physicalDamageTable.SetRowLabelSize(0)
		self.physicalDamageTable.SetColLabelSize(32)
		self.physicalDamageTable.SetColSize(0, 200)
		self.physicalDamageTable.SetDefaultCellAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER)

		self.elementDamageTable.SetColLabelValue(0, "Body Part")
		self.elementDamageTable.SetColLabelRenderer(1, cgr.HeaderBitmapColLabelRenderer(wx.Bitmap("images/damage-types-24/fire.png"), ""))
		self.elementDamageTable.SetColLabelRenderer(2, cgr.HeaderBitmapColLabelRenderer(wx.Bitmap("images/damage-types-24/water.png"), ""))
		self.elementDamageTable.SetColLabelRenderer(3, cgr.HeaderBitmapColLabelRenderer(wx.Bitmap("images/damage-types-24/ice.png"), ""))
		self.elementDamageTable.SetColLabelRenderer(4, cgr.HeaderBitmapColLabelRenderer(wx.Bitmap("images/damage-types-24/thunder.png"), ""))
		self.elementDamageTable.SetColLabelRenderer(5, cgr.HeaderBitmapColLabelRenderer(wx.Bitmap("images/damage-types-24/dragon.png"), ""))
		self.elementDamageTable.SetColLabelSize(32)
		self.elementDamageTable.SetRowLabelSize(0)
		self.elementDamageTable.SetColSize(0, 200)
		self.elementDamageTable.SetDefaultCellAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER)
		
		self.breakDamageTable.SetColLabelValue(0, "Body Part")
		self.breakDamageTable.SetColLabelValue(1, "Flinch") 
		self.breakDamageTable.SetColLabelValue(2, "Break")
		self.breakDamageTable.SetColLabelValue(3, "Sever")
		self.breakDamageTable.SetColLabelRenderer(4, cgr.HeaderBitmapColLabelRenderer(wx.Bitmap("images/damage-types-24/kinsect.png"), ""))
		self.breakDamageTable.SetColLabelSize(32)
		self.breakDamageTable.SetRowLabelSize(0)
		self.breakDamageTable.SetColSize(0, 200)
		self.breakDamageTable.SetDefaultCellAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER)
		
		self.loadMonsterDamage(self.currentMonsterID)


	def loadMonsterDamage(self, monsterID: int) -> None:
		conn = sqlite3.connect("mhw.db")
		
		sql = """
			SELECT h.*, pt.name body_part
			FROM monster_hitzone h
				JOIN monster_hitzone_text pt
					ON pt.id = h.id
					AND pt.lang_id = :langId
			WHERE h.monster_id = :monsterId
			ORDER BY h.id
		"""
		
		data = conn.execute(sql, ("en", monsterID))
		data = data.fetchall()
		
		hitzones = []
		for row in data:
			hitzones.append(m.Hitzone(row))

		for index, hit in enumerate(hitzones):
			self.physicalDamageTable.AppendRows(1)
			self.physicalDamageTable.SetCellValue(index, 0, hit.name)

			bold = self.physicalDamageTable.GetCellFont(index, 1).Bold()

			if hit.cut >= 45:
				self.physicalDamageTable.SetCellFont(index, 1, bold)
			self.physicalDamageTable.SetCellValue(index, 1, str(hit.cut))

			if hit.impact >= 45:
				self.physicalDamageTable.SetCellFont(index, 2, bold)
			self.physicalDamageTable.SetCellValue(index, 2, str(hit.impact))

			if hit.shot >= 45:
				self.physicalDamageTable.SetCellFont(index, 3, bold)
			self.physicalDamageTable.SetCellValue(index, 3, str(hit.shot))

			if str(hit.ko) != str(0):
				self.physicalDamageTable.SetCellValue(index, 4, str(hit.ko))

			self.elementDamageTable.AppendRows(1)
			self.elementDamageTable.SetCellValue(index, 0, str(hit.name))

			self.elementDamageTable.SetCellBackgroundColour(index, 1, util.hexToRGB(util.damageColors["fire"][hit.fire]))
			self.elementDamageTable.SetCellValue(index, 1, str(hit.fire))

			self.elementDamageTable.SetCellBackgroundColour(index, 2, util.hexToRGB(util.damageColors["water"][hit.water]))
			self.elementDamageTable.SetCellValue(index, 2, str(hit.water))

			self.elementDamageTable.SetCellBackgroundColour(index, 3, util.hexToRGB(util.damageColors["ice"][hit.ice]))
			self.elementDamageTable.SetCellValue(index, 3, str(hit.ice))

			self.elementDamageTable.SetCellBackgroundColour(index, 4, util.hexToRGB(util.damageColors["thunder"][hit.thunder]))
			self.elementDamageTable.SetCellValue(index, 4, str(hit.thunder))

			self.elementDamageTable.SetCellBackgroundColour(index, 5, util.hexToRGB(util.damageColors["dragon"][hit.dragon]))
			self.elementDamageTable.SetCellValue(index, 5, str(hit.dragon))

		sql = """
			SELECT b.flinch, b.wound, b.sever, b.extract, bt.part_name
			FROM monster_break b JOIN monster_break_text bt
				ON bt.id = b.id
			WHERE b.monster_id = :monsterId
				AND bt.lang_id = :langId
			ORDER BY b.id
		"""

		data = conn.execute(sql, (monsterID, "en"))
		data = data.fetchall()

		breaks = []
		for row in data:
			breaks.append(m.Break(row))

		for index, b in enumerate(breaks):
			self.breakDamageTable.AppendRows(1)
			self.breakDamageTable.SetCellValue(index, 0, b.name)
			if b.flinch != None:
				self.breakDamageTable.SetCellValue(index, 1, str(b.flinch))
			if b.wound != None:
				self.breakDamageTable.SetCellValue(index, 2, str(b.wound))
			if b.sever != None:
				self.breakDamageTable.SetCellValue(index, 3, str(b.sever))
			self.breakDamageTable.SetCellBackgroundColour(index, 4, util.hexToRGB(util.extractColors[b.extract]))
			self.breakDamageTable.SetCellValue(index, 4, f"{b.extract.capitalize()}")

		w, h = self.root.GetSize()
		self.root.SetSize(w - 1, h)
		self.root.SetSize(w, h)

	
	def initMonsterMaterials(self):
		self.materialsTree = wx.lib.agw.hypertreelist.HyperTreeList(self.materialsPanel, -1, style=0,
												agwStyle=
												gizmos.TR_DEFAULT_STYLE
												| gizmos.TR_TWIST_BUTTONS
												| gizmos.TR_ROW_LINES
												| gizmos.TR_COLUMN_LINES
												| gizmos.TR_NO_LINES
												| gizmos.TR_FULL_ROW_HIGHLIGHT
												| gizmos.TR_HIDE_ROOT
												)
		self.materialsTree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.onMaterialSelection)

		self.materialsTree.AddColumn("")
		self.materialsTree.AddColumn("")
		self.materialsTree.AddColumn("id")
		self.materialsTree.SetMainColumn(0)
		self.materialsTree.SetColumnWidth(0, (self.root.GetSize().width * 0.44) * 0.65)
		self.materialsTree.SetColumnWidth(1, (self.root.GetSize().width * 0.44) * 0.22)
		self.materialsTree.SetColumnAlignment(1, wx.ALIGN_CENTER)
		self.materialsTree.SetColumnWidth(2, 0)

		self.materialsTree.SetImageList(self.ilMats)

		self.monsterMaterialsSizer.Add(self.materialsTree, 1, wx.EXPAND)
		self.materialsPanel.SetSizer(self.monsterMaterialsSizer)

		self.loadMonsterMaterials(self.currentMonsterID)
	

	def loadMonsterMaterials(self, monsterID: int) -> None:
		root = self.materialsTree.AddRoot("Materials")
		
		# TODO only make the node if the monster exists in that rank

		# master rank
		#self.masterRankNode = self.materialsTree.AppendItem(root, "Master Rank")
		#masterRankColour = util.hexToRGB("#FFEB3B")
		#self.materialsTree.SetItemBackgroundColour(self.masterRankNode, masterRankColour)
		
		# high rank
		self.highRankNode = self.materialsTree.AppendItem(root, "High Rank")
		highRankColour = util.hexToRGB("#FB8C00")
		self.materialsTree.SetItemBackgroundColour(self.highRankNode, highRankColour)
		
		# low rank
		self.lowRankNode = self.materialsTree.AppendItem(root, "Low Rank")
		lowRankColour = util.hexToRGB("#4DD0E1")
		self.materialsTree.SetItemBackgroundColour(self.lowRankNode, lowRankColour)

		sql = """
			SELECT r.rank, ct.name condition_name, r.stack, r.percentage,
				i.id item_id, it.name item_name, i.icon_name item_icon_name, i.category item_category,
				i.icon_color item_icon_color
			FROM monster_reward r
				JOIN monster_reward_condition_text ct
					ON ct.id = r.condition_id
					AND ct.lang_id = :langId
				JOIN item i
					ON i.id = r.item_id
				JOIN item_text it
					ON it.id = i.id
					AND it.lang_id = :langId
			WHERE r.monster_id = :monsterId ORDER BY r.id
		"""

		conn = sqlite3.connect("mhw.db")
		data = conn.execute(sql, ("en", monsterID, ))
		data = data.fetchall()

		rewards = []
		for row in data:
			rewards.append(m.Reward(row))

		rewardCondition = 0
		monsterMaterial = 0
		categoriesLR = []
		categoriesHR = []
		categoriesMR = []
		rankNodes = {
			"LR": self.lowRankNode,
			"HR": self.highRankNode,
			#"MR": self.masterRankNode,
			}

		self.ilMats.RemoveAll()
		test = self.ilMats.Add(self.testIcon)
		#noLog = wx.LogNull()
	
		# TODO refactor into function
		for index, r in enumerate(rewards):
			if index == 0:
				self.currentMonsterMaterialID = r.itemID
			currentCategory = str(r.conditionName)
			if r.rank == "LR":
				if currentCategory in categoriesLR:
					monsterMaterial = self.materialsTree.AppendItem(rewardCondition,  str(r.itemName))
				else:
					rewardCondition = self.materialsTree.AppendItem(rankNodes[r.rank], str(r.conditionName))
					monsterMaterial = self.materialsTree.AppendItem(rewardCondition,  str(r.itemName))
				self.materialsTree.SetItemText(monsterMaterial, f"{r.stack} x {r.percentage}%", 1)
				self.materialsTree.SetItemText(monsterMaterial, str(r), 2)
				try:
					img = self.ilMats.Add(wx.Bitmap(f"images/materials-24/{r.iconName}{r.iconColor}.png"))
					self.materialsTree.SetItemImage(monsterMaterial, img, which=wx.TreeItemIcon_Normal)
				except:
					self.materialsTree.SetItemImage(monsterMaterial, test, which=wx.TreeItemIcon_Normal)
				categoriesLR.append(currentCategory)

			elif r.rank == "HR":
				if currentCategory in categoriesHR:
					monsterMaterial = self.materialsTree.AppendItem(rewardCondition,  str(r.itemName))
				else:
					rewardCondition = self.materialsTree.AppendItem(rankNodes[r.rank], str(r.conditionName))
					monsterMaterial = self.materialsTree.AppendItem(rewardCondition,  str(r.itemName))
				self.materialsTree.SetItemText(monsterMaterial, f"{r.stack} x {r.percentage}%", 1)
				self.materialsTree.SetItemText(monsterMaterial, str(r), 2)
				try:
					img = self.ilMats.Add(wx.Bitmap(f"images/materials-24/{r.iconName}{r.iconColor}.png"))
					self.materialsTree.SetItemImage(monsterMaterial, img, which=wx.TreeItemIcon_Normal)
				except:
					self.materialsTree.SetItemImage(monsterMaterial, test, which=wx.TreeItemIcon_Normal)
				categoriesHR.append(currentCategory)

			#elif r.rank == "MR":
			#	if currentCategory in categoriesMR:
			#		monsterMaterial = self.materialsTree.AppendItem(rewardCondition,  str(r.itemName))
			#	else:
			#		rewardCondition = self.materialsTree.AppendItem(rankNodes[r.rank], str(r.conditionName))
			#		monsterMaterial = self.materialsTree.AppendItem(rewardCondition,  str(r.itemName))
			#		self.materialsTree.SetItemBackgroundColour(rewardCondition, masterRankColour)
			#	self.materialsTree.SetItemBackgroundColour(monsterMaterial, masterRankColour)
			#	self.materialsTree.SetItemText(monsterMaterial, f"{r.stack} x {r.percentage}%", 1)
			#	self.materialsTree.SetItemText(monsterMaterial, str(r.itemID), 2)
			#	self.materialsTree.SetItemImage(monsterMaterial, self.test, which = wx.TreeItemIcon_Normal)
			#		
			#	categoriesMR.append(currentCategory)

		self.materialsTree.ExpandAll() 

		#del noLog

		# TODO maybe make this an option to auto expand a particular option or all of them
		#self.materialsTree.ExpandAllChildren()
		#self.materialsTree.Expand(self.masterRankNode)
		#
		#self.materialsTree.Expand(self.lowRankNode)


	def populateTree(self):
		pass
		# TODO just rewrite it


	def onSize(self, event):
		# TODO if monsterstab is selected then resize else dont
		width, height = self.root.GetSize()
		numOfColumns = 4
		numOfColumnsDamage = 14
		halfOfWindow = 3

		self.monstersTable.SetColSize(1, ((width / halfOfWindow) / numOfColumns + 30))
		self.monstersTable.SetColSize(2, ((width / halfOfWindow) / numOfColumns))
		self.monstersTable.SetColSize(3, ((width / halfOfWindow) / numOfColumns))
		self.monstersTable.SetColSize(4, ((width / halfOfWindow) / numOfColumns))

		# TODO adjust cols for summary tree
			
		# TODO adjust columns here and account for there being three tables now
		#for col in range(numOfColumnsDamage):
		#	self.damageTable.SetColSize(col, ((width * 0.66) / numOfColumnsDamage - 13))
		#	self.damageTable.SetColSize(0, ((width * 0.66) / numOfColumnsDamage + 80))

		# TODO set the splitter in property grid

		self.materialsTree.SetColumnWidth(0, (self.root.GetSize().width * 0.44) * 0.65)
		self.materialsTree.SetColumnWidth(1, (self.root.GetSize().width * 0.44) * 0.11)
		self.materialsTree.SetColumnWidth(2, (self.root.GetSize().width * 0.44) * 0.11)


	def onMaterialSelection(self, event):
		materialInfo = self.materialsTree.GetItemText(event.GetItem(), 2)
		materialInfo = materialInfo.replace("(", "").replace(")", "").replace("'", "").split(",")
		for i, item in enumerate(materialInfo):
			if item[0] == " ":
				materialInfo[i] = item[1:]
		self.link.event = True
		self.link.eventType = "item"
		self.link.item =  link.MonsterMaterialLink(materialInfo)
		self.root.followLink()
		self.link.reset()


	def onMonsterSelected(self, event):
		self.currentMonsterID = str(self.monsterList.GetItemText(event.GetEventObject().GetFirstSelected(), 1))
		self.currentMonsterName = str(self.monsterList.GetItemText(event.GetEventObject().GetFirstSelected(), 0))
		if self.currentMonsterID != "":
			self.monsterImage.LoadFile(f"images/monsters/160/{self.currentMonsterName}.png")
		else:
			self.monsterImage.LoadFile("images/monsters/160/Unknown.png")
		self.monsterImageLabel.SetBitmap(self.monsterImage)
		self.monsterImageLabel.SetSize((160, 160))

		self.physicalDamageTable.ClearGrid()
		try:
			self.physicalDamageTable.DeleteRows(0, self.physicalDamageTable.GetNumberRows())
		except:
			pass

		self.elementDamageTable.ClearGrid()
		try:
			self.elementDamageTable.DeleteRows(0, self.elementDamageTable.GetNumberRows())
		except:
			pass

		self.breakDamageTable.ClearGrid()
		try:
			self.breakDamageTable.DeleteRows(0, self.breakDamageTable.GetNumberRows())
		except:
			pass
		
		self.materialsTree.DeleteAllItems()
		self.summaryTree.DeleteAllItems()
		self.loadMonsterSummary(self.currentMonsterID)
		self.loadMonsterDamage(self.currentMonsterID)
		self.loadMonsterMaterials(self.currentMonsterID)

	
	def onMonsterSizeSelect(self, event):
		self.currentMonsterSize = event.GetEventObject().GetName()
		self.loadMonsterList()
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

wxColour = NewType("wxColour", None)
sqlite3Connection = NewType("sqlite3Connection", None)


class MonstersTab:

	def __init__(self, root, mainNotebook):
		self.root = root
		self.mainNotebook = mainNotebook
		
		self.currentMonsterID = 17 # nergigante
		self.currentMonsterMaterialID = 212 # nergigante : immortal dragon scale
		self.testIcon = wx.Bitmap("images/unknown.png", wx.BITMAP_TYPE_ANY) # REMOVE since youll be using specific icons

		self.initMonstersTab()
		self.loadData()
		self.initMonsterSummary() # TODO sort weaknesses from highest to low/none
		self.initMonsterDamage()
		self.initMonsterMaterials()

		# for loading monster's data in detailed view
		self.monstersTable.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.onMonsterSelect)
		# for scaling the columns
		self.monstersTable.Bind(wx.EVT_SIZE, self.onSize)

		# TEST defaults to materials tab
		# PREFERENCES make this customizable
		self.monsterDetailsNotebook.SetSelection(0)

		self.physicalDamagePane.Expand()
		self.elementDamagePane.Expand()
		self.breakDamagePane.Expand()

		self.damagePanel.SetVirtualSize(600, 1800)
		self.damagePanel.SetScrollRate(20,20)

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
		self.monstersTableSizer = wx.BoxSizer(wx.HORIZONTAL)
		# create monsters table and add bindings on selection and on size change of the main window
		self.monstersTable = wx.grid.Grid(self.monstersPanel)
		self.monstersTable.CreateGrid(56, 5) # TODO make the grid based of the monsters data
		# add left side sizer to the main sizer of the monsters tab
		self.monstersSizer.Add(self.monstersTableSizer, 0, wx.EXPAND)
		# add table to sizer
		self.monstersTableSizer.Add(self.monstersTable, 1, wx.EXPAND)

		# right side
		# sizer containing the monsters details
		self.monstersDetailedSizer = wx.BoxSizer(wx.VERTICAL)
		# create bitmap from image and load bitmap into a label
		conn = sqlite3.connect("MonsterHunter.db")
		data = conn.execute("SELECT name FROM monsters WHERE id = ?", (self.currentMonsterID, ))
		monsterIcon = data.fetchone()[0]
		self.monsterImage = wx.Bitmap("images/monsters/325/" + monsterIcon + ".png", wx.BITMAP_TYPE_ANY)
		self.monsterImageLabel = wx.StaticBitmap(self.monstersPanel, bitmap=self.monsterImage)
		# detailed view notebook
		self.monsterDetailsNotebook = wx.Notebook(self.monstersPanel)
		self.summaryPanel = wx.Panel(self.monsterDetailsNotebook)
		self.damagePanel = wx.ScrolledWindow(self.monsterDetailsNotebook)
		self.materialsPanel = wx.Panel(self.monsterDetailsNotebook)
		#
		self.monsterSummarySizer = wx.BoxSizer(wx.HORIZONTAL)
		self.monsterDetailsNotebook.AddPage(self.summaryPanel, "Summary")
		# 
		self.monsterDamageSizer = wx.BoxSizer(wx.VERTICAL)
		self.monsterDetailsNotebook.AddPage(self.damagePanel, "Damage")
		#
		self.monsterMaterialsSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.monsterDetailsNotebook.AddPage(self.materialsPanel, "Materials")
		# add the right side detailed view to the main size of the monsters notebook tab
		self.monstersSizer.Add(self.monstersDetailedSizer, 1, wx.EXPAND)
		# add widgets within to their parent sizer
		self.monstersDetailedSizer.Add(self.monsterImageLabel, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL | wx.ADJUST_MINSIZE, 10)
		self.monstersDetailedSizer.Add(self.monsterDetailsNotebook, 3, wx.EXPAND)

		# set sizer for the monsters notebook tab
		self.monstersPanel.SetSizer(self.monstersSizer)


	def initMonsterSummary(self):
		self.summaryTree = wx.lib.agw.hypertreelist.HyperTreeList(self.summaryPanel, -1, style=0, agwStyle=
												gizmos.TR_DEFAULT_STYLE
												| gizmos.TR_TWIST_BUTTONS
												| gizmos.TR_ROW_LINES
												| gizmos.TR_COLUMN_LINES
												| gizmos.TR_NO_LINES
												| gizmos.TR_FULL_ROW_HIGHLIGHT
												| gizmos.TR_HIDE_ROOT
												)

		self.summaryTree.AddColumn("")
		self.summaryTree.AddColumn("")
		self.summaryTree.SetMainColumn(0)
		self.summaryTree.SetColumnWidth(0, (self.root.GetSize().width * 0.45) * 0.34)
		self.summaryTree.SetColumnWidth(1, (self.root.GetSize().width * 0.45) * 0.27)

		isz = (24,24)
		self.il = wx.ImageList(isz[0], isz[1])

		self.testidx = self.il.Add(self.testIcon)

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

		self.summaryTree.SetImageList(self.il)

		self.monsterSummaryImageLabel = wx.StaticBitmap(self.summaryPanel, bitmap=wx.Bitmap("images/monsters/325/Nergigante.png"))
		self.monsterSummaryNameLabel = wx.StaticText(self.summaryPanel, label="Nergigante", style=wx.ALIGN_LEFT)
		self.monsterSummaryNameLabel.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False))
		self.monsterSummaryTypeLabel = wx.StaticText(self.summaryPanel, label="Elder Dragon", style=wx.ALIGN_LEFT)
		self.monsterSummaryTypeLabel.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT, False))
		self.monsterSummaryDescription = wx.StaticText(self.summaryPanel, label="testing\ntesting\ntesting", style=wx.ALIGN_LEFT)
		self.monsterSummaryDescription.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False))

		self.monsterSummaryLeftSizer = wx.BoxSizer(wx.VERTICAL)
		self.monsterSummaryRightSizer = wx.BoxSizer(wx.VERTICAL)

		self.monsterSummaryLeftSizer.Add(self.summaryTree, 1, wx.EXPAND)

		self.monsterSummaryRightSizer.Add(self.monsterSummaryImageLabel, 1, wx.ALIGN_CENTER)
		self.monsterSummaryRightSizer.Add(self.monsterSummaryNameLabel, wx.SizerFlags().Proportion(1).Border(wx.LEFT, 10))
		self.monsterSummaryRightSizer.Add(self.monsterSummaryTypeLabel, wx.SizerFlags().Proportion(1).Border(wx.LEFT, 20))
		self.monsterSummaryRightSizer.Add(self.monsterSummaryDescription, wx.SizerFlags().Proportion(18).Border(wx.LEFT, 30))

		self.monsterSummarySizer.Add(self.monsterSummaryLeftSizer, 1, wx.EXPAND)
		self.monsterSummarySizer.Add(self.monsterSummaryRightSizer, 1, wx.EXPAND)
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

		getName = sqlite3.connect("MonsterHunter.db")
		name = getName.execute("SELECT name FROM monsters WHERE id = :monsterID", (self.currentMonsterID, ))
		name = name.fetchone()
		monsterName = name[0]
		self.monsterSummaryImageLabel.SetBitmap(wx.Bitmap("images/monsters/256/" + str(monsterName) + ".png"))
		self.monsterSummaryNameLabel.SetLabelText(str(monsterName)) 
		self.monsterSummaryTypeLabel.SetLabelText(str(data[39]))
		self.monsterSummaryDescription.SetLabelText(str(data[40]))
		self.monsterSummaryDescription.Wrap(300)

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
						self.summaryTree.SetItemText(genericSummaryNode, "", 1)
					else:
						self.summaryTree.SetItemText(genericSummaryNode, data[col], 1)
					self.summaryTree.SetItemImage(genericSummaryNode, self.testidx, which = wx.TreeItemIcon_Normal) # IMAGES proper icons
					self.summaryTree.Expand(self.monsterAilmentsNode)

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
		self.physicalDamagePane = wx.CollapsiblePane(self.damagePanel, label="Physical")
		self.physicalDamagePaneSizer = wx.BoxSizer(wx.VERTICAL)
		self.physicalDamageTable = cgr.HeaderBitmapGrid(self.physicalDamagePane.GetPane())
		self.physicalDamageTable.CreateGrid(25, 5)
		self.physicalDamagePaneSizer.Add(self.physicalDamageTable, 0, wx.RIGHT|wx.LEFT|wx.EXPAND, 25)
		self.physicalDamagePane.GetPane().SetSizer(self.physicalDamagePaneSizer)
		self.physicalDamagePane.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.onPaneStateChanged)

		# element damage grid
		self.elementDamagePane = wx.CollapsiblePane(self.damagePanel, label="Element")
		self.elementDamagePaneSizer = wx.BoxSizer(wx.VERTICAL)
		self.elementDamageTable = cgr.HeaderBitmapGrid(self.elementDamagePane.GetPane())
		self.elementDamageTable.CreateGrid(25, 6)
		self.elementDamagePaneSizer.Add(self.elementDamageTable, 0, wx.RIGHT|wx.LEFT|wx.EXPAND, 25)
		self.elementDamagePane.GetPane().SetSizer(self.elementDamagePaneSizer)
		self.elementDamagePane.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.onPaneStateChanged)

		# break damage grid
		self.breakDamagePane = wx.CollapsiblePane(self.damagePanel, label="Break")
		self.breakDamagePaneSizer = wx.BoxSizer(wx.VERTICAL)
		self.breakDamageTable = cgr.HeaderBitmapGrid(self.breakDamagePane.GetPane())
		self.breakDamageTable.CreateGrid(15, 5)
		self.breakDamagePaneSizer.Add(self.breakDamageTable, 0, wx.RIGHT|wx.LEFT|wx.EXPAND, 25)
		self.breakDamagePane.GetPane().SetSizer(self.breakDamagePaneSizer)
		self.breakDamagePane.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.onPaneStateChanged)
		
		self.monsterDamageSizer.Add(self.physicalDamagePane, 0, wx.EXPAND)
		self.monsterDamageSizer.Add(self.elementDamagePane, 0, wx.EXPAND)
		self.monsterDamageSizer.Add(self.breakDamagePane, 0, wx.EXPAND)
		self.damagePanel.SetSizer(self.monsterDamageSizer)

		self.physicalDamageTable.SetColLabelValue(0, "Body Part")
		self.physicalDamageTable.SetColLabelAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
		self.physicalDamageTable.SetColLabelRenderer(1, cgr.HeaderBitmapColLabelRenderer("images/damage-types-24/cut.png", ""))
		self.physicalDamageTable.SetColLabelRenderer(2, cgr.HeaderBitmapColLabelRenderer("images/damage-types-24/impact.png", ""))
		self.physicalDamageTable.SetColLabelRenderer(3, cgr.HeaderBitmapColLabelRenderer("images/damage-types-24/shot.png", ""))
		self.physicalDamageTable.SetColLabelRenderer(4, cgr.HeaderBitmapColLabelRenderer("images/damage-types-24/stun.png", ""))
		self.physicalDamageTable.SetRowLabelSize(0)
		self.physicalDamageTable.SetColLabelSize(32)
		self.physicalDamageTable.SetColSize(0, 200)
		self.physicalDamageTable.SetDefaultCellAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER)

		self.elementDamageTable.SetColLabelValue(0, "Body Part")
		self.elementDamageTable.SetColLabelRenderer(1, cgr.HeaderBitmapColLabelRenderer("images/damage-types-24/fire.png", ""))
		self.elementDamageTable.SetColLabelRenderer(2, cgr.HeaderBitmapColLabelRenderer("images/damage-types-24/water.png", ""))
		self.elementDamageTable.SetColLabelRenderer(3, cgr.HeaderBitmapColLabelRenderer("images/damage-types-24/ice.png", ""))
		self.elementDamageTable.SetColLabelRenderer(4, cgr.HeaderBitmapColLabelRenderer("images/damage-types-24/thunder.png", ""))
		self.elementDamageTable.SetColLabelRenderer(5, cgr.HeaderBitmapColLabelRenderer("images/damage-types-24/dragon.png", ""))
		self.elementDamageTable.SetColLabelSize(32)
		self.elementDamageTable.SetRowLabelSize(0)
		self.elementDamageTable.SetColSize(0, 200)
		self.elementDamageTable.SetDefaultCellAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER)
		
		self.breakDamageTable.SetColLabelValue(0, "Body Part")
		self.breakDamageTable.SetColLabelValue(1, "Flinch") 
		self.breakDamageTable.SetColLabelValue(2, "Break")
		self.breakDamageTable.SetColLabelValue(3, "Sever")
		self.breakDamageTable.SetColLabelRenderer(4, cgr.HeaderBitmapColLabelRenderer("images/damage-types-24/kinsect.png", ""))
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

		# 2 - cut
		# 3 - impact
		# 4 - shot
		# 5 - fire
		# 6 - water
		# 7 - ice
		# 8 - thunder
		# 9 - dragon
		# 10 - ko
		# 11 - body part name
		
		weaknessData = conn.execute(sql, ("en", monsterID))

		for index, row in enumerate(weaknessData):
			self.physicalDamageTable.SetCellValue(index, 0, str(row[11]))
			self.physicalDamageTable.SetCellValue(index, 1, str(row[2]))
			self.physicalDamageTable.SetCellValue(index, 2, str(row[3]))
			self.physicalDamageTable.SetCellValue(index, 3, str(row[4]))
			if str(row[10]) != str(0):
				self.physicalDamageTable.SetCellValue(index, 4, str(row[10]))

			self.elementDamageTable.SetCellValue(index, 0, str(row[11]))
			self.elementDamageTable.SetCellValue(index, 1, str(row[5]))
			self.elementDamageTable.SetCellValue(index, 2, str(row[6]))
			self.elementDamageTable.SetCellValue(index, 3, str(row[7]))
			self.elementDamageTable.SetCellValue(index, 4, str(row[8]))
			self.elementDamageTable.SetCellValue(index, 5, str(row[9]))

		sql = """
			SELECT b.flinch, b.wound, b.sever, b.extract, bt.part_name
			FROM monster_break b JOIN monster_break_text bt
				ON bt.id = b.id
			WHERE b.monster_id = :monsterId
				AND bt.lang_id = :langId
			ORDER BY b.id
			"""

		# 0 - flinch
		# 1 - wound
		# 2 - sever
		# 3 - extract
		# 4 - body part name

		breakData = conn.execute(sql, (monsterID, "en"))

		for index, row in enumerate(breakData):
			self.breakDamageTable.SetCellValue(index, 0, str(row[4]))
			if row[0] != None:
				self.breakDamageTable.SetCellValue(index, 1, str(row[0]))
			if row[1] != None:
				self.breakDamageTable.SetCellValue(index, 2, str(row[1]))
			if row[2] != None:
				self.breakDamageTable.SetCellValue(index, 3, str(row[2]))
			self.breakDamageTable.SetCellValue(index, 4, str(row[3]))

	
	def initMonsterMaterials(self):
		self.materialsTree = wx.lib.agw.hypertreelist.HyperTreeList(self.materialsPanel, -1, style=0, agwStyle=
												gizmos.TR_DEFAULT_STYLE
												| gizmos.TR_TWIST_BUTTONS
												| gizmos.TR_ROW_LINES
												| gizmos.TR_COLUMN_LINES
												| gizmos.TR_NO_LINES
												| gizmos.TR_FULL_ROW_HIGHLIGHT
												| gizmos.TR_HIDE_ROOT
												)

		self.materialsTree.Bind(wx.EVT_TREE_SEL_CHANGED, self.onMaterialSelection)

		self.materialsTree.AddColumn("")
		self.materialsTree.AddColumn("#")
		self.materialsTree.AddColumn("%")
		self.materialsTree.AddColumn("id")
		self.materialsTree.SetMainColumn(0)
		self.materialsTree.SetColumnWidth(0, (self.root.GetSize().width * 0.44) * 0.65)
		self.materialsTree.SetColumnWidth(1, (self.root.GetSize().width * 0.44) * 0.11)
		self.materialsTree.SetColumnWidth(2, (self.root.GetSize().width * 0.44) * 0.11)
		self.materialsTree.SetColumnWidth(3, 0)

		self.materialsTree.SetImageList(self.il)

		self.initMaterialDetail()

		self.monsterMaterialsSizer.Add(self.materialsTree, 2, wx.EXPAND)
		self.monsterMaterialsSizer.Add(self.materialDetailPanel, 1, wx.EXPAND)
		self.materialsPanel.SetSizer(self.monsterMaterialsSizer)

		self.loadMonsterMaterials(self.currentMonsterID)

	def initMaterialDetail(self):
		self.materialDetailPanel = wx.Panel(self.materialsPanel)
		self.materialDetailSizer = wx.BoxSizer(wx.VERTICAL)
		self.materialImage = wx.Bitmap("util/VectorDrawable2Svg-master/png/ic_items_scale_base128.png", wx.BITMAP_TYPE_ANY)
		self.materialImageLabel = wx.StaticBitmap(self.materialDetailPanel, bitmap=self.materialImage)

		self.materialDetailsPropertyGrid = wxpg.PropertyGridManager(self.materialDetailPanel, style=wxpg.PG_TOOLBAR)

		self.initMaterialData(self.currentMonsterMaterialID)

		self.materialDetailSizer.Add(self.materialImageLabel, 1, wx.EXPAND)
		self.materialDetailSizer.Add(self.materialDetailsPropertyGrid, 3, wx.EXPAND)

		self.materialDetailPanel.SetSizer(self.materialDetailSizer)
	

	def loadMonsterMaterials(self, monsterID: int) -> None:
		root = self.materialsTree.AddRoot("Materials")

		# master rank
		self.masterRankNode = self.materialsTree.AppendItem(root, "Master Rank")
		masterRankColour = wx.Colour(255, 230, 0)
		self.materialsTree.SetItemBackgroundColour(self.masterRankNode, wx.Colour(255, 230, 0))
		
		# high rank
		self.highRankNode = self.materialsTree.AppendItem(root, "High Rank")
		highRankColour = wx.Colour(255, 140, 0)
		self.materialsTree.SetItemBackgroundColour(self.highRankNode, wx.Colour(255, 140, 0))
		
		# low rank
		self.lowRankNode = self.materialsTree.AppendItem(root, "Low Rank")
		lowRankColour = wx.Colour(30, 190, 255)
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

		rewardCondition = 0
		monsterMaterial = 0
		categoriesLR = []
		categoriesHR = []
		categoriesMR = []
		rankNodes = {
			"LR": self.lowRankNode,
			"HR": self.highRankNode,
			"MR": self.masterRankNode,
			}
	
		# TODO refactor into function
		for index, row in enumerate(data):
			if index == 0:
				self.currentMonsterMaterialID = row[4]
			currentCategory = str(row[1])
			if row[0] == "LR":
				if currentCategory in categoriesLR:
					monsterMaterial = self.materialsTree.AppendItem(rewardCondition,  str(row[5]))
					self.materialsTree.SetItemText(monsterMaterial, str(row[2]), 1)
					self.materialsTree.SetItemText(monsterMaterial, str(row[3]), 2)
					self.materialsTree.SetItemText(monsterMaterial, str(row[4]), 3)
					self.materialsTree.SetItemImage(monsterMaterial, self.testidx, which = wx.TreeItemIcon_Normal) # IMAGES proper icons
					self.materialsTree.SetItemBackgroundColour(monsterMaterial, lowRankColour)
				else:
					rewardCondition = self.materialsTree.AppendItem(rankNodes[row[0]], str(row[1]))
					monsterMaterial = self.materialsTree.AppendItem(rewardCondition,  str(row[5]))
					self.materialsTree.SetItemText(monsterMaterial, str(row[2]), 1)
					self.materialsTree.SetItemText(monsterMaterial, str(row[3]), 2)
					self.materialsTree.SetItemText(monsterMaterial, str(row[4]), 3)
					self.materialsTree.SetItemImage(monsterMaterial, self.testidx, which = wx.TreeItemIcon_Normal) # IMAGES proper icons
					self.materialsTree.SetItemBackgroundColour(rewardCondition, lowRankColour)
					self.materialsTree.SetItemBackgroundColour(monsterMaterial, lowRankColour)

				categoriesLR.append(currentCategory)

			elif row[0] == "HR":
				if currentCategory in categoriesHR:
					monsterMaterial = self.materialsTree.AppendItem(rewardCondition,  str(row[5]))
					self.materialsTree.SetItemText(monsterMaterial, str(row[2]), 1)
					self.materialsTree.SetItemText(monsterMaterial, str(row[3]), 2)
					self.materialsTree.SetItemText(monsterMaterial, str(row[4]), 3)
					self.materialsTree.SetItemImage(monsterMaterial, self.testidx, which = wx.TreeItemIcon_Normal) # IMAGES proper icons
					self.materialsTree.SetItemBackgroundColour(monsterMaterial, highRankColour)
				else:
					rewardCondition = self.materialsTree.AppendItem(rankNodes[row[0]], str(row[1]))
					monsterMaterial = self.materialsTree.AppendItem(rewardCondition,  str(row[5]))
					self.materialsTree.SetItemText(monsterMaterial, str(row[2]), 1)
					self.materialsTree.SetItemText(monsterMaterial, str(row[3]), 2)
					self.materialsTree.SetItemText(monsterMaterial, str(row[4]), 3)
					self.materialsTree.SetItemImage(monsterMaterial, self.testidx, which = wx.TreeItemIcon_Normal) # IMAGES proper icons
					self.materialsTree.SetItemBackgroundColour(rewardCondition, highRankColour)
					self.materialsTree.SetItemBackgroundColour(monsterMaterial, highRankColour)

				categoriesHR.append(currentCategory)

			elif row[0] == "MR":
				if currentCategory in categoriesMR:
					monsterMaterial = self.materialsTree.AppendItem(rewardCondition,  str(row[5]))
					self.materialsTree.SetItemText(monsterMaterial, str(row[2]), 1)
					self.materialsTree.SetItemText(monsterMaterial, str(row[3]), 2)
					self.materialsTree.SetItemText(monsterMaterial, str(row[4]), 3)
					self.materialsTree.SetItemImage(monsterMaterial, self.testidx, which = wx.TreeItemIcon_Normal) # IMAGES proper icons
					self.materialsTree.SetItemBackgroundColour(monsterMaterial, masterRankColour)
				else:
					rewardCondition = self.materialsTree.AppendItem(rankNodes[row[0]], str(row[1]))
					monsterMaterial = self.materialsTree.AppendItem(rewardCondition,  str(row[5]))
					self.materialsTree.SetItemText(monsterMaterial, str(row[2]), 1)
					self.materialsTree.SetItemText(monsterMaterial, str(row[3]), 2)
					self.materialsTree.SetItemText(monsterMaterial, str(row[4]), 3)
					self.materialsTree.SetItemImage(monsterMaterial, self.testidx, which = wx.TreeItemIcon_Normal) # IMAGES proper icons
					self.materialsTree.SetItemBackgroundColour(rewardCondition, masterRankColour)
					self.materialsTree.SetItemBackgroundColour(monsterMaterial, masterRankColour)

				categoriesMR.append(currentCategory)

		self.materialsTree.ExpandAll()

		# TODO maybe make this an option to auto expand a particular option or all of them
		#self.materialsTree.Expand(self.masterRankNode)
		#self.materialsTree.Expand(self.highRankNode) 
		#self.materialsTree.Expand(self.lowRankNode)


	# work in progress
	# TODO think of a better layout for the data
	def addMaterialToRank(self, dataRow, rankString: str, rankCategoriesList: List[str], rankColor: wxColour) -> None:
		print(type(dataRow))
		if dataRow[0] == rankString:
			if currentCategory in rankCategoriesList:
				monsterMaterial = self.materialsTree.AppendItem(rewardCondition,  str(dataRow[5]))
				self.materialsTree.SetItemText(monsterMaterial, str(dataRow[2]), 1)
				self.materialsTree.SetItemText(monsterMaterial, str(dataRow[3]), 2)
				self.materialsTree.SetItemImage(monsterMaterial, self.testidx, which = wx.TreeItemIcon_Normal) # IMAGES proper icons
				self.materialsTree.SetItemBackgroundColour(monsterMaterial, rankColor)
			else:
				rewardCondition = self.materialsTree.AppendItem(rankNodes[dataRow[0]], str(dataRow[1]))
				monsterMaterial = self.materialsTree.AppendItem(rewardCondition,  str(dataRow[5]))
				self.materialsTree.SetItemText(monsterMaterial, str(dataRow[2]), 1)
				self.materialsTree.SetItemText(monsterMaterial, str(dataRow[3]), 2)
				self.materialsTree.SetItemImage(monsterMaterial, self.testidx, which = wx.TreeItemIcon_Normal) # IMAGES proper icons
				self.materialsTree.SetItemBackgroundColour(rewardCondition, rankColor)
				self.materialsTree.SetItemBackgroundColour(monsterMaterial, rankColor)
				self.materialsTree.Expand(rewardCondition)

			rankCategoriesList.append(currentCategory)


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
		
	
	# TODO when notebook is changed to monsters tab then call the contents of onSize
	

	def loadData(self):
		conn = sqlite3.connect("MonsterHunter.db")
		data = conn.execute("SELECT * FROM monsters ORDER by size DESC, name ASC ")
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
		self.monstersTable.SetColLabelSize(30)
		self.monstersTable.HideCol(0)


	def onMaterialSelection(self, event):
		itemID = self.materialsTree.GetItemText(event.GetItem(), 3)
		conn = sqlite3.connect("mhw.db")

		itemInfo = self.loadMonsterMaterialsummaryPage(itemID, conn)
		itemObtaining = self.loadMaterialObtainingPage(itemID, conn)
		itemUsage = self.loadMaterialUsagePage(itemID, conn)
		# PREFERENCES remember the last selected page and select it
		self.materialDetailsPropertyGrid.Clear()
		self.loadMaterialPropertyGrid(itemInfo, itemObtaining, itemUsage)

	def initMaterialData(self, itemID: int) -> None:
		itemID = str(itemID)
		conn = sqlite3.connect("mhw.db")

		itemInfo = self.loadMonsterMaterialsummaryPage(itemID, conn)
		itemObtaining = self.loadMaterialObtainingPage(itemID, conn)
		itemUsage = self.loadMaterialUsagePage(itemID, conn)
		self.loadMaterialPropertyGrid(itemInfo, itemObtaining, itemUsage)

	def loadMonsterMaterialsummaryPage(self, itemID: int, conn: sqlite3Connection) -> List[str]:
		itemDetails = """
			SELECT i.*, it.name, it.description
			FROM item i
			JOIN item_text it
				ON it.id = i.id
				AND it.lang_id = :langId
			WHERE i.id = :itemId
			"""
		
		data = conn.execute(itemDetails, ("en", itemID))
		data = data.fetchone()
		itemInfo = []
		for item in data:
			itemInfo.append(item)

		# 0 - item id
		# 1 - item type ie material
		# 2 - subcategory ie trade, supply, account
		# 3 - rarity
		# 4 - buy price
		# 5 - sell price
		# 6 - carry limit
		# 7 - points
		# 8 - icon type ie scale
		# 9 - icon color ie Gray
		# 10 - item name ie immortal dragon scale
		# 11- item desc ei Rare Nergigante material. Mostly obtained...
		
		return itemInfo

	
	def loadMaterialUsagePage(self, itemID: int, conn: sqlite3Connection) -> List[List[str]]:
		# more specifically this: List[List[str], List[str], List[str]]

		charmUsage = """
			SELECT c.id, c.rarity, c.previous_id, ctext.name, cr.quantity
			FROM charm_recipe cr
				JOIN charm c
					ON c.id = cr.charm_id
				JOIN charm_text ctext
					ON ctext.id = c.id
			WHERE cr.item_id = :itemId
			AND ctext.lang_id = :langId
			"""

		armorUsage = """
			SELECT armor_id id, name, armor_type, rarity, slot_1, slot_2, slot_3, ar.quantity
			FROM armor_recipe ar
				JOIN armor a
					ON ar.armor_id = a.id
				JOIN armor_text atext
					ON a.id = atext.id
			WHERE ar.item_id = :itemId
				AND atext.lang_id = :langId
			"""

		weaponUsage = """
			SELECT w.id, w.rarity, w.weapon_type, w.category, wt.*, wr.quantity
			FROM weapon w
				JOIN weapon_text wt USING (id)
				JOIN weapon_recipe wr ON w.id = wr.weapon_id
			WHERE wt.lang_id = :langId
				AND wr.item_id = :itemId
			"""
		
		data = conn.execute(charmUsage, (itemID, "en"))
		data = data.fetchall()
		charmUsage = []

		for row in data:
			charmUsage.append(row)

		# 0 - charm id
		# 1 - rarity
		# 2 - previous charm level id
		# 3 - charm name
		# 4 - required quantity

		data = conn.execute(armorUsage, (itemID, "en"))
		data = data.fetchall()
		armorUsage = []

		for row in data:
			armorUsage.append(row)

		# 0 - armor id
		# 1 - armor name
		# 2 - armor type
		# 3 - rarity
		# 4 - slot 1
		# 5 - slot 2
		# 6 - slot 3
		# 7 - required quantity

		data = conn.execute(weaponUsage, ("en", itemID))
		data = data.fetchall()
		weaponUsage = []

		for row in data:
			weaponUsage.append(row)

		# 0 - weapon id
		# 1 - rarity
		# 2 - weapon type
		# 3 - weapon category??
		# 4 - weapon id duplicate
		# 5 - lang id
		# 6 - weapon name
		# 7 - required quantity
		
		return [charmUsage, armorUsage, weaponUsage]


	# TODO missing return type!
	def loadMaterialObtainingPage(self, itemID: int, conn: sqlite3Connection):
		itemRewards = """
			SELECT r.monster_id, mtext.name monster_name, m.size monster_size,
				rtext.name condition_name, r.rank, r.stack, r.percentage
			FROM monster_reward r
				JOIN monster_reward_condition_text rtext
					ON rtext.id = r.condition_id
				JOIN monster m
					ON m.id = r.monster_id
				JOIN monster_text mtext
					ON mtext.id = m.id
					AND mtext.lang_id = rtext.lang_id
			WHERE r.item_id = :itemId
				AND rtext.lang_id = :langId
				ORDER BY m.id ASC, r.percentage DESC
			"""

		data = conn.execute(itemRewards, (itemID, "en"))
		data = data.fetchall()
		itemObtaining = []

		for row in data:
			itemObtaining.append(row)

		# 0 - monster id
		# 1 - monster name
		# 2 - monster size
		# 3 - reward condition
		# 4 - rank
		# 5 - stack
		# 6 - percentage
		
		return itemObtaining

	
	def loadMaterialPropertyGrid(self, itemInfo, itemObtaining, itemUsage):
		for index, item in enumerate(itemInfo):
			if str(item) == "None" or str(item) == "0":
				itemInfo[index] = "-"
			else:
				itemInfo[index] = str(item)
				
		# IMAGES replace icon with item icon probably base scale
		self.summaryMaterialPage = self.materialDetailsPropertyGrid.AddPage("Summary", self.testIcon)
		self.summaryMaterialPage.Append(wxpg.PropertyCategory("Summary"))
		self.summaryMaterialPage.Append(wxpg.StringProperty("Name",value=itemInfo[10]))
		self.summaryMaterialPage.Append(wxpg.LongStringProperty("Description",value=itemInfo[11]))
		self.summaryMaterialPage.Append(wxpg.StringProperty("Rarity",value=itemInfo[3]))
		self.summaryMaterialPage.Append(wxpg.StringProperty("Buy",value=itemInfo[4]))
		if itemInfo[5] == "-":	
			# IMAGES points icon
			self.summaryMaterialPage.Append(wxpg.StringProperty("Sell",value=itemInfo[7]))
		else:
			# IMAGES zenny icon
			self.summaryMaterialPage.Append(wxpg.StringProperty("Sell",value=itemInfo[5]))
		self.summaryMaterialPage.Append(wxpg.StringProperty("Carry",value=itemInfo[6]))

		self.summaryMaterialPage.SetSplitterLeft()

		# IMAGES replace icon with armor icon probably base chest or head
		self.usageMaterialPage = self.materialDetailsPropertyGrid.AddPage("Usage", self.testIcon)
		self.usageMaterialPage.Append(wxpg.PropertyCategory("Usage"))
		if itemUsage[0]:
			self.usageMaterialPage.AppendIn(wxpg.PGPropArgCls("Usage"), wxpg.PropertyCategory("Charms"))
			for item in itemUsage[0]:
				self.usageMaterialPage.Append(wxpg.StringProperty(str(item[3]),value=str(item[4])))
		if itemUsage[1]:
			self.usageMaterialPage.AppendIn(wxpg.PGPropArgCls("Usage"), wxpg.PropertyCategory("Armor"))
			for item in itemUsage[1]:
				self.usageMaterialPage.Append(wxpg.StringProperty(str(item[1]),value=str(item[7])))
		if itemUsage[2]:
			self.usageMaterialPage.AppendIn(wxpg.PGPropArgCls("Usage"), wxpg.PropertyCategory("Weapons"))
			for item in itemUsage[2]:
				self.usageMaterialPage.Append(wxpg.StringProperty(str(item[6]),value=str(item[7])))
		self.usageMaterialPage.SetSplitterLeft()

		# IMAGES replace icon with unknow monster icon
		self.obtainingMaterialPage = self.materialDetailsPropertyGrid.AddPage("Obtaining", self.testIcon)
		self.obtainingMaterialPage.Append(wxpg.PropertyCategory("Obtaining"))
		for item in itemObtaining:
			self.obtainingMaterialPage.AppendIn(wxpg.PGPropArgCls("Obtaining"), wxpg.PropertyCategory(str(item[1])))
			try:
				self.obtainingMaterialPage.Append(wxpg.StringProperty(str(item[4]) + " " + str(item[3]),value=str(item[5]) + " x " + str(item[6]) + "%"))
			except:
				pass

		self.obtainingMaterialPage.SetSplitterLeft()


	def onPaneStateChanged(self, event):
		if self.physicalDamagePane.IsCollapsed() and self.elementDamagePane.IsCollapsed() and self.breakDamagePane.IsCollapsed():
			self.damagePanel.SetVirtualSize(self.damagePanel.GetSize()[0], self.damagePanel.GetSize()[1])
		else:
			self.damagePanel.SetVirtualSize(self.damagePanel.GetSize()[0], self.damagePanel.GetSize()[1] + 1000)
		self.damagePanel.Layout()


	def onMonsterSelect(self, event):
		if str(self.monstersTable.GetCellValue(event.GetRow(), 1)) != "":
			self.monsterImage.LoadFile("images/monsters/325/" + str(self.monstersTable.GetCellValue(event.GetRow(), 1)) + ".png")
		else:
			self.monsterImage.LoadFile("images/monsters/325/Unknown.png")
		self.monsterImageLabel.SetBitmap(self.monsterImage)
		self.physicalDamageTable.ClearGrid()
		self.elementDamageTable.ClearGrid()
		self.breakDamageTable.ClearGrid()
		self.materialsTree.DeleteAllItems()
		self.summaryTree.DeleteAllItems()
		self.currentMonsterID = self.monstersTable.GetCellValue(event.GetRow(), 0)
		self.loadMonsterSummary(self.currentMonsterID)
		self.loadMonsterDamage(self.currentMonsterID)
		self.loadMonsterMaterials(self.currentMonsterID)
import wx
import wx.grid
import wx.lib.gizmos as gizmos
import customGridRenderer as cgr
import wx.propgrid as wxpg
import sqlite3


class Application(wx.Frame):

	def __init__(self, *args, **kw):
		super(Application, self).__init__(*args, **kw)

		icon = wx.Icon("images/OfflineDatabase.ico")
		self.SetIcon(icon)
		self.SetSize(1200, 1000)
		self.SetTitle("Database")
		self.resolutionWidth, self.resolutionHeight = wx.DisplaySize()
		self.currentMonsterID = 43 # nergigante
		self.currentMonsterMaterialID = 412 # nergigante : immortal dragon scale
		self.testIcon = wx.Bitmap("Nergigante32.png", wx.BITMAP_TYPE_ANY) # TODO remove

		self.initMainNotebook()
		self.initMonstersTab()
		self.weaponsFrame = wx.Panel(self.mainNotebook) # TODO move to weapons init
		self.mainNotebook.AddPage(self.weaponsFrame, "Weapons") # TODO move to weapons init!
		self.makeMenuBar()
		self.CreateStatusBar()

		self.SetStatusText("Welcome to wxPython!")
		self.loadData()
		self.initDamage()
		self.initMaterials()

		# for loading monster's data in detailed view
		self.monstersTable.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.onMonsterSelect)
		# for scaling the columns
		self.monstersTable.Bind(wx.EVT_SIZE, self.onSize)

		# to trigger onSize event so the table looks as it should
		self.SetSize(1199, 1000)
		# roughly center
		self.SetPosition(wx.Point(self.resolutionWidth / 1.4 - self.GetSize().width, self.resolutionHeight / 1.5 - self.GetSize().height / 1.3))

		# TEST materials tab
		self.monsterDetailsNotebook.SetSelection(2)

		self.usageMaterialPage.SetSplitterLeft() # TODO remove?
		self.obtainingMaterialPage.SetSplitterLeft()

		self.SetSize(1200, 1000)


	def initMainNotebook(self):
		# the outermost panel holding in all the widgets
		self.mainPanel = wx.Panel(self)
		# main geometry manager
		self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
		# main notebook holding the top tabs ie: monsters, weapons etc.
		self.mainNotebook = wx.Notebook(self.mainPanel)
		# add notebook to sizer
		self.mainSizer.Add(self.mainNotebook, 1, wx.EXPAND)

		# set the sizer for mainWindow
		self.mainPanel.SetSizer(self.mainSizer)


	def initMonstersTab(self):
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
		conn = sqlite3.connect("../MonsterHunterWorld/MonsterHunter.db")
		data = conn.execute("SELECT name FROM monsters WHERE id = ?", (self.currentMonsterID, ))
		monsterIcon = data.fetchone()[0]
		self.monsterImage = wx.Bitmap("images/monsters/256/" + monsterIcon + ".png", wx.BITMAP_TYPE_ANY)
		self.monsterImageLabel = wx.StaticBitmap(self.monstersPanel, bitmap=self.monsterImage)
		# detailed view notebook
		self.monsterDetailsNotebook = wx.Notebook(self.monstersPanel)
		self.overviewPanel = wx.Panel(self.monsterDetailsNotebook)
		self.damagePanel = wx.Panel(self.monsterDetailsNotebook)
		self.materialsPanel = wx.Panel(self.monsterDetailsNotebook)
		self.monsterDetailsNotebook.AddPage(self.overviewPanel, "Overview")
		# 
		self.monsterDamageSizer = wx.BoxSizer(wx.VERTICAL)
		self.monsterDetailsNotebook.AddPage(self.damagePanel, "Damage")
		#
		self.monsterMaterialsSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.monsterDetailsNotebook.AddPage(self.materialsPanel, "Materials")
		# add the right side detailed view to the main size of the monsters notebook tab
		self.monstersSizer.Add(self.monstersDetailedSizer, 1, wx.EXPAND)
		# add widgets within to their parent sizer
		self.monstersDetailedSizer.Add(self.monsterImageLabel, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL | wx.ADJUST_MINSIZE, 10)
		self.monstersDetailedSizer.Add(self.monsterDetailsNotebook, 1, wx.EXPAND)

		# set sizer for the monsters notebook tab
		self.monstersPanel.SetSizer(self.monstersSizer)

	
	def initDamage(self):
		self.damageTable = cgr.HeaderBitmapGrid(self.damagePanel)
		self.damageTable.CreateGrid(35, 14)
		self.monsterDamageSizer.Add(self.damageTable, 1, wx.EXPAND)
		self.damagePanel.SetSizer(self.monsterDamageSizer)

		self.damageTable.SetColLabelAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)

		self.damageTable.SetColLabelRenderer(1, cgr.HeaderBitmapColLabelRenderer("images/damage types/cut.png"))
		self.damageTable.SetColLabelRenderer(2, cgr.HeaderBitmapColLabelRenderer("images/damage types/impact.png"))
		self.damageTable.SetColLabelRenderer(3, cgr.HeaderBitmapColLabelRenderer("images/damage types/shot.png"))
		self.damageTable.SetColLabelRenderer(4, cgr.HeaderBitmapColLabelRenderer("images/damage types/fire.png"))
		self.damageTable.SetColLabelRenderer(5, cgr.HeaderBitmapColLabelRenderer("images/damage types/water.png"))
		self.damageTable.SetColLabelRenderer(6, cgr.HeaderBitmapColLabelRenderer("images/damage types/ice.png"))
		self.damageTable.SetColLabelRenderer(7, cgr.HeaderBitmapColLabelRenderer("images/damage types/thunder.png"))
		self.damageTable.SetColLabelRenderer(8, cgr.HeaderBitmapColLabelRenderer("images/damage types/dragon.png"))
		self.damageTable.SetColLabelRenderer(9, cgr.HeaderBitmapColLabelRenderer("images/damage types/stun.png"))
		self.damageTable.SetColLabelRenderer(13, cgr.HeaderBitmapColLabelRenderer("images/kinsect.png"))

		"""for num in range(1, 13):
			self.damageTable.SetColLabelRenderer(num, HeaderBitmapColLabelRenderer("images/VectorDrawable2Svg-master/png2/32/ic_equipment_dual_blades_rarity_" + str(num) + ".xml.svg.png"))
		self.damageTable.SetColLabelRenderer(1, HeaderBitmapColLabelRenderer("images/VectorDrawable2Svg-master/png2/trans.png"))"""

		self.damageTable.SetRowLabelSize(0)
		self.damageTable.SetColLabelSize(32)
		self.damageTable.SetColLabelValue(0, "Body Part")

		for num in range(1, 14):
			self.damageTable.SetColLabelValue(num, "")
		self.damageTable.SetColLabelValue(10, "FLN") 
		self.damageTable.SetColLabelValue(11, "BRK")
		self.damageTable.SetColLabelValue(12, "SVR")

		self.loadDamage(self.currentMonsterID)


	def loadDamage(self, monsterID):
		conn = sqlite3.connect("../MonsterHunterWorld/mhw.db")
		data = conn.execute("SELECT id FROM monster_hitzone WHERE monster_id = ?", (monsterID, ))
		bodyPartID = []
		bodyPartRow = {}

		for row in data:
			bodyPartID.append(row[0])

		dataWeak = conn.execute("SELECT cut, impact, shot, ko, fire, water, ice, thunder, dragon FROM monster_hitzone WHERE monster_id = ?", (monsterID, ))
		dataBreak = conn.execute("SELECT flinch, wound, sever, extract FROM monster_break WHERE monster_id = ?", (monsterID, ))

		bodyPartName = []
		for id in bodyPartID:
			data2 = conn.execute("SELECT name FROM monster_hitzone_text WHERE id = ?", (id, ))
			name = data2.fetchone()
			bodyPartName.append(name[0])

		i = 0
		for row in dataWeak:
			self.damageTable.SetCellValue(i, 0, str(bodyPartName[i]))
			self.damageTable.SetCellValue(i, 1, str(row[0]))
			self.damageTable.SetCellValue(i, 2, str(row[1]))
			self.damageTable.SetCellValue(i, 3, str(row[2]))
			self.damageTable.SetCellValue(i, 4, str(row[3]))
			self.damageTable.SetCellValue(i, 5, str(row[4]))
			self.damageTable.SetCellValue(i, 6, str(row[5]))
			self.damageTable.SetCellValue(i, 7, str(row[6]))
			self.damageTable.SetCellValue(i, 8, str(row[7]))
			self.damageTable.SetCellValue(i, 9, str(row[8]))
			bodyPartRow[bodyPartName[i]] = i
			bodyPartRow[bodyPartName[i] + "s"] = i
			i += 1

		###
		data = conn.execute("SELECT id FROM monster_break WHERE monster_id = ?", (monsterID, ))
		bodyPartID = []

		for row in data:
			bodyPartID.append(row[0])

		bodyPartName = []
		for id in bodyPartID:
			data2 = conn.execute("SELECT part_name FROM monster_break_text WHERE id = ?", (id, ))
			name = data2.fetchone()
			bodyPartName.append(name[0])


		j = 0
		for row in dataBreak:
			self.damageTable.SetCellValue(i, 0, str(bodyPartName[j]))
			self.damageTable.SetCellValue(i, 10, str(row[0]))
			if str(row[1]) == "None":
				self.damageTable.SetCellValue(i, 11, "")
			else:
				self.damageTable.SetCellValue(i, 11, str(row[1]))
			if str(row[2]) == "None":
				self.damageTable.SetCellValue(i, 12, "")
			else:
				self.damageTable.SetCellValue(i, 12, str(row[2]))
			self.damageTable.SetCellValue(i, 13, str(row[3]))
			i += 1
			j += 1

		# TODO maybe uses the stars for weakness/ailments, alt use images
		# TODO fix data maybe and then use the dictionary to use the same body part name
		#self.damageTable.SetCellValue(i, 13, "⭐⭐⭐")
		#self.damageTable.SetCellValue(i + 1, 13, "⭐⭐")
		#self.damageTable.SetCellValue(i + 2, 13, "⭐⭐")

	
	def initMaterials(self):
		self.materialsTree = gizmos.TreeListCtrl(self.materialsPanel, -1, style=0, agwStyle=
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
		self.materialsTree.SetColumnWidth(0, (self.GetSize().width * 0.44) * 0.65)
		self.materialsTree.SetColumnWidth(1, (self.GetSize().width * 0.44) * 0.11)
		self.materialsTree.SetColumnWidth(2, (self.GetSize().width * 0.44) * 0.11)
		self.materialsTree.SetColumnWidth(3, 0)

		isz = (32,32)
		il = wx.ImageList(isz[0], isz[1])
		self.fldridx = il.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, isz))
		self.fldropenidx = il.Add(wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, isz))
		self.fileidx = il.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, isz))
		self.nergidx = il.Add(self.testIcon)

		self.materialsTree.SetImageList(il)
		self.il = il

		self.initMaterialDetail()

		self.monsterMaterialsSizer.Add(self.materialsTree, 2, wx.EXPAND)
		self.monsterMaterialsSizer.Add(self.materialDetailPanel, 1, wx.EXPAND)
		self.materialsPanel.SetSizer(self.monsterMaterialsSizer)

		self.loadMaterials(self.currentMonsterID)

	def initMaterialDetail(self):
		self.materialDetailPanel = wx.Panel(self.materialsPanel)
		self.materialDetailSizer = wx.BoxSizer(wx.VERTICAL)
		self.materialImage = wx.Bitmap("images/VectorDrawable2Svg-master/png/ic_items_scale_base128.png", wx.BITMAP_TYPE_ANY)
		self.materialImageLabel = wx.StaticBitmap(self.materialDetailPanel, bitmap=self.materialImage)

		self.materialDetailsProperyGrid = wxpg.PropertyGridManager(self.materialDetailPanel, 
																   style=
																   # wxpg.PG_SPLITTER_AUTO_CENTER
																   #| wxpg.PG_AUTO_SORT
																    wxpg.PG_TOOLBAR
																  )

		self.initMaterialData(self.currentMonsterMaterialID)
		
		icon = wx.Bitmap("images/status effects/mhw-ice-damage_s.png", wx.BITMAP_TYPE_ANY)

		self.materialDetailSizer.Add(self.materialImageLabel, 1, wx.EXPAND)
		self.materialDetailSizer.Add(self.materialDetailsProperyGrid, 3, wx.EXPAND)

		self.materialDetailPanel.SetSizer(self.materialDetailSizer)
	

	def loadMaterials(self, monsterID):
		self.root = self.materialsTree.AddRoot("Materials")

		# master rank
		self.masterRankNode = self.materialsTree.AppendItem(self.root, "Master Rank")
		masterRankColour = wx.Colour(255, 230, 0)
		self.materialsTree.SetItemBackgroundColour(self.masterRankNode, wx.Colour(255, 230, 0))
		
		# high rank
		self.highRankNode = self.materialsTree.AppendItem(self.root, "High Rank")
		highRankColour = wx.Colour(255, 140, 0)
		self.materialsTree.SetItemBackgroundColour(self.highRankNode, wx.Colour(255, 140, 0))
		
		# low rank
		self.lowRankNode = self.materialsTree.AppendItem(self.root, "Low Rank")
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

		conn = sqlite3.connect("../MonsterHunterWorld/mhw.db")
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
					self.materialsTree.SetItemImage(monsterMaterial, self.nergidx, which = wx.TreeItemIcon_Normal) # TODO proper icons
					self.materialsTree.SetItemBackgroundColour(monsterMaterial, lowRankColour)
				else:
					rewardCondition = self.materialsTree.AppendItem(rankNodes[row[0]], str(row[1]))
					monsterMaterial = self.materialsTree.AppendItem(rewardCondition,  str(row[5]))
					self.materialsTree.SetItemText(monsterMaterial, str(row[2]), 1)
					self.materialsTree.SetItemText(monsterMaterial, str(row[3]), 2)
					self.materialsTree.SetItemText(monsterMaterial, str(row[4]), 3)
					self.materialsTree.SetItemImage(monsterMaterial, self.nergidx, which = wx.TreeItemIcon_Normal) # TODO proper icons
					self.materialsTree.SetItemBackgroundColour(rewardCondition, lowRankColour)
					self.materialsTree.SetItemBackgroundColour(monsterMaterial, lowRankColour)
					self.materialsTree.Expand(rewardCondition)

				categoriesLR.append(currentCategory)

			elif row[0] == "HR":
				if currentCategory in categoriesHR:
					monsterMaterial = self.materialsTree.AppendItem(rewardCondition,  str(row[5]))
					self.materialsTree.SetItemText(monsterMaterial, str(row[2]), 1)
					self.materialsTree.SetItemText(monsterMaterial, str(row[3]), 2)
					self.materialsTree.SetItemText(monsterMaterial, str(row[4]), 3)
					self.materialsTree.SetItemImage(monsterMaterial, self.nergidx, which = wx.TreeItemIcon_Normal) # TODO proper icons
					self.materialsTree.SetItemBackgroundColour(monsterMaterial, highRankColour)
				else:
					rewardCondition = self.materialsTree.AppendItem(rankNodes[row[0]], str(row[1]))
					monsterMaterial = self.materialsTree.AppendItem(rewardCondition,  str(row[5]))
					self.materialsTree.SetItemText(monsterMaterial, str(row[2]), 1)
					self.materialsTree.SetItemText(monsterMaterial, str(row[3]), 2)
					self.materialsTree.SetItemText(monsterMaterial, str(row[4]), 3)
					self.materialsTree.SetItemImage(monsterMaterial, self.nergidx, which = wx.TreeItemIcon_Normal) # TODO proper icons
					self.materialsTree.SetItemBackgroundColour(rewardCondition, highRankColour)
					self.materialsTree.SetItemBackgroundColour(monsterMaterial, highRankColour)
					self.materialsTree.Expand(rewardCondition)
					

				categoriesHR.append(currentCategory)

			elif row[0] == "MR":
				if currentCategory in categoriesMR:
					monsterMaterial = self.materialsTree.AppendItem(rewardCondition,  str(row[5]))
					self.materialsTree.SetItemText(monsterMaterial, str(row[2]), 1)
					self.materialsTree.SetItemText(monsterMaterial, str(row[3]), 2)
					self.materialsTree.SetItemText(monsterMaterial, str(row[4]), 3)
					self.materialsTree.SetItemImage(monsterMaterial, self.nergidx, which = wx.TreeItemIcon_Normal) # TODO proper icons
					self.materialsTree.SetItemBackgroundColour(monsterMaterial, masterRankColour)
				else:
					rewardCondition = self.materialsTree.AppendItem(rankNodes[row[0]], str(row[1]))
					monsterMaterial = self.materialsTree.AppendItem(rewardCondition,  str(row[5]))
					self.materialsTree.SetItemText(monsterMaterial, str(row[2]), 1)
					self.materialsTree.SetItemText(monsterMaterial, str(row[3]), 2)
					self.materialsTree.SetItemText(monsterMaterial, str(row[4]), 3)
					self.materialsTree.SetItemImage(monsterMaterial, self.nergidx, which = wx.TreeItemIcon_Normal) # TODO proper icons
					self.materialsTree.SetItemBackgroundColour(rewardCondition, masterRankColour)
					self.materialsTree.SetItemBackgroundColour(monsterMaterial, masterRankColour)
					self.materialsTree.Expand(rewardCondition)

				categoriesMR.append(currentCategory)

		self.materialsTree.Expand(self.masterRankNode)
		#self.materialsTree.Expand(self.highRankNode) # TODO maybe make this an option to auto expand a particular option or all of them
		#self.materialsTree.Expand(self.lowRankNode)


	# work in progress
	# TODO think of a better layout for the data
	def addMaterialToRank(self, dataRow, rankString, rankCategoriesList, rankColor):
		if dataRow[0] == rankString:
			if currentCategory in rankCategoriesList:
				monsterMaterial = self.materialsTree.AppendItem(rewardCondition,  str(dataRow[5]))
				self.materialsTree.SetItemText(monsterMaterial, str(dataRow[2]), 1)
				self.materialsTree.SetItemText(monsterMaterial, str(dataRow[3]), 2)
				self.materialsTree.SetItemImage(monsterMaterial, self.nergidx, which = wx.TreeItemIcon_Normal) # TODO proper icons
				self.materialsTree.SetItemBackgroundColour(monsterMaterial, rankColor)
			else:
				rewardCondition = self.materialsTree.AppendItem(rankNodes[dataRow[0]], str(dataRow[1]))
				monsterMaterial = self.materialsTree.AppendItem(rewardCondition,  str(dataRow[5]))
				self.materialsTree.SetItemText(monsterMaterial, str(dataRow[2]), 1)
				self.materialsTree.SetItemText(monsterMaterial, str(dataRow[3]), 2)
				self.materialsTree.SetItemImage(monsterMaterial, self.nergidx, which = wx.TreeItemIcon_Normal) # TODO proper icons
				self.materialsTree.SetItemBackgroundColour(rewardCondition, rankColor)
				self.materialsTree.SetItemBackgroundColour(monsterMaterial, rankColor)
				self.materialsTree.Expand(rewardCondition)

			rankCategoriesList.append(currentCategory)


	def onSize(self, event):
		width, height = self.GetSize()
		numOfColumns = 4
		numOfColumnsDamage = 14
		halfOfWindow = 3

		self.monstersTable.SetColSize(1, ((width / halfOfWindow) / numOfColumns + 30))
		self.monstersTable.SetColSize(2, ((width / halfOfWindow) / numOfColumns))
		self.monstersTable.SetColSize(3, ((width / halfOfWindow) / numOfColumns))
		self.monstersTable.SetColSize(4, ((width / halfOfWindow) / numOfColumns))
			
		for col in range(numOfColumnsDamage):
			self.damageTable.SetColSize(col, ((width * 0.66) / numOfColumnsDamage - 13))
			self.damageTable.SetColSize(0, ((width * 0.66) / numOfColumnsDamage + 80))

		self.materialsTree.SetColumnWidth(0, (self.GetSize().width * 0.44) * 0.65)
		self.materialsTree.SetColumnWidth(1, (self.GetSize().width * 0.44) * 0.11)
		self.materialsTree.SetColumnWidth(2, (self.GetSize().width * 0.44) * 0.11)
		
	
	def loadData(self):
		conn = sqlite3.connect("../MonsterHunterWorld/MonsterHunter.db")
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
		conn = sqlite3.connect("../MonsterHunterWorld/mhw.db")

		itemInfo = self.loadMaterialSummaryPage(itemID, conn)
		itemObtaining = self.loadMaterialObtainingPage(itemID, conn)
		itemUsage = self.loadMaterialUsagePage(itemID, conn)
		self.materialDetailsProperyGrid.Clear() # TODO remember the last selected page and select it
		self.loadMaterialPropertyGrid(itemInfo, itemObtaining, itemUsage)

	def initMaterialData(self, itemID):
		itemID = str(itemID)
		conn = sqlite3.connect("../MonsterHunterWorld/mhw.db")

		itemInfo = self.loadMaterialSummaryPage(itemID, conn)
		itemObtaining = self.loadMaterialObtainingPage(itemID, conn)
		itemUsage = self.loadMaterialUsagePage(itemID, conn)
		self.loadMaterialPropertyGrid(itemInfo, itemObtaining, itemUsage)

	def loadMaterialSummaryPage(self, itemID, conn):
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

	
	def loadMaterialUsagePage(self, itemID, conn):

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


	def loadMaterialObtainingPage(self, itemID, conn):
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
				
		# TODO replace icon with item icon probably base scale
		self.summaryMaterialPage = self.materialDetailsProperyGrid.AddPage("Summary", self.testIcon)
		self.summaryMaterialPage.Append(wxpg.PropertyCategory("Summary"))
		self.summaryMaterialPage.Append(wxpg.StringProperty("Name",value=itemInfo[10]))
		self.summaryMaterialPage.Append(wxpg.LongStringProperty("Description",value=itemInfo[11]))
		self.summaryMaterialPage.Append(wxpg.StringProperty("Rarity",value=itemInfo[3]))
		self.summaryMaterialPage.Append(wxpg.StringProperty("Buy",value=itemInfo[4]))
		if itemInfo[5] == "-":	
			# TODO points icon
			self.summaryMaterialPage.Append(wxpg.StringProperty("Sell",value=itemInfo[7]))
		else:
			# TODO zenny icon
			self.summaryMaterialPage.Append(wxpg.StringProperty("Sell",value=itemInfo[5]))
		self.summaryMaterialPage.Append(wxpg.StringProperty("Carry",value=itemInfo[6]))

		# TODO replace icon with armor icon probably base chest or head
		self.usageMaterialPage = self.materialDetailsProperyGrid.AddPage("Usage", self.testIcon)
		self.usageMaterialPage.Append(wxpg.PropertyCategory("Usage"))
		self.usageMaterialPage.AppendIn(wxpg.PGPropArgCls("Usage"), wxpg.PropertyCategory("Charms"))
		for item in itemUsage[0]:
			self.usageMaterialPage.Append(wxpg.StringProperty(str(item[3]),value=str(item[4])))
		self.usageMaterialPage.AppendIn(wxpg.PGPropArgCls("Usage"), wxpg.PropertyCategory("Armor"))
		for item in itemUsage[1]:
			self.usageMaterialPage.Append(wxpg.StringProperty(str(item[1]),value=str(item[7])))
		self.usageMaterialPage.AppendIn(wxpg.PGPropArgCls("Usage"), wxpg.PropertyCategory("Weapons"))
		for item in itemUsage[2]:
			self.usageMaterialPage.Append(wxpg.StringProperty(str(item[6]),value=str(item[7])))
		self.usageMaterialPage.SetSplitterLeft()

		# TODO replace icon with unknow monster icon
		self.obtainingMaterialPage = self.materialDetailsProperyGrid.AddPage("Obtaining", self.testIcon)
		self.obtainingMaterialPage.Append(wxpg.PropertyCategory("Obtaining"))
		for item in itemObtaining:
			self.obtainingMaterialPage.AppendIn(wxpg.PGPropArgCls("Obtaining"), wxpg.PropertyCategory(str(item[1])))
			try:
				self.obtainingMaterialPage.Append(wxpg.StringProperty(str(item[4]) + " " + str(item[3]),value=str(item[5]) + " x " + str(item[6]) + "%"))
			except:
				print("item already exists, its not a problem though :|")

		self.obtainingMaterialPage.SetSplitterLeft()


	def onMonsterSelect(self, event):
		if str(self.monstersTable.GetCellValue(event.GetRow(), 1)) != "":
			self.monsterImage.LoadFile("images/monsters/256/" + str(self.monstersTable.GetCellValue(event.GetRow(), 1)) + ".png")
		else:
			self.monsterImage.LoadFile("images/monsters/256/Unknown.png")
		self.monsterImageLabel.SetBitmap(self.monsterImage)
		self.damageTable.ClearGrid()
		self.materialsTree.DeleteAllItems()
		self.currentMonsterID = self.monstersTable.GetCellValue(event.GetRow(), 0)
		self.loadDamage(self.currentMonsterID)
		self.loadMaterials(self.currentMonsterID)


	def makeMenuBar(self):
		fileMenu = wx.Menu()
		# The "\t..." syntax defines an accelerator key that also triggers the same event
		helloItem = fileMenu.Append(-1, "&Hello...\tCtrl-H",
				"Help string shown in status bar for this menu item")
		fileMenu.AppendSeparator()

		exitItem = fileMenu.Append(wx.ID_EXIT)

		helpMenu = wx.Menu()
		aboutItem = helpMenu.Append(wx.ID_ABOUT)

		menuBar = wx.MenuBar()
		menuBar.Append(fileMenu, "&File")
		menuBar.Append(helpMenu, "&Help")

		self.SetMenuBar(menuBar)

		self.Bind(wx.EVT_MENU, self.OnHello, helloItem)
		self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)
		self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)


	def OnExit(self, event):
		self.Close(True)


	def OnHello(self, event):
		wx.MessageBox("Hello again from wxPython")


	def OnAbout(self, event):
		wx.MessageBox("This is a wxPython Hello World sample",
					  "About Hello World 2",
					  wx.OK|wx.ICON_INFORMATION)


if __name__ == '__main__':
	app = wx.App()
	frm = Application(None, title="Database")
	frm.Show()
	app.MainLoop()
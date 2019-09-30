import wx
import wx.grid
import wx.lib.gizmos as gizmos
import CustomGridRenderer as cgr
import wx.propgrid as wxpg
import sqlite3
import time
import os


class WeaponsTab:

	def __init__(self, root, mainNotebook):
		self.root = root
		self.mainNotebook = mainNotebook
		self.c = wx.ColourDatabase()

		self.currentlySelectedWeaponID = 1
		self.currentWeaponTree = "great-sword"
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

		# TODO could switch to these colors but will have to redo the images 
		"""self.rarityColors = {
			1: "#e5e5e5",
			2: "#e5e5e5",
			3: "#aac44b",
			4: "#57ac4c",
			5: "#75b8c2",
			6: "#6764d7",
			7: "#895edc",
			8: "#c47c5e",
			#9: "#cb7793",
			#10: "#4fd1f5",
			#11: "#f5d569",
			#12: "#d5edfa",
		}"""

		self.elementColors = {
			"Fire": "EF5350",
			"Water": "2196F3",
			"Ice": "90CAF9",
			"Thunder": "FFEE58",
			"Dragon": "7E57C2",
			"Poison": "AB47BC",
			"Paralysis": "FFCA28",
			"Blast": "8D6E63",
			"Sleep": "78909C", # 26C6DA
		}	

		# TODO maybe remove or change the colors to the ones i actually want
		self.sharpnessColors = {
			"red": "d92c2c",
			"orange": "d9662c",
			"yellow": "d9d12c",
			"green": "70d92c",
			"blue": "2c86d9",
			"white": "ffffff",
			"purple": "cc99ff",
		}

		self.initWeaponsTab()


	def initWeaponsTab(self):
		self.weaponsPanel = wx.Panel(self.mainNotebook)
		self.mainNotebook.AddPage(self.weaponsPanel, "Weapons")
		self.weaponsSizer = wx.BoxSizer(wx.HORIZONTAL)

		self.weaponsTreeSizer = wx.BoxSizer(wx.VERTICAL)
		
		self.weaponsDetailedSizer = wx.BoxSizer(wx.VERTICAL)
		self.weaponImage = wx.Bitmap("images/weapons/great-sword/Buster Sword I.png", wx.BITMAP_TYPE_ANY)
		self.weaponImageLabel = wx.StaticBitmap(self.weaponsPanel, bitmap=self.weaponImage)

		self.weaponDetailsNotebook = wx.Notebook(self.weaponsPanel)
		self.weaponDetailPanel = wx.Panel(self.weaponDetailsNotebook)
		#self.weaponFamilyPanel = wx.Panel(self.weaponDetailsNotebook) # REMOVE i dont think this is much use
		
		self.weaponDetailSizer = wx.BoxSizer(wx.VERTICAL)
		self.weaponDetailsNotebook.AddPage(self.weaponDetailPanel, "Detail")
		self.weaponDetailPanel.SetSizer(self.weaponDetailSizer)
		
		#self.weaponFamilySizer = wx.BoxSizer(wx.VERTICAL) # REMOVE i dont think this is much use
		#self.weaponDetailsNotebook.AddPage(self.weaponFamilyPanel, "Family") # REMOVE i dont think this is much use
		
		self.weaponsDetailedSizer.Add(self.weaponImageLabel, 1, wx.ALIGN_CENTER | wx.ALL | wx.ADJUST_MINSIZE, 10)
		self.weaponsDetailedSizer.Add(self.weaponDetailsNotebook, 3, wx.EXPAND)

		self.weaponsSizer.Add(self.weaponsTreeSizer, 2, wx.EXPAND)
		self.weaponsSizer.Add(self.weaponsDetailedSizer, 1, wx.EXPAND)

		self.weaponsPanel.SetSizer(self.weaponsSizer)
		
		self.initWeaponButtons()
		self.initWeaponsTree()
		self.initWeaponDetailTab()


	def initWeaponButtons(self):
		# TODO change to appropriate icons
		self.greatSwordButton = wx.BitmapButton(self.weaponsPanel, bitmap=self.testIcon, name="great-sword")
		self.longSwordButton = wx.BitmapButton(self.weaponsPanel, bitmap=self.testIcon, name="long-sword")
		self.swordAndShieldButton = wx.BitmapButton(self.weaponsPanel, bitmap=self.testIcon, name="sword-and-shield")
		self.dualBladesButton = wx.BitmapButton(self.weaponsPanel, bitmap=self.testIcon, name="dual-blades")
		self.hammerButton = wx.BitmapButton(self.weaponsPanel, bitmap=self.testIcon, name="hammer")
		self.huntingHornButton = wx.BitmapButton(self.weaponsPanel, bitmap=self.testIcon, name="hunting-horn")
		self.lanceButton = wx.BitmapButton(self.weaponsPanel, bitmap=self.testIcon, name="lance")
		self.gunLanceButton = wx.BitmapButton(self.weaponsPanel, bitmap=self.testIcon, name="gunlance")
		self.switchAxeButton = wx.BitmapButton(self.weaponsPanel, bitmap=self.testIcon, name="switch-axe")
		self.chargeBladeButton = wx.BitmapButton(self.weaponsPanel, bitmap=self.testIcon, name="charge-blade")
		self.insectGlaiveButton = wx.BitmapButton(self.weaponsPanel, bitmap=self.testIcon, name="insect-glaive")
		self.lightBowGunButton = wx.BitmapButton(self.weaponsPanel, bitmap=self.testIcon, name="light-bowgun")
		self.heavyBowGunButton = wx.BitmapButton(self.weaponsPanel, bitmap=self.testIcon, name="heavy-bowgun")
		self.bowButton = wx.BitmapButton(self.weaponsPanel, bitmap=self.testIcon, name="bow")

		self.greatSwordButton.Bind(wx.EVT_BUTTON, self.onWeaponTypeSelection)
		self.longSwordButton.Bind(wx.EVT_BUTTON, self.onWeaponTypeSelection)
		self.swordAndShieldButton.Bind(wx.EVT_BUTTON, self.onWeaponTypeSelection)
		self.dualBladesButton.Bind(wx.EVT_BUTTON, self.onWeaponTypeSelection)
		self.hammerButton.Bind(wx.EVT_BUTTON, self.onWeaponTypeSelection)
		self.huntingHornButton.Bind(wx.EVT_BUTTON, self.onWeaponTypeSelection)
		self.lanceButton.Bind(wx.EVT_BUTTON, self.onWeaponTypeSelection)
		self.gunLanceButton.Bind(wx.EVT_BUTTON, self.onWeaponTypeSelection)
		self.switchAxeButton.Bind(wx.EVT_BUTTON, self.onWeaponTypeSelection)
		self.chargeBladeButton.Bind(wx.EVT_BUTTON, self.onWeaponTypeSelection)
		self.insectGlaiveButton.Bind(wx.EVT_BUTTON, self.onWeaponTypeSelection)
		self.lightBowGunButton.Bind(wx.EVT_BUTTON, self.onWeaponTypeSelection)
		self.heavyBowGunButton.Bind(wx.EVT_BUTTON, self.onWeaponTypeSelection)
		self.bowButton.Bind(wx.EVT_BUTTON, self.onWeaponTypeSelection)

		self.weaponButtonsSizer = wx.BoxSizer(wx.HORIZONTAL)

		self.weaponButtonsSizer.Add(self.greatSwordButton)
		self.weaponButtonsSizer.Add(self.longSwordButton)
		self.weaponButtonsSizer.Add(self.swordAndShieldButton)
		self.weaponButtonsSizer.Add(self.dualBladesButton)
		self.weaponButtonsSizer.Add(self.hammerButton)
		self.weaponButtonsSizer.Add(self.huntingHornButton)
		self.weaponButtonsSizer.Add(self.lanceButton)
		self.weaponButtonsSizer.Add(self.gunLanceButton)
		self.weaponButtonsSizer.Add(self.switchAxeButton)
		self.weaponButtonsSizer.Add(self.chargeBladeButton)
		self.weaponButtonsSizer.Add(self.insectGlaiveButton)
		self.weaponButtonsSizer.Add(self.lightBowGunButton)
		self.weaponButtonsSizer.Add(self.heavyBowGunButton)
		self.weaponButtonsSizer.Add(self.bowButton)

		self.weaponsTreeSizer.Add(self.weaponButtonsSizer)


	def initWeaponsTree(self):
		self.weaponsTree = gizmos.TreeListCtrl(self.weaponsPanel, -1, style=0,
												agwStyle=
												  gizmos.TR_DEFAULT_STYLE
												#| gizmos.TR_TWIST_BUTTONS
												| gizmos.TR_ROW_LINES
												| gizmos.TR_COLUMN_LINES
												#| gizmos.TR_NO_LINES
												| gizmos.TR_FULL_ROW_HIGHLIGHT
												| gizmos.TR_HIDE_ROOT
												)
		self.weaponsTree.Bind(wx.EVT_TREE_SEL_CHANGED, self.onWeaponSelection)
		self.weaponsTreeSizer.Add(self.weaponsTree, 1, wx.EXPAND)

		isz = (24, 24)
		self.il = wx.ImageList(isz[0], isz[1])

		self.nergidx = self.il.Add(self.testIcon)

		self.rarity1 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/1.png", wx.BITMAP_TYPE_ANY))
		self.rarity2 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/2.png", wx.BITMAP_TYPE_ANY))
		self.rarity3 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/3.png", wx.BITMAP_TYPE_ANY))
		self.rarity4 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/4.png", wx.BITMAP_TYPE_ANY))
		self.rarity5 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/5.png", wx.BITMAP_TYPE_ANY))
		self.rarity6 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/6.png", wx.BITMAP_TYPE_ANY))
		self.rarity7 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/7.png", wx.BITMAP_TYPE_ANY))
		self.rarity8 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/8.png", wx.BITMAP_TYPE_ANY))
		# TODO iceborne
		#self.rarity9 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/9.png", wx.BITMAP_TYPE_ANY))
		#self.rarity10 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/10.png", wx.BITMAP_TYPE_ANY))
		#self.rarity11 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/11.png", wx.BITMAP_TYPE_ANY))
		#self.rarity12 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/12.png", wx.BITMAP_TYPE_ANY))

		self.affinity = self.il.Add(wx.Bitmap("images/weapon-detail-24/affinity.png", wx.BITMAP_TYPE_ANY))
		self.attack = self.il.Add(wx.Bitmap("images/weapon-detail-24/attack.png", wx.BITMAP_TYPE_ANY))
		self.defense = self.il.Add(wx.Bitmap("images/weapon-detail-24/defense.png", wx.BITMAP_TYPE_ANY))
		self.elderseal = self.il.Add(wx.Bitmap("images/weapon-detail-24/elderseal.png", wx.BITMAP_TYPE_ANY))
		self.element = self.il.Add(wx.Bitmap("images/weapon-detail-24/element.png", wx.BITMAP_TYPE_ANY))
		self.phials = self.il.Add(wx.Bitmap("images/weapon-detail-24/phials.png", wx.BITMAP_TYPE_ANY))
		self.slots = self.il.Add(wx.Bitmap("images/weapon-detail-24/slots.png", wx.BITMAP_TYPE_ANY))

		self.weaponsTree.SetImageList(self.il)

		self.weaponsTree.AddColumn("Name")
		self.weaponsTree.AddColumn("") # Physical
		self.weaponsTree.AddColumn("") # Element/Status
		self.weaponsTree.AddColumn("") # Affinity
		self.weaponsTree.AddColumn("") # Defense
		self.weaponsTree.AddColumn("") # Slots
		
		self.weaponsTree.AddColumn("R") # R
		self.weaponsTree.AddColumn("O") # O
		self.weaponsTree.AddColumn("Y") # Y
		self.weaponsTree.AddColumn("G") # G
		self.weaponsTree.AddColumn("B") # B
		self.weaponsTree.AddColumn("W") # W
		self.weaponsTree.AddColumn("P") # P
		
		self.weaponsTree.AddColumn("id")
		
		self.weaponsTree.SetMainColumn(0)
		self.weaponsTree.SetColumnWidth(0, 400)

		self.weaponTreeIcons = {
			1: self.attack,
			2: self.element,
			3: self.affinity,
			4: self.defense,
			5: self.slots,
		}

		for num in range(1, 6):
			self.weaponsTree.SetColumnImage(num, self.weaponTreeIcons[num])
			self.weaponsTree.SetColumnAlignment(num, wx.ALIGN_CENTER)
			self.weaponsTree.SetColumnWidth(num, 35)

		for num in range(6, 13):
			#self.weaponsTree.SetColumnImage(num, self.nergidx)
			self.weaponsTree.SetColumnAlignment(num, wx.ALIGN_CENTER)
			self.weaponsTree.SetColumnWidth(num, 24)
		
		self.weaponsTree.SetColumnWidth(5, 50)
		self.weaponsTree.SetColumnWidth(13, 0)

		self.loadWeaponsTree()


	def loadWeaponsTree(self):
		root = self.weaponsTree.AddRoot("Weapon")
		normalWeaponNode = self.weaponsTree.AppendItem(root, "Normal")
		kulveWeaponNode = self.weaponsTree.AppendItem(root, "Kulve")

		# TODO icons dont change depending on rarity!!!
		self.rarity1 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/1.png", wx.BITMAP_TYPE_ANY))
		self.rarity2 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/2.png", wx.BITMAP_TYPE_ANY))
		self.rarity3 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/3.png", wx.BITMAP_TYPE_ANY))
		self.rarity4 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/4.png", wx.BITMAP_TYPE_ANY))
		self.rarity5 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/5.png", wx.BITMAP_TYPE_ANY))
		self.rarity6 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/6.png", wx.BITMAP_TYPE_ANY))
		self.rarity7 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/7.png", wx.BITMAP_TYPE_ANY))
		self.rarity8 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/8.png", wx.BITMAP_TYPE_ANY))
		#self.rarity9 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/9.png", wx.BITMAP_TYPE_ANY))
		#self.rarity10 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/10.png", wx.BITMAP_TYPE_ANY))
		#self.rarity11 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/11.png", wx.BITMAP_TYPE_ANY))
		#self.rarity12 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/12.png", wx.BITMAP_TYPE_ANY))

		self.rarityIcons = {
			1: self.rarity1,
			2: self.rarity2,
			3: self.rarity3,
			4: self.rarity4,
			5: self.rarity5,
			6: self.rarity6,
			7: self.rarity7,
			8: self.rarity8,
			#9: self.rarity9, # TODO iceborne
			#10: self.rarity10, # TODO iceborne
			#11: self.rarity11, # TODO iceborne
			#12: self.rarity12, # TODO iceborne
		}

		sql = """
			SELECT w.id, w.weapon_type, w.category, w.rarity, w.attack, w.attack_true, w.affinity, w.defense, w.slot_1, w.slot_2, w.slot_3, w.element1, w.element1_attack,
				w.element2, w.element2_attack, w.element_hidden, w.sharpness, w.sharpness_maxed, w.previous_weapon_id, w.craftable, w.kinsect_bonus,
				w.elderseal, w.phial, w.phial_power, w.shelling, w.shelling_level, w.coating_close, w.coating_power, w.coating_poison, w.coating_paralysis, w.coating_sleep, w.coating_blast,
				w.notes, wa.special_ammo, wt.name
			FROM weapon w
				JOIN weapon_text wt USING (id)
				LEFT JOIN weapon_ammo wa ON w.ammo_id = wa.id
			WHERE wt.lang_id = :langId
				AND w.weapon_type = :weaponType
			ORDER BY w.id ASC
			"""

		conn = sqlite3.connect("mhw.db")
		data = conn.execute(sql, ("en", self.currentWeaponTree, ))

		weaponNodes = {}

		for row in data:
			if row[2] != "Kulve":
				if row[18] == None:
					self.populateWeaponsTree(normalWeaponNode, row, weaponNodes)
				else:
					self.populateWeaponsTree(weaponNodes[row[18]], row, weaponNodes)
			else:
				self.populateWeaponsTree(kulveWeaponNode, row, weaponNodes)

		# PREFERENCES again add this as a setting in the preferences window/tab/whatever
		self.weaponsTree.ExpandAll()
		#self.weaponsTree.Expand(normalWeaponNode)
		#self.weaponsTree.Expand(kulveWeaponNode)


	def populateWeaponsTree(self, weaponNode, row, weaponNodes):
		if bool(row[19]):
			# TODO maybe add rarity in a similar manner?? row[3]
			name = str(row[34]) + " 🔨" # TODO make this clearer that it means craftable
		else:
			name = str(row[34])
		weapon = self.weaponsTree.AppendItem(weaponNode,  name)
		self.weaponsTree.SetItemText(weapon, str(row[4]), 1)

		# TODO change the element implementation to the one below in weapon detail, shorten the name column
		element = str(row[12])
		if row[15] == 0 and row[12] == None:
			element = ""
		elif row[15] == 1:
			element = "(" + str(row[12]) + ")"
			# special color for dual element?? or alternatively have two columns for elements
			if row[14] != None:
				element = str(row[12]) + "\n" + str(row[14])
		if row[6] == 0:
			affinity = ""
		else:
			affinity = str(row[6]) + "%" # TODO maybe add a plus in here when affinity is positive
		if row[7] == 0:
			defense = ""
		else:
			defense = "+" + str(row[7])
		self.weaponsTree.SetItemText(weapon, element, 2) 
		self.weaponsTree.SetItemText(weapon, affinity, 3)
		self.weaponsTree.SetItemText(weapon, defense, 4)
		self.weaponsTree.SetItemText(weapon, str(row[8:11]), 5)
		
		# sharpness
		sharpnessSplit = str(row[16]).replace("(", "").replace(")", "").replace(" ", "").split(",")
		self.weaponsTree.SetItemText(weapon, sharpnessSplit[0], 6)
		self.weaponsTree.SetItemText(weapon, sharpnessSplit[1], 7)
		self.weaponsTree.SetItemText(weapon, sharpnessSplit[2], 8)
		self.weaponsTree.SetItemText(weapon, sharpnessSplit[3], 9)
		self.weaponsTree.SetItemText(weapon, sharpnessSplit[4], 10)
		self.weaponsTree.SetItemText(weapon, sharpnessSplit[5], 11)
		self.weaponsTree.SetItemText(weapon, sharpnessSplit[6], 12)
		
		# id - hidden, icon
		self.weaponsTree.SetItemText(weapon, str(row[0]), 13)

		self.weaponsTree.SetItemImage(weapon, self.rarityIcons[row[3]], which=wx.TreeItemIcon_Normal)
		weaponNodes[row[0]] = weapon


	def initWeaponDetailTab(self):
		self.weaponDetailList = wx.ListCtrl(self.weaponDetailPanel, style=wx.LC_REPORT
																	| wx.BORDER_NONE
																	| wx.LC_NO_HEADER
																	| wx.LC_VRULES
																	| wx.LC_HRULES
																	)

		self.weaponDetailList.Bind(wx.EVT_SIZE, self.onSize)
		self.weaponDetailList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onWeaponDetailSelect)
		self.weaponDetailList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
		
		self.weaponDetailSizer.Add(self.weaponDetailList, 5, wx.EXPAND)

		self.weaponSharpnessTable = cgr.HeaderBitmapGrid(self.weaponDetailPanel)
		self.weaponSharpnessTable.CreateGrid(6, 7)

		self.weaponDetailSizer.Add(self.weaponSharpnessTable, 2, wx.EXPAND|wx.BOTTOM, 15)

		self.materialsRequiredPropertyGrid = wxpg.PropertyGridManager(self.weaponDetailPanel, style=wxpg.PG_SPLITTER_AUTO_CENTER)

		self.weaponDetailSizer.Add(self.materialsRequiredPropertyGrid, 4, wx.EXPAND)

		# TODO prob move all the widgets in here into their own foldable panels, and change damage to foldable panel as well
		self.loadWeaponDetails()
		self.loadWeaponMaterials()


	def loadWeaponDetails(self):
		sql = """
			SELECT w.id, w.weapon_type, w.category, w.rarity, w.attack, w.attack_true, w.affinity, w.defense, w.slot_1, w.slot_2, w.slot_3, w.element1, w.element1_attack,
				w.element2, w.element2_attack, w.element_hidden, w.sharpness, w.sharpness_maxed, w.previous_weapon_id, w.craftable, w.kinsect_bonus,
				w.elderseal, w.phial, w.phial_power, w.shelling, w.shelling_level, w.coating_close, w.coating_power, w.coating_poison, w.coating_paralysis, w.coating_sleep, w.coating_blast,
				w.notes, wt.name
			FROM weapon w
				JOIN weapon_text wt USING (id)
				LEFT OUTER JOIN weapon_ammo wa ON w.ammo_id = wa.id
			WHERE w.id = :weaponId
			AND wt.lang_id = :langId
		"""

		conn = sqlite3.connect("mhw.db")
		data = conn.execute(sql, (self.currentlySelectedWeaponID, "en"))
		data = data.fetchone()

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = 0
		info.Text = "Attribute"
		self.weaponDetailList.InsertColumn(0, info)

		info.Align = wx.LIST_FORMAT_CENTER
		info.Text = "Value"
		self.weaponDetailList.InsertColumn(1, info)

		affinity = "-"
		if data[6] != 0:
			affinity = str(data[6]) + "%"

		element1 = "-"
		if data[11] == None:
			pass
		elif data[15] == 0:
			element1 = str(data[11]) + " " + str(data[12])
		elif data[15] == 1:
			element1 = str(data[11]) + " (" + str(data[12]) + ")"

		element2 = "-"
		if data[13] == None:
			pass
		else:
			element2 = str(data[13]) + " " + str(data[14])

		elderseal = "-"
		if data[21] != None:
			elderseal = data[21]

		defense = "-"
		if data[7] > 0:
			defense = "+" + str(data[7])

		phial = "-"
		if data[22] != None:
			phial = data[22]

		# TODO prob replaces any "None"'s with "-" or ""
		weaponDetail = {
			"Rarity": (data[3], self.rarityIcons[data[3]]), # TODO change to svg convert
			"Attack": (data[4], self.attack),
			"Attack (True)": (data[5], self.attack),
			"Affinity": (affinity, self.affinity),
			"Element I": (element1, self.element), # TODO change to data[11] since we'll know the element by the icon
			"Element II": (element2, self.element), # unless i decide to use the generic "element" icon
			"Slots": (data[8:11], self.slots),
			"Elderseal": (elderseal, self.elderseal),
			"Defense": (defense, self.defense),
			"Phial Type": (phial, self.phials),
		}

		for col, (key, value) in enumerate(weaponDetail.items()):
			index = self.weaponDetailList.InsertItem(self.weaponDetailList.GetItemCount(), key, value[1])
			self.weaponDetailList.SetItem(index, 1, str(value[0]))
			self.weaponDetailList.SetItemData(index, 0)

		self.weaponDetailList.SetColumnWidth(0, 280)
		self.weaponDetailList.SetColumnWidth(1, 100)
		
		self.weaponDetailList.SetItemBackgroundColour(0, self.hexToRGB(self.rarityColors[int(self.weaponDetailList.GetItemText(0, 1))]))

		# weapon affinity
		try:
			if int(self.weaponDetailList.GetItemText(3, 1).replace("%", "")) > 0:
				self.weaponDetailList.SetItemBackgroundColour(3, self.hexToRGB("#C8E6C9"))
			elif int(self.weaponDetailList.GetItemText(3, 1).replace("%", "")) < 0:
				self.weaponDetailList.SetItemBackgroundColour(3, self.hexToRGB("#FFCDD2"))
		except:
			pass

		# TODO maybe gray out the element or lighten the color to indicate element that needs awakening
		#self.weaponDetailList.SetItemTextColour(5, self.c.Find("Gray"))
		#self.weaponDetailList.SetItemBackgroundColour(5, self.c.Find("Light Gray"))
		try:
			element1 = self.weaponDetailList.GetItemText(4, 1).split(" ")[0]
			self.weaponDetailList.SetItemBackgroundColour(4, self.hexToRGB(self.elementColors[element1]))
		except:
			pass

		try:
			element2 = self.weaponDetailList.GetItemText(5, 1).split(" ")[0]
			self.weaponDetailList.SetItemBackgroundColour(5, self.hexToRGB(self.elementColors[element2]))
		except:
			pass
	
		if self.weaponDetailList.GetItemText(7, 1) != "-":
			self.weaponDetailList.SetItemBackgroundColour(7, self.hexToRGB("#D1C4E9"))

		if self.weaponDetailList.GetItemText(8, 1) != "-":
			self.weaponDetailList.SetItemBackgroundColour(8, self.hexToRGB("#D7CCC8"))

		if self.weaponDetailList.GetItemText(9, 1) != "-":
			self.weaponDetailList.SetItemBackgroundColour(9, self.hexToRGB("#FFECB3")) # impact still need to do element

		sharpnessMaxed = bool(data[17])
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
			self.weaponSharpnessTable.SetCellBackgroundColour(row, 1, self.c.Find("red"))

			self.weaponSharpnessTable.SetCellValue(row, 2, str(sharpnessLevels[row][1]))
			self.weaponSharpnessTable.SetCellBackgroundColour(row, 2, self.c.Find("coral"))

			self.weaponSharpnessTable.SetCellValue(row, 3, str(sharpnessLevels[row][2]))
			self.weaponSharpnessTable.SetCellBackgroundColour(row, 3, self.c.Find("yellow"))

			self.weaponSharpnessTable.SetCellValue(row, 4, str(sharpnessLevels[row][3]))
			self.weaponSharpnessTable.SetCellBackgroundColour(row, 4, self.c.Find("green"))

			self.weaponSharpnessTable.SetCellValue(row, 5, str(sharpnessLevels[row][4]))
			self.weaponSharpnessTable.SetCellBackgroundColour(row, 5, self.c.Find("slate blue"))

			self.weaponSharpnessTable.SetCellValue(row, 6, str(sharpnessLevels[row][5]))
			self.weaponSharpnessTable.SetCellBackgroundColour(row, 6, self.c.Find("white"))

		# TODO maybe split sharpness with each row having its own grid or listctrl this way allowing me to show
		# the difference in in sharpness visually per handicraft level as opposed to just numbers

	
	def loadWeaponMaterials(self):
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
			ORDER BY i.id
    	"""
		conn = sqlite3.connect("mhw.db")
		data = conn.execute(sql, ("en", self.currentlySelectedWeaponID))
		data = data.fetchall()

		mainPage = self.materialsRequiredPropertyGrid.AddPage("Materials Required", self.testIcon)

		for item in data:
			if item[6] == "Create":
				mainPage.Append(wxpg.PropertyCategory("Create"))
				try:
					mainPage.Append(wxpg.StringProperty(str(item[1]), value=str(item[5])))
				except:
					pass
			elif item[6] == "Upgrade":
				mainPage.Append(wxpg.PropertyCategory("Upgrade"))
				try:
					mainPage.Append(wxpg.StringProperty(str(item[1]), value=str(item[5])))
				except:
					pass


	def adjustSharpness(self, handicraftLevel, sharpnessMaxed, data):
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

	
	def onWeaponDetailSelect(self, event):
		self.weaponDetailList.Select(event.GetIndex(), False)


	def onWeaponSelection(self, event):
		self.currentlySelectedWeaponID = self.weaponsTree.GetItemText(event.GetItem(), 13)
		if self.currentlySelectedWeaponID != "":
			weaponName = (self.weaponsTree.GetItemText(event.GetItem(), 0)).replace(" 🔨", "").replace("\"", "'")
			weaponType = self.currentWeaponTree
			placeholder = self.currentWeaponTree
			if os.path.isfile("images/weapons/" + weaponType + "/" + weaponName + ".png"):
				self.weaponImage = wx.Bitmap("images/weapons/" + weaponType + "/" + weaponName + ".png", wx.BITMAP_TYPE_ANY)
			else:
				self.weaponImage = wx.Bitmap("images/weapons/" + weaponType + "/" + placeholder + ".png", wx.BITMAP_TYPE_ANY)
			self.weaponImageLabel.SetBitmap(self.weaponImage)
			self.weaponDetailList.ClearAll()
			self.weaponSharpnessTable.ClearGrid()
			self.materialsRequiredPropertyGrid.Clear() # propertygrid actually needs a page otherwise clear doesnt work
	
			self.loadWeaponDetails()
			self.loadWeaponMaterials()

		
	def onWeaponTypeSelection(self, event):
		self.currentWeaponTree = event.GetEventObject().GetName()
		self.weaponsTree.DeleteAllItems()
		self.loadWeaponsTree()


	def hexToRGB(self, color):
			color = color.replace("#", "")
			red = int(color[0:2], 16)
			green = int(color[2:4], 16)
			blue = int(color[4:6], 16)

			return (red, green, blue)


	def onSize(self, event):
		self.weaponDetailList.SetColumnWidth(0, self.weaponDetailPanel.GetSize()[0] * 0.66)
		self.weaponDetailList.SetColumnWidth(1, self.weaponDetailPanel.GetSize()[0] * 0.34)

		# TODO make each sharpness column have the appropriate bg colour, i probably need to make a custom class
		#for num in range(10):
		#	self.weaponsTree.SetColumnColour(num, wx.Colour(255, 1, 1))
		#self.weaponsTree.SetBackgroundColour(wx.Colour(255, 1, 1))
		#self.weaponsTree.Refresh()

		"""# TEST
		#print(self.weaponsPanel.GetSize()[0] * 0.70 - 400 - 7 * 24 - 6 * 35 - 15)
		self.weaponsTree.SetColumnWidth(0, self.weaponsPanel.GetSize()[0] * 0.70 * 0.43)
		for num in range(1, 6):
			self.weaponsTree.SetColumnWidth(num, self.weaponsPanel.GetSize()[0] * 0.70 * 0.05)

		for num in range(6, 13):
			self.weaponsTree.SetColumnWidth(num, self.weaponsPanel.GetSize()[0] * 0.70 * 0.03)
		
		self.weaponsTree.SetColumnWidth(5, self.weaponsPanel.GetSize()[0] * 0.70 * 0.08)
		self.weaponsTree.SetColumnWidth(13, 0)"""
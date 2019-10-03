import wx
import wx.grid
import wx.lib.gizmos as gizmos
import CustomGridRenderer as cgr
import wx.propgrid as wxpg
import sqlite3
import time
import os
import typing
from typing import List
from typing import Union
from typing import Tuple
from typing import Dict
from typing import NewType

wxTreeListItem = NewType('wxTreeListItem', None)

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
		self.weaponSongsPanel = wx.Panel(self.weaponDetailsNotebook)
		self.weaponAmmoPanel = wx.Panel(self.weaponDetailsNotebook)
		#self.weaponFamilyPanel = wx.Panel(self.weaponDetailsNotebook) # REMOVE i dont think this is much use
		
		self.weaponDetailSizer = wx.BoxSizer(wx.VERTICAL)
		self.weaponDetailsNotebook.AddPage(self.weaponDetailPanel, "Detail")
		self.weaponDetailPanel.SetSizer(self.weaponDetailSizer)

		self.weaponSongsSizer = wx.BoxSizer(wx.VERTICAL)
		self.weaponDetailsNotebook.AddPage(self.weaponSongsPanel, "Songs")
		self.weaponSongsPanel.SetSizer(self.weaponSongsSizer)

		self.weaponAmmoSizer = wx.BoxSizer(wx.VERTICAL)
		self.weaponDetailsNotebook.AddPage(self.weaponAmmoPanel, "Ammo")
		self.weaponAmmoPanel.SetSizer(self.weaponAmmoSizer)
		
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

		self.test = self.il.Add(self.testIcon)

		self.sharpnessTest = self.il.Add(wx.Bitmap("sharpnessTest.png"))

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
		self.slots = self.il.Add(wx.Bitmap("images/weapon-detail-24/slots.png", wx.BITMAP_TYPE_ANY))

		self.sharpness = self.il.Add(wx.Bitmap("images/weapon-detail-24/whetstone.png", wx.BITMAP_TYPE_ANY))

		self.slots1 = self.il.Add(wx.Bitmap("images/decoration-slots-24/1.png", wx.BITMAP_TYPE_ANY))
		self.slots2 = self.il.Add(wx.Bitmap("images/decoration-slots-24/2.png", wx.BITMAP_TYPE_ANY))
		self.slots3 = self.il.Add(wx.Bitmap("images/decoration-slots-24/3.png", wx.BITMAP_TYPE_ANY))

		self.phialType = self.il.Add(wx.Bitmap("images/weapon-detail-24/phials.png", wx.BITMAP_TYPE_ANY))

		self.notes = self.il.Add(wx.Bitmap("images/weapon-detail-24/notes.png", wx.BITMAP_TYPE_ANY))
		self.note1 = self.il.Add(wx.Bitmap("images/weapon-detail-24/note1.png", wx.BITMAP_TYPE_ANY))
		self.note2 = self.il.Add(wx.Bitmap("images/weapon-detail-24/note2.png", wx.BITMAP_TYPE_ANY))
		self.note3 = self.il.Add(wx.Bitmap("images/weapon-detail-24/note3.png", wx.BITMAP_TYPE_ANY))

		self.kinsectBonus = self.il.Add(wx.Bitmap("images/damage-types-24/kinsect.png", wx.BITMAP_TYPE_ANY))

		self.specialAmmo = self.il.Add(wx.Bitmap("images/weapon-detail-24/specialammo.png", wx.BITMAP_TYPE_ANY))
		self.deviation = self.il.Add(wx.Bitmap("images/weapon-detail-24/deviation.png"))

		self.closeCoating = self.il.Add(wx.Bitmap("images/weapon-detail-24/coating.png")) # TODO make all colors
		self.powerCoating = self.il.Add(wx.Bitmap("images/weapon-detail-24/coating.png")) # TODO make all colors
		self.paralysisCoating = self.il.Add(wx.Bitmap("images/weapon-detail-24/coating.png")) # TODO make all colors
		self.poisonCoating = self.il.Add(wx.Bitmap("images/weapon-detail-24/coating.png")) # TODO make all colors
		self.sleepCoating = self.il.Add(wx.Bitmap("images/weapon-detail-24/coating.png")) # TODO make all colors
		self.blastCoating = self.il.Add(wx.Bitmap("images/weapon-detail-24/coating.png")) # TODO make all colors

		self.shelling = self.il.Add(wx.Bitmap("images/weapon-detail-24/shelling.png", wx.BITMAP_TYPE_ANY))

		self.weaponsTree.SetImageList(self.il)
		self.weaponDetailsNotebook.AssignImageList(self.il)

		self.weaponsTree.AddColumn("Name")
		self.weaponsTree.AddColumn("") # Physical
		self.weaponsTree.AddColumn("") # Element/Status
		self.weaponsTree.AddColumn("") # Affinity
		self.weaponsTree.AddColumn("") # Defense
		self.weaponsTree.AddColumn("") # Slots 1
		self.weaponsTree.AddColumn("") # Slots 2
		self.weaponsTree.AddColumn("") # Slots 3
		
		# sharpness
		self.weaponsTree.AddColumn("") # R
		self.weaponsTree.AddColumn("") # O
		self.weaponsTree.AddColumn("") # Y
		self.weaponsTree.AddColumn("") # G
		self.weaponsTree.AddColumn("") # B
		self.weaponsTree.AddColumn("") # W
		self.weaponsTree.AddColumn("") # P
		
		self.weaponsTree.AddColumn("id")
		
		self.weaponsTree.SetMainColumn(0)
		self.weaponsTree.SetColumnWidth(0, 400)

		self.weaponTreeIcons = {
			1: self.attack,
			2: self.element,
			3: self.affinity,
			4: self.defense,
			5: self.slots,
			6: self.slots,
			7: self.slots,
			8: self.sharpness,
			9: self.sharpness,
			10: self.sharpness,
			11: self.sharpness,
			12: self.sharpness,
			13: self.sharpness,
			14: self.sharpness,
		}

		self.decorationSlotsIcons = {
			1: self.slots1,
			2: self.slots2,
			3: self.slots3,
		}

		for num in range(1, 8):
			self.weaponsTree.SetColumnImage(num, self.weaponTreeIcons[num])
			self.weaponsTree.SetColumnAlignment(num, wx.ALIGN_CENTER)
			self.weaponsTree.SetColumnWidth(num, 24)

		self.weaponsTree.SetColumnWidth(1, 35)
		self.weaponsTree.SetColumnWidth(2, 35)
		self.weaponsTree.SetColumnWidth(3, 35)
		self.weaponsTree.SetColumnWidth(4, 35)

		# TODO either set to 8 or 14 or all or none, i'm gravitating towards none since the images will be self explanatory
		#self.weaponsTree.SetColumnImage(14, self.weaponTreeIcons[14])

		for num in range(8, 15):
			#self.weaponsTree.SetColumnImage(num, self.weaponTreeIcons[num]) # REMOVE
			self.weaponsTree.SetColumnAlignment(num, wx.ALIGN_CENTER)
			self.weaponsTree.SetColumnWidth(num, 24)
		
		self.weaponsTree.SetColumnWidth(15, 0)

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


	def populateWeaponsTree(self, weaponNode: wxTreeListItem, row: Tuple[str], weaponNodes: Dict[int, wxTreeListItem]) -> None:
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
		# i think just use the generic element icon and leave it at that, element number is the same anyway(always??) and it messes with row height 
		"""if row[14] != None:
			element = str(row[12]) + "\n" + str(row[14])"""
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

		if row[8] != 0:
			weapon.SetImage(5, self.decorationSlotsIcons[row[8]], wx.TreeItemIcon_Normal)
		if row[9] != 0:
			weapon.SetImage(6, self.decorationSlotsIcons[row[9]], wx.TreeItemIcon_Normal)
		if row[10] != 0:
			weapon.SetImage(7, self.decorationSlotsIcons[row[10]], wx.TreeItemIcon_Normal)
		#self.weaponsTree.SetItemText(weapon, str(row[8]), 5) # TODO split into 3 three cols, with an appropriate image for each
		#self.weaponsTree.SetItemText(weapon, str(row[9]), 6) # TODO split into 3 three cols, with an appropriate image for each
		#self.weaponsTree.SetItemText(weapon, str(row[10]), 7) # TODO split into 3 three cols, with an appropriate image for each
		
		# sharpness
		try:
			sharpnessSplit = str(row[16]).replace("(", "").replace(")", "").replace(" ", "").split(",")
			# TODO work something out with the sharpness graphics
			# for now just this small icon test
			# TODO genius really, divide the total sharpness(400) by 2.38 so that the sharpness is represented...
			# to scale within 168px and then make that image based off of data from the sharpness attribute
			# then implement the example below
			# REMOVE placeholders
			weapon.SetImage(8, self.sharpnessTest, wx.TreeItemIcon_Normal)
			weapon.SetImage(9, self.sharpnessTest + 1, wx.TreeItemIcon_Normal)
			weapon.SetImage(10, self.sharpnessTest + 2, wx.TreeItemIcon_Normal)
			weapon.SetImage(11, self.sharpnessTest + 3, wx.TreeItemIcon_Normal)
			weapon.SetImage(12, self.sharpnessTest + 4, wx.TreeItemIcon_Normal)
			weapon.SetImage(13, self.sharpnessTest + 5, wx.TreeItemIcon_Normal)
			weapon.SetImage(14, self.sharpnessTest + 6, wx.TreeItemIcon_Normal)
			self.weaponsTree.SetItemText(weapon, sharpnessSplit[0], 8)
			self.weaponsTree.SetItemText(weapon, sharpnessSplit[1], 9)
			self.weaponsTree.SetItemText(weapon, sharpnessSplit[2], 10)
			self.weaponsTree.SetItemText(weapon, sharpnessSplit[3], 11)
			self.weaponsTree.SetItemText(weapon, sharpnessSplit[4], 12)
			self.weaponsTree.SetItemText(weapon, sharpnessSplit[5], 13)
			self.weaponsTree.SetItemText(weapon, sharpnessSplit[6], 14)
		except:
			for num in range(6, 13):
				self.weaponsTree.SetItemText(weapon, "-", num)

		
		# id - hidden, icon
		self.weaponsTree.SetItemText(weapon, str(row[0]), 13)

		self.weaponsTree.SetItemImage(weapon, self.rarityIcons[row[3]], which=wx.TreeItemIcon_Normal)
		weaponNodes[row[0]] = weapon


	def initWeaponDetailTab(self):
		self.weaponDetailList = wx.ListCtrl(self.weaponDetailPanel, style=wx.LC_REPORT
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
		self.weaponDetailSizer.Add(self.weaponSharpnessTable, 2, wx.EXPAND|wx.TOP, 10)

		self.materialsRequiredPropertyGrid = wxpg.PropertyGridManager(self.weaponDetailPanel, style=wxpg.PG_SPLITTER_AUTO_CENTER)
		self.weaponDetailSizer.Add(self.materialsRequiredPropertyGrid, 4, wx.EXPAND)

		self.weaponSongsList = wx.ListCtrl(self.weaponSongsPanel, style=wx.LC_REPORT
																	#| wx.LC_NO_HEADER
																	| wx.LC_VRULES
																	| wx.LC_HRULES
																	)
		self.weaponSongsList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
		self.weaponSongsSizer.Add(self.weaponSongsList, 1, wx.EXPAND)

		self.weaponAmmoList = wx.ListCtrl(self.weaponAmmoPanel, style=wx.LC_REPORT
																	#| wx.LC_NO_HEADER
																	| wx.LC_VRULES
																	| wx.LC_HRULES
																	)
		self.weaponAmmoList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
		self.weaponAmmoSizer.Add(self.weaponAmmoList, 1, wx.EXPAND)

		self.loadWeaponDetails()
		self.loadWeaponMaterials()


	def loadWeaponDetails(self):
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

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = 0
		info.Text = "Attribute"
		self.weaponDetailList.InsertColumn(0, info)

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
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
			"Rarity": (data[3], self.rarityIcons[data[3]]),
			"Attack": (data[4], self.attack),
			"Attack (True)": (data[5], self.attack),
			"Affinity": (affinity, self.affinity),
			"Element I": (element1, self.element), # TODO change to data[11] since we'll know the element by the icon
			"Element II": (element2, self.element), # unless i decide to use the generic "element" icon
			"Slots": (data[8:11], self.slots),
			"Elderseal": (elderseal, self.elderseal),
			"Defense": (defense, self.defense),
		}

		# TODO add data[index] to each of them
		# notes [32] WRB - white red blue
		# shelling [24:25] - normal 1
		# phial type [22] - impact / power
		# kinsect bonus [20] - sever
		# special ammo [33] - wyvernblast
		# deviation [34] - none / low
		# 26:31 coatings:
		# 26 = close
		# 27 = power
		# 28 = para
		# 29 = poison
		# 30 = sleep
		# 31 = blast

	
		note1 = str(data[32])[0]
		note2 = str(data[32])[1]
		note3 = str(data[32])[2]
		

		additionalDetails = {
			"switch-axe": ["Phial Type", data[22], self.phialType],
			"charge-blade": ["Phial Type", data[22], self.phialType],
			"gunlance": ["Shelling", data[24:25], self.shelling],
			"insect-glaive": ["Kinsect Bonus", data[20], self.kinsectBonus],

			"hunting-horn": ["Notes", self.notes,
							"Note 1", note1, self.note1,
							"Note 2", note2, self.note2,
							"Note 3", note3, self.note3,],

			"light-bowgun": ["Special Ammo", data[33], self.specialAmmo,
							"Deviation", data[34], self.deviation,],

			"heavy-bowgun": ["Special Ammo", data[33], self.specialAmmo,
							"Deviation", data[34], self.deviation],

			"bow": ["Close", data[26], self.closeCoating,
					"Power", data[27], self.powerCoating,
					"Paralysis", data[28], self.paralysisCoating,
					"Poison", data[29], self.poisonCoating,
					"Sleep", data[30], self.sleepCoating,
					"Blast", data[31], self.blastCoating,],
		}

		# REMOVE col from enumerate isnt used anymore and could be removed
		for col, (key, value) in enumerate(weaponDetail.items()):
			index = self.weaponDetailList.InsertItem(self.weaponDetailList.GetItemCount(), key, value[1])
			self.weaponDetailList.SetItem(index, 1, str(value[0]))
	
		#index = self.weaponDetailList.InsertItem(self.weaponDetailList.GetItemCount(), key, value[1])
		#self.weaponDetailList.SetItem(index, 1, str(value[0]), col + 16) # REMOVE i dont think this helps
		# if anything i would show the slots using the unicode characters instead
		#self.weaponDetailList.SetItemData(index, 0) # REMOVE seems this doesnt do anything

		self.weaponDetailList.SetColumnWidth(0, 280)
		self.weaponDetailList.SetColumnWidth(1, 170)
		
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

		try:
			self.weaponDetailsNotebook.RemovePage(1)
			self.weaponDetailsNotebook.RemovePage(1)
		except:
			pass

		if self.currentWeaponTree in ["charge-blade", "switch-axe", "gunlance", "insect-glaive"]:
			index = self.weaponDetailList.InsertItem(self.weaponDetailList.GetItemCount(), additionalDetails[self.currentWeaponTree][0], additionalDetails[self.currentWeaponTree][2])
			self.weaponDetailList.SetItem(index, 1, str(additionalDetails[self.currentWeaponTree][1]))
		elif self.currentWeaponTree in ["light-bowgun", "heavy-bowgun"]:
			index = self.weaponDetailList.InsertItem(self.weaponDetailList.GetItemCount(), additionalDetails[self.currentWeaponTree][0], additionalDetails[self.currentWeaponTree][2])
			self.weaponDetailList.SetItem(index, 1, str(additionalDetails[self.currentWeaponTree][1]))
			index = self.weaponDetailList.InsertItem(self.weaponDetailList.GetItemCount(), additionalDetails[self.currentWeaponTree][3], additionalDetails[self.currentWeaponTree][5])
			self.weaponDetailList.SetItem(index, 1, str(additionalDetails[self.currentWeaponTree][4]))
			self.weaponDetailsNotebook.AddPage(self.weaponAmmoPanel, "Ammo")
			self.weaponDetailsNotebook.SetPageImage(1, self.deviation)
			self.loadBowgunAmmo()
		elif self.currentWeaponTree == "bow":
			index = self.weaponDetailList.InsertItem(self.weaponDetailList.GetItemCount(), additionalDetails[self.currentWeaponTree][0], additionalDetails[self.currentWeaponTree][2])
			self.weaponDetailList.SetItem(index, 1, str(additionalDetails[self.currentWeaponTree][1]))
			index = self.weaponDetailList.InsertItem(self.weaponDetailList.GetItemCount(), additionalDetails[self.currentWeaponTree][3], additionalDetails[self.currentWeaponTree][5])
			self.weaponDetailList.SetItem(index, 1, str(additionalDetails[self.currentWeaponTree][4]))
			index = self.weaponDetailList.InsertItem(self.weaponDetailList.GetItemCount(), additionalDetails[self.currentWeaponTree][6], additionalDetails[self.currentWeaponTree][8])
			self.weaponDetailList.SetItem(index, 1, str(additionalDetails[self.currentWeaponTree][7]))
			index = self.weaponDetailList.InsertItem(self.weaponDetailList.GetItemCount(), additionalDetails[self.currentWeaponTree][9], additionalDetails[self.currentWeaponTree][11])
			self.weaponDetailList.SetItem(index, 1, str(additionalDetails[self.currentWeaponTree][10]))
			index = self.weaponDetailList.InsertItem(self.weaponDetailList.GetItemCount(), additionalDetails[self.currentWeaponTree][12], additionalDetails[self.currentWeaponTree][14])
			self.weaponDetailList.SetItem(index, 1, str(additionalDetails[self.currentWeaponTree][13]))
			index = self.weaponDetailList.InsertItem(self.weaponDetailList.GetItemCount(), additionalDetails[self.currentWeaponTree][15], additionalDetails[self.currentWeaponTree][17])
			self.weaponDetailList.SetItem(index, 1, str(additionalDetails[self.currentWeaponTree][16]))
		elif self.currentWeaponTree == "hunting-horn":
			# TODO probably move the note icons in the the second column, and maybe do the same with coatings
			index = self.weaponDetailList.InsertItem(self.weaponDetailList.GetItemCount(), additionalDetails[self.currentWeaponTree][0], additionalDetails[self.currentWeaponTree][1])
			index = self.weaponDetailList.InsertItem(self.weaponDetailList.GetItemCount(), "", -1)
			self.weaponDetailList.SetItem(index, 1, str(additionalDetails[self.currentWeaponTree][3]), self.note1)
			index = self.weaponDetailList.InsertItem(self.weaponDetailList.GetItemCount(), "", -1)
			self.weaponDetailList.SetItem(index, 1, str(additionalDetails[self.currentWeaponTree][6]), self.note2)
			index = self.weaponDetailList.InsertItem(self.weaponDetailList.GetItemCount(), "", -1)
			self.weaponDetailList.SetItem(index, 1, str(additionalDetails[self.currentWeaponTree][9]), self.note3)
			self.weaponDetailsNotebook.AddPage(self.weaponSongsPanel, "Notes")
			self.weaponDetailsNotebook.SetPageImage(1, self.notes)
			self.loadHuntingHornSongs()

		if self.currentWeaponTree not in ["light-bowgun", "heavy-bowgun", "bow"]:
			# TODO i think we want to do the insert method but actually destroy the widget and note hide it,
			# unless we can get the sizer to act like its not there
			if not self.weaponSharpnessTable.IsShown():
				self.weaponSharpnessTable.Show()
				#print(self.weaponDetailSizer.GetItemCount())
				self.weaponDetailSizer.Insert(1, self.weaponSharpnessTable, 2, wx.EXPAND|wx.BOTTOM, 15)
				self.weaponDetailSizer.SetDimension(self.weaponDetailPanel.GetPosition(), self.weaponDetailPanel.GetSize())
				#self.weaponDetailSizer.Add(self.weaponSharpnessTable, 2, wx.EXPAND|wx.BOTTOM, 15)

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
		else:
			if self.weaponSharpnessTable.IsShown():
				self.weaponSharpnessTable.Hide()
				#print(self.weaponDetailSizer.GetItem(2))
				self.weaponDetailSizer.Remove(1)
				self.weaponDetailSizer.SetDimension(self.weaponDetailPanel.GetPosition(), self.weaponDetailPanel.GetSize())


	def loadBowgunAmmo(self):
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

		self.weaponAmmoList.SetColumnWidth(0, 132)
		self.weaponAmmoList.SetColumnWidth(1, 102)
		self.weaponAmmoList.SetColumnWidth(2, 112)
		self.weaponAmmoList.SetColumnWidth(3, 102)

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

		col = 3
		# different checks are used avoid going out of bounds since not all ammo types have the same amount of columns
		for item in ammoTypes:
			if col == 127:
				if data[col] != 0 and data[col] != None:
					index = self.weaponAmmoList.InsertItem(self.weaponAmmoList.GetItemCount(), item, self.test)
					self.weaponAmmoList.SetItem(index, 1, str(data[col]))
					if self.currentWeaponTree == "heavy-bowgun":
						self.weaponAmmoList.SetItem(index, 2, "Rapid")
					self.weaponAmmoList.SetItem(index, 3, str(data[col + 1]).capitalize())
			elif col > 127:
				if data[col] != 0 and data[col] != None:
					index = self.weaponAmmoList.InsertItem(self.weaponAmmoList.GetItemCount(), item, self.test)
					self.weaponAmmoList.SetItem(index, 1, str(data[col]))
					self.weaponAmmoList.SetItem(index, 2, "Normal+" + str(data[col + 1]))
					self.weaponAmmoList.SetItem(index, 3, str(data[col + 2]).capitalize())
			else:
				if data[col] != 0 and data[col] != None:
					index = self.weaponAmmoList.InsertItem(self.weaponAmmoList.GetItemCount(), item, self.test)
					self.weaponAmmoList.SetItem(index, 1, str(data[col]))
					if data[col + 1] == 1:
						self.weaponAmmoList.SetItem(index, 2, "Rapid+" + str(data[col + 2]))
					elif data[col + 2] == - 1:
						self.weaponAmmoList.SetItem(index, 2, "Auto Reload")
					else:
						self.weaponAmmoList.SetItem(index, 2, "Normal+" + str(data[col + 2]))
					self.weaponAmmoList.SetItem(index, 3, str(data[col + 3]).capitalize())
			if col == 127:
				col += 2
			elif col > 127:
				col += 3
			else:
				col += 4


	def loadHuntingHornSongs(self):
		# TODO finish melodies section
		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = 0
		info.Text = "Attribute"
		self.weaponSongslList.InsertColumn(0, info)


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


	def adjustSharpness(self, handicraftLevel: int, sharpnessMaxed: bool, data: List[str]) -> Union[List[str], List[int]]:
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
			self.weaponSongsList.ClearAll()
			self.weaponAmmoList.ClearAll()
			try:
				self.weaponSharpnessTable.ClearGrid()
			except:
				pass
			self.materialsRequiredPropertyGrid.Clear() # propertygrid actually needs a page otherwise clear doesnt work
	
			self.loadWeaponDetails()
			self.loadWeaponMaterials()

		
	def onWeaponTypeSelection(self, event):
		self.currentWeaponTree = event.GetEventObject().GetName()
		self.weaponsTree.DeleteAllItems()
		self.loadWeaponsTree()


	def hexToRGB(self, color: str) -> Tuple[int, int, int]:
			"""
			:color = The hexadecimal representation of the color, # hash optional.

			returns = A tuple containing the red, green and blue color information.
			"""
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
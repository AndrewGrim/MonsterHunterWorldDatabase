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
import Armor as a
import ArmorImageList as ail

wxTreeListItem = NewType('wxTreeListItem', None)
Armor = NewType('Armor', None)

class ArmorTab:

	def __init__(self, root, mainNotebook):
		self.root = root
		self.mainNotebook = mainNotebook
		self.c = wx.ColourDatabase()

		self.currentArmorTree = "LR"
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

		# TODO maybe have the same button like in armor tab but for loading only low/high/master rank armro??
		self.initArmorTab()


	def initArmorTab(self):
		self.armorPanel = wx.Panel(self.mainNotebook)
		self.mainNotebook.AddPage(self.armorPanel, "Armor")
		self.armorSizer = wx.BoxSizer(wx.HORIZONTAL)

		self.armorTreeSizer = wx.BoxSizer(wx.VERTICAL) 
		
		self.armorDetailedSizer = wx.BoxSizer(wx.VERTICAL)
		self.armorImage = wx.Bitmap("images/weapons/great-sword/Buster Sword I.png", wx.BITMAP_TYPE_ANY)
		self.armorImageLabel = wx.StaticBitmap(self.armorPanel, bitmap=self.armorImage, size=(160, 160))

		self.armorDetailsNotebook = wx.Notebook(self.armorPanel)
		self.armorDetailPanel = wx.Panel(self.armorDetailsNotebook)
		self.armorSongsPanel = wx.Panel(self.armorDetailsNotebook)
		self.armorAmmoPanel = wx.Panel(self.armorDetailsNotebook)
		#self.armorFamilyPanel = wx.Panel(self.armorDetailsNotebook) # REMOVE i dont think this is much use
		
		self.armorDetailSizer = wx.BoxSizer(wx.VERTICAL)
		self.armorDetailsNotebook.AddPage(self.armorDetailPanel, "Detail")
		self.armorDetailPanel.SetSizer(self.armorDetailSizer)

		self.armorSongsSizer = wx.BoxSizer(wx.VERTICAL)
		self.armorDetailsNotebook.AddPage(self.armorSongsPanel, "Songs")
		self.armorSongsPanel.SetSizer(self.armorSongsSizer)

		self.armorAmmoSizer = wx.BoxSizer(wx.VERTICAL)
		self.armorDetailsNotebook.AddPage(self.armorAmmoPanel, "Ammo")
		self.armorAmmoPanel.SetSizer(self.armorAmmoSizer)
		
		#self.armorFamilySizer = wx.BoxSizer(wx.VERTICAL) # REMOVE i dont think this is much use
		#self.armorDetailsNotebook.AddPage(self.armorFamilyPanel, "Family") # REMOVE i dont think this is much use
		
		self.armorDetailedSizer.Add(self.armorImageLabel, 1, wx.ALIGN_CENTER)
		self.armorDetailedSizer.Add(self.armorDetailsNotebook, 3, wx.EXPAND)

		self.armorSizer.Add(self.armorTreeSizer, 2, wx.EXPAND)
		self.armorSizer.Add(self.armorDetailedSizer, 1, wx.EXPAND)

		self.armorPanel.SetSizer(self.armorSizer)
		
		self.initArmorButtons()
		self.initArmorTree()
		self.loadArmorTree()


	def initArmorButtons(self):
		# TODO change to appropriate icons
		self.lowRankButton = wx.BitmapButton(self.armorPanel, bitmap=self.testIcon, name="LR")
		self.highRankButton = wx.BitmapButton(self.armorPanel, bitmap=self.testIcon, name="HR")
		self.masterRankButton = wx.BitmapButton(self.armorPanel, bitmap=self.testIcon, name="MR")

		self.lowRankButton.Bind(wx.EVT_BUTTON, self.onArmorTypeSelection)
		self.highRankButton.Bind(wx.EVT_BUTTON, self.onArmorTypeSelection)
		self.masterRankButton.Bind(wx.EVT_BUTTON, self.onArmorTypeSelection)
	
		self.armorButtonsSizer = wx.BoxSizer(wx.HORIZONTAL)

		self.armorButtonsSizer.Add(self.lowRankButton)
		self.armorButtonsSizer.Add(self.highRankButton)
		self.armorButtonsSizer.Add(self.masterRankButton)

		self.armorTreeSizer.Add(self.armorButtonsSizer)


	def initArmorTree(self):
		self.armorTree = wx.lib.agw.hypertreelist.HyperTreeList(self.armorPanel, -1, style=0,
												agwStyle=
												gizmos.TR_DEFAULT_STYLE
												| gizmos.TR_ROW_LINES
												| gizmos.TR_COLUMN_LINES
												| gizmos.TR_FULL_ROW_HIGHLIGHT
												| gizmos.TR_HIDE_ROOT
												#| gizmos.TR_ELLIPSIZE_LONG_ITEMS
												)
		#self.armorTree.Bind(wx.EVT_TREE_SEL_CHANGED, self.onArmorSelection)
		self.armorTreeSizer.Add(self.armorTree, 1, wx.EXPAND)

		self.il = ail.ArmorImageList()
		self.armorTree.SetImageList(self.il.il)

		self.armorTree.AddColumn("Name") # 0
		
		self.armorTree.AddColumn("Rarity") # 1
		self.armorTree.AddColumn("Slot I") # 2
		self.armorTree.AddColumn("Slot II") # 3
		self.armorTree.AddColumn("Slot III") # 4
		self.armorTree.AddColumn("Defense") # 5
		self.armorTree.AddColumn("Defense Max") # 6
		self.armorTree.AddColumn("Defense Augmented Max") # 7
		self.armorTree.AddColumn("Fire") # 8
		self.armorTree.AddColumn("Water") # 9
		self.armorTree.AddColumn("Ice") # 10
		self.armorTree.AddColumn("Thunder") # 11
		self.armorTree.AddColumn("Dragon") # 12
		self.armorTree.AddColumn("id") # 13
		self.armorTree.AddColumn("armorSetID") # 14

		for num in range(1, 15):
			self.armorTree.SetColumnWidth(num, 29)
			self.armorTree.SetColumnAlignment(num, wx.ALIGN_CENTER)
		self.armorTree.SetColumnWidth(0, 200)

		for num in range(2, 5):
			self.armorTree.SetColumnImage(num, self.il.slots)

		for num in range(5, 8):
			self.armorTree.SetColumnImage(num, self.il.defense)

		self.armorTree.SetColumnImage(8, self.il.fire)
		self.armorTree.SetColumnImage(9, self.il.water)
		self.armorTree.SetColumnImage(10, self.il.ice)
		self.armorTree.SetColumnImage(11, self.il.thunder)
		self.armorTree.SetColumnImage(12, self.il.dragon)


	def loadArmorTree(self):
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
		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, ("en", self.currentArmorTree))
		data = data.fetchall()

		armorList = []
		
		for row in data:
			armorList.append(a.Armor(row))
		self.populateArmorTree(armorList)

		self.armorTree.ExpandAll()


	def populateArmorTree(self, armorList: List[Armor]) -> None:
		"""
		armorList = The list of all the queried Armor objects, which contain the data pertaining to the individual armor pieces.
		"""
		root = self.armorTree.AddRoot("Armor")
		armorSets = []
		for a in armorList:
			currentArmorSet = a.armorSetName
			if currentArmorSet in armorSets:
				armorPiece = self.armorTree.AppendItem(armorSetNode,  a.name)
			else:
				armorSetNode = self.armorTree.AppendItem(root,  a.armorSetName)
				self.armorTree.SetItemImage(armorSetNode, self.il.armorIcons["armorset"][a.rarity], which=wx.TreeItemIcon_Normal)
				armorPiece = self.armorTree.AppendItem(armorSetNode,  a.name)
				armorSets.append(currentArmorSet)
			self.armorTree.SetItemText(armorPiece, str(a.rarity), 1)
			self.armorTree.SetItemText(armorPiece, str(a.defenseBase), 5)
			self.armorTree.SetItemText(armorPiece, str(a.defenseMax), 6)
			self.armorTree.SetItemText(armorPiece, str(a.defenseAugmentedMax), 7)
			self.armorTree.SetItemText(armorPiece, str(a.fire), 8)
			self.armorTree.SetItemText(armorPiece, str(a.water), 9)
			self.armorTree.SetItemText(armorPiece, str(a.ice), 10)
			self.armorTree.SetItemText(armorPiece, str(a.thunder), 11)
			self.armorTree.SetItemText(armorPiece, str(a.dragon), 12)

			self.armorTree.SetItemText(armorPiece, str(a.id), 13)
			self.armorTree.SetItemText(armorPiece, str(a.armorSetID), 14)

			self.armorTree.SetItemImage(armorPiece, self.il.armorIcons[a.armorType][a.rarity], which=wx.TreeItemIcon_Normal)
			if a.slot1 != 0:
				self.armorTree.SetItemText(armorPiece, str(a.slot1), 2) 
				armorPiece.SetImage(2, self.il.slotIcons[a.slot1], wx.TreeItemIcon_Normal)
			if a.slot2 != 0:
				self.armorTree.SetItemText(armorPiece, str(a.slot2), 3)
				armorPiece.SetImage(3, self.il.slotIcons[a.slot2], wx.TreeItemIcon_Normal)
			if a.slot3 != 0:
				self.armorTree.SetItemText(armorPiece, str(a.slot3), 4)
				armorPiece.SetImage(4, self.il.slotIcons[a.slot3], wx.TreeItemIcon_Normal)


	def onArmorTypeSelection(self, event):
		"""
		When an armor rank button at the top of the screen is pressed the armor tree is reloaded with the new armor rank information.
		"""
		self.currentArmorTree = event.GetEventObject().GetName()
		self.armorTree.DeleteAllItems()
		self.loadArmorTree()
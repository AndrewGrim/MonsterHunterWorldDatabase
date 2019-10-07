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

wxTreeListItem = NewType('wxTreeListItem', None)

class ArmorTab:

	def __init__(self, root, mainNotebook):
		self.root = root
		self.mainNotebook = mainNotebook
		self.c = wx.ColourDatabase()

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

		# TODO maybe have the same button like in weapons tab but for loading only low/high/master rank armro??
		self.initWeaponsTab()


	def initWeaponsTab(self):
		self.weaponsPanel = wx.Panel(self.mainNotebook)
		self.mainNotebook.AddPage(self.weaponsPanel, "Armor")
		self.weaponsSizer = wx.BoxSizer(wx.HORIZONTAL)

		self.weaponsTreeSizer = wx.BoxSizer(wx.VERTICAL) 
		
		self.weaponsDetailedSizer = wx.BoxSizer(wx.VERTICAL)
		self.weaponImage = wx.Bitmap("images/weapons/great-sword/Buster Sword I.png", wx.BITMAP_TYPE_ANY)
		self.weaponImageLabel = wx.StaticBitmap(self.weaponsPanel, bitmap=self.weaponImage, size=(160, 160))

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
		
		self.weaponsDetailedSizer.Add(self.weaponImageLabel, 1, wx.ALIGN_CENTER)
		self.weaponsDetailedSizer.Add(self.weaponDetailsNotebook, 3, wx.EXPAND)

		self.weaponsSizer.Add(self.weaponsTreeSizer, 2, wx.EXPAND)
		self.weaponsSizer.Add(self.weaponsDetailedSizer, 1, wx.EXPAND)

		self.weaponsPanel.SetSizer(self.weaponsSizer)
		
		self.initWeaponsTree()


	def initWeaponsTree(self):
		self.weaponsTree = wx.lib.agw.hypertreelist.HyperTreeList(self.weaponsPanel, -1, style=0,
												agwStyle=
												gizmos.TR_DEFAULT_STYLE
												| gizmos.TR_ROW_LINES
												| gizmos.TR_COLUMN_LINES
												| gizmos.TR_FULL_ROW_HIGHLIGHT
												| gizmos.TR_HIDE_ROOT
												| gizmos.TR_ELLIPSIZE_LONG_ITEMS
												)
		#self.weaponsTree.Bind(wx.EVT_TREE_SEL_CHANGED, self.onWeaponSelection)
		self.weaponsTreeSizer.Add(self.weaponsTree, 1, wx.EXPAND)

		isz = (24, 24)
		self.il = wx.ImageList(isz[0], isz[1])

		self.test = self.il.Add(self.testIcon)

		#self.rarity1 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/1.png", wx.BITMAP_TYPE_ANY))
		#self.rarity2 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/2.png", wx.BITMAP_TYPE_ANY))
		#self.rarity3 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/3.png", wx.BITMAP_TYPE_ANY))
		#self.rarity4 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/4.png", wx.BITMAP_TYPE_ANY))
		#self.rarity5 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/5.png", wx.BITMAP_TYPE_ANY))
		#self.rarity6 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/6.png", wx.BITMAP_TYPE_ANY))
		#self.rarity7 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/7.png", wx.BITMAP_TYPE_ANY))
		#self.rarity8 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/8.png", wx.BITMAP_TYPE_ANY))
		# TODO iceborne
		#self.rarity9 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/9.png", wx.BITMAP_TYPE_ANY))
		#self.rarity10 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/10.png", wx.BITMAP_TYPE_ANY))
		#self.rarity11 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/11.png", wx.BITMAP_TYPE_ANY))
		#self.rarity12 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/12.png", wx.BITMAP_TYPE_ANY))

		self.weaponsTree.SetImageList(self.il)
		self.weaponDetailsNotebook.AssignImageList(self.il)

		self.weaponsTree.AddColumn("Name") # 0
		self.weaponsTree.AddColumn("") # Physical 1
		self.weaponsTree.AddColumn("") # Element/Status 2
		self.weaponsTree.AddColumn("") # Affinity 3
		self.weaponsTree.AddColumn("") # Defense 4
		self.weaponsTree.AddColumn("") # Slots 1 5
		self.weaponsTree.AddColumn("") # Slots 2 6
		self.weaponsTree.AddColumn("") # Slots 3 7
		
		self.weaponsTree.AddColumn("id") # 15
		
		self.weaponsTree.SetMainColumn(0)
		self.weaponsTree.SetColumnWidth(0, 400)

		#self.decorationSlotsIcons = {
		#	1: self.slots1,
		#	2: self.slots2,
		#	3: self.slots3,
		#}

		"""for num in range(1, 8):
			self.weaponsTree.SetColumnImage(num, self.weaponTreeIcons[num])
			self.weaponsTree.SetColumnAlignment(num, wx.ALIGN_CENTER)
			self.weaponsTree.SetColumnWidth(num, 24)"""

		self.weaponsTree.SetColumnWidth(1, 35)
		self.weaponsTree.SetColumnWidth(2, 60)
		self.weaponsTree.SetColumnWidth(3, 35)
		self.weaponsTree.SetColumnWidth(4, 35)
		self.weaponsTree.SetColumnWidth(5, 29)
		self.weaponsTree.SetColumnWidth(6, 29)
		self.weaponsTree.SetColumnWidth(7, 29)
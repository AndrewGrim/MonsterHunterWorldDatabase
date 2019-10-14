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
import Kinsect as k

wxTreeListItem = NewType('wxTreeListItem', None)
Kinsect = NewType('Kinsect', None)

class KinsectsTab:

	def __init__(self, root, mainNotebook):
		self.root = root
		self.mainNotebook = mainNotebook

		self.currentlySelectedKinsectID = 1
		self.testIcon = wx.Bitmap("images/unknown.png", wx.BITMAP_TYPE_ANY)

		self.initKinsectTab()


	def initKinsectTab(self):
		self.kinsectPanel = wx.Panel(self.mainNotebook)
		self.mainNotebook.AddPage(self.kinsectPanel, "Kinsects")
		self.kinsectSizer = wx.BoxSizer(wx.HORIZONTAL)

		self.kinsectTreeSizer = wx.BoxSizer(wx.VERTICAL) 
		
		self.kinsectDetailedSizer = wx.BoxSizer(wx.VERTICAL)
		self.kinsectImage = wx.Bitmap("images/weapons/great-sword/Buster Sword I.png", wx.BITMAP_TYPE_ANY)
		self.kinsectImageLabel = wx.StaticBitmap(self.kinsectPanel, bitmap=self.kinsectImage, size=(160, 160))

		self.kinsectDetailsNotebook = wx.Notebook(self.kinsectPanel)
		self.kinsectDetailPanel = wx.Panel(self.kinsectDetailsNotebook)
		
		self.kinsectDetailSizer = wx.BoxSizer(wx.VERTICAL)
		self.kinsectDetailsNotebook.AddPage(self.kinsectDetailPanel, "Detail")
		self.kinsectDetailPanel.SetSizer(self.kinsectDetailSizer)
		
		self.kinsectDetailedSizer.Add(self.kinsectImageLabel, 1, wx.ALIGN_CENTER)
		self.kinsectDetailedSizer.Add(self.kinsectDetailsNotebook, 3, wx.EXPAND)

		self.kinsectSizer.Add(self.kinsectTreeSizer, 1, wx.EXPAND)
		self.kinsectSizer.Add(self.kinsectDetailedSizer, 1, wx.EXPAND)

		self.kinsectPanel.SetSizer(self.kinsectSizer)
		
		self.initKinsectTree()
		self.initKinsectDetailTab()


	def initKinsectTree(self):
		self.kinsectTree = wx.lib.agw.hypertreelist.HyperTreeList(self.kinsectPanel, -1, style=0,
												agwStyle=
												gizmos.TR_DEFAULT_STYLE
												| gizmos.TR_ROW_LINES
												| gizmos.TR_COLUMN_LINES
												| gizmos.TR_FULL_ROW_HIGHLIGHT
												| gizmos.TR_HIDE_ROOT
												| gizmos.TR_ELLIPSIZE_LONG_ITEMS
												)
		self.kinsectTree.Bind(wx.EVT_TREE_SEL_CHANGED, self.onKinsectSelection)
		self.kinsectTreeSizer.Add(self.kinsectTree, 1, wx.EXPAND)

		isz = (24, 24)
		self.il = wx.ImageList(isz[0], isz[1])

		self.test = self.il.Add(self.testIcon)

		self.kinsectTree.SetImageList(self.il)

		self.kinsectTree.AddColumn("Name") # 0
		self.kinsectTree.AddColumn("") # attackType 1
		self.kinsectTree.AddColumn("") # dustEffect 2
		self.kinsectTree.AddColumn("") # power 3
		self.kinsectTree.AddColumn("") # speed 4
		self.kinsectTree.AddColumn("") # heal 5
		self.kinsectTree.AddColumn("id") # id 6
		
		self.kinsectTree.SetMainColumn(0)
		self.kinsectTree.SetColumnWidth(0, 400)

		for num in range(1, 6):
			self.kinsectTree.SetColumnAlignment(num, wx.ALIGN_CENTER)

		self.kinsectTree.SetColumnWidth(1, 70)
		self.kinsectTree.SetColumnWidth(2, 70)
		self.kinsectTree.SetColumnWidth(3, 45)
		self.kinsectTree.SetColumnWidth(4, 45)
		self.kinsectTree.SetColumnWidth(5, 45)
		self.kinsectTree.SetColumnWidth(6, 0)

		self.kinsectTree.SetColumnImage(1, self.test)
		self.kinsectTree.SetColumnImage(2, self.test)
		self.kinsectTree.SetColumnImage(3, self.test)
		self.kinsectTree.SetColumnImage(4, self.test)
		self.kinsectTree.SetColumnImage(5, self.test)

		self.loadKinsectTree()


	def loadKinsectTree(self):
		root = self.kinsectTree.AddRoot("Kinsect")

		sql = """
			SELECT k.*, kt.name
			FROM kinsect k
				JOIN kinsect_text kt USING (id)
			WHERE kt.lang_id = :langId
			ORDER BY k.id ASC
		"""

		conn = sqlite3.connect("mhw.db")
		data = conn.execute(sql, ("en", ))
		data = data.fetchall()

		kinsects = []
		for row in data:
			kinsects.append((k.Kinsect(row)))

		kinsectNodes = {}
		for kin in kinsects:
			if kin.previousID is None:
				self.populateKinsectTree(root, kin, kinsectNodes)
			else:
				self.populateKinsectTree(kinsectNodes[kin.previousID], kin, kinsectNodes)


		self.kinsectTree.ExpandAll()


	def populateKinsectTree(self, kinsectNode: wxTreeListItem, kin: Kinsect, kinsectNodes: Dict[int, wxTreeListItem]) -> None:
		kinsect = self.kinsectTree.AppendItem(kinsectNode,  kin.name)
		self.kinsectTree.SetItemImage(kinsect, self.test, which=wx.TreeItemIcon_Normal)
		self.kinsectTree.SetItemText(kinsect, kin.attackType, 1)
		self.kinsectTree.SetItemText(kinsect, kin.dustEffect, 2)
		self.kinsectTree.SetItemText(kinsect, f"Lv {kin.power}", 3)
		self.kinsectTree.SetItemText(kinsect, f"Lv {kin.speed}", 4)
		self.kinsectTree.SetItemText(kinsect, f"Lv {kin.heal}", 5)
		self.kinsectTree.SetItemText(kinsect, f"{kin.id}", 6)

		kinsectNodes[kin.id] = kinsect


	def initKinsectDetailTab(self):
		self.kinsectDetailList = wx.ListCtrl(self.kinsectDetailPanel, style=wx.LC_REPORT
																	| wx.LC_VRULES
																	| wx.LC_HRULES
																	)
		self.kinsectDetailList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
		self.kinsectDetailSizer.Add(self.kinsectDetailList, 1, wx.EXPAND)

		self.kinsectMaterialList = wx.ListCtrl(self.kinsectDetailPanel, style=wx.LC_REPORT
																		| wx.LC_VRULES
																		| wx.LC_HRULES
																		)
		self.kinsectMaterialList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
		self.kinsectDetailSizer.Add(self.kinsectMaterialList, 1, wx.EXPAND)

		self.loadKinsectDetails()	
		self.loadKinsectMaterials()


	def loadKinsectDetails(self):
		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_CENTER
		info.Text = ""
		self.kinsectDetailList.InsertColumn(0, info)
		self.kinsectDetailList.SetColumnWidth(0, 480)
		self.kinsectDetailList.InsertColumn(1, info)
		self.kinsectDetailList.SetColumnWidth(1, 200)


		sql = """
			SELECT k.*, kt.name
			FROM kinsect k
				JOIN kinsect_text kt USING (id)
			WHERE kt.lang_id = :langId
				AND k.id = :kinId
			ORDER BY k.id ASC
		"""

		conn = sqlite3.connect("mhw.db")
		data = conn.execute(sql, ("en", self.currentlySelectedKinsectID))
		data = data.fetchone()

		kin = k.Kinsect(data)

		index = self.kinsectDetailList.InsertItem(self.kinsectDetailList.GetItemCount(), "Rarity", self.test)
		self.kinsectDetailList.SetItem(index, 1, f"{kin.rarity}")
		index = self.kinsectDetailList.InsertItem(self.kinsectDetailList.GetItemCount(), "Attack Type", self.test)
		self.kinsectDetailList.SetItem(index, 1, f"{kin.attackType}")
		index = self.kinsectDetailList.InsertItem(self.kinsectDetailList.GetItemCount(), "Dust Effect", self.test)
		self.kinsectDetailList.SetItem(index, 1, f"{kin.dustEffect}")
		index = self.kinsectDetailList.InsertItem(self.kinsectDetailList.GetItemCount(), "Power", self.test)
		self.kinsectDetailList.SetItem(index, 1, f"{kin.power}")
		index = self.kinsectDetailList.InsertItem(self.kinsectDetailList.GetItemCount(), "Speed", self.test)
		self.kinsectDetailList.SetItem(index, 1, f"{kin.speed}")
		index = self.kinsectDetailList.InsertItem(self.kinsectDetailList.GetItemCount(), "Heal", self.test)
		self.kinsectDetailList.SetItem(index, 1, f"{kin.heal}")


	def loadKinsectMaterials(self):
		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = "Req. Materials"
		self.kinsectMaterialList.InsertColumn(0, info)
		self.kinsectMaterialList.SetColumnWidth(0, 480)

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_CENTER
		info.Text = ""
		self.kinsectMaterialList.InsertColumn(1, info)
		self.kinsectMaterialList.SetColumnWidth(1, 200)


		sql = """
			SELECT k.id, kr.item_id, kr.quantity, kt.name,
				i.category, i.icon_name, i.icon_color, it.name
			FROM kinsect k
				JOIN kinsect_recipe kr
					ON k.id = kr.kinsect_id
				JOIN item i
					ON kr.item_id = i.id
				JOIN item_text it
					ON kr.item_id = it.id
				JOIN kinsect_text kt USING (id)
			WHERE kt.lang_id = :langId
				AND it.lang_id = :langId
				AND k.id = :kinId
		"""

		conn = sqlite3.connect("mhw.db")
		data = conn.execute(sql, ("en", self.currentlySelectedKinsectID))
		data = data.fetchall()

		materials = []
		for row in data:
			materials.append(k.KinsectMaterial(row))

		for mat in materials:
			index = self.kinsectMaterialList.InsertItem(self.kinsectMaterialList.GetItemCount(), mat.name, self.test)
			self.kinsectMaterialList.SetItem(index, 1, f"{mat.quantity}")
		

	def onKinsectSelection(self, event):
		"""
		When a specific kinsect is selected in the tree, the detail view gets populated with the information from the database.
		"""
		self.currentlySelectedKinsectID = self.kinsectTree.GetItemText(event.GetItem(), 6)

		self.kinsectDetailList.ClearAll()
		self.kinsectMaterialList.ClearAll()
		self.loadKinsectDetails()
		self.loadKinsectMaterials()
		width, height = self.kinsectDetailPanel.GetSize()
		self.kinsectDetailPanel.SetSize(width + 1, height + 1)
		self.kinsectDetailPanel.SetSize(width, height)
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
import KinsectsTab as k

wxTreeListItem = NewType('wxTreeListItem', None)
kKinsect = NewType('Kinsect', None)

class KinsectsTab:

	def __init__(self, root, mainNotebook):
		self.root = root
		self.mainNotebook = mainNotebook

		self.currentlySelectedKinsectID = 1
		self.testIcon = wx.Bitmap("images/unknown.png", wx.BITMAP_TYPE_ANY)

		self.kinsectDetail = {
			1: ["images/unknown.png", "Rarity"],
			2: ["images/weapon-detail-24/attacktype.png", "Attack Type"],
			3: ["images/weapon-detail-24/dusteffect.png", "Dust Effect"],
			4: ["images/weapon-detail-24/power.png", "Power"],
			5: ["images/weapon-detail-24/speed.png", "Speed"],
			6: ["images/weapon-detail-24/heal.png", "Heal"],
		}

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

		self.initKinsectTab()


	def initKinsectTab(self):
		self.kinsectPanel = wx.Panel(self.mainNotebook)
		self.mainNotebook.AddPage(self.kinsectPanel, "Kinsects")
		self.kinsectSizer = wx.BoxSizer(wx.HORIZONTAL)

		self.kinsectTreeSizer = wx.BoxSizer(wx.VERTICAL) 
		
		self.kinsectDetailedSizer = wx.BoxSizer(wx.VERTICAL)
		kinsectImage = wx.Bitmap("images/kinsects/Culldrone I.jpg", wx.BITMAP_TYPE_ANY)
		self.kinsectImageLabel = wx.StaticBitmap(self.kinsectPanel, bitmap=kinsectImage, size=(230, 230))
		self.kinsectImageLabel.SetBackgroundColour((0, 0, 0))

		self.kinsectDetailsNotebook = wx.Notebook(self.kinsectPanel)
		self.kinsectDetailPanel = wx.Panel(self.kinsectDetailsNotebook)
		
		self.kinsectDetailSizer = wx.BoxSizer(wx.VERTICAL)
		self.kinsectDetailsNotebook.AddPage(self.kinsectDetailPanel, "Detail")
		self.kinsectDetailPanel.SetSizer(self.kinsectDetailSizer)

		self.kinsectDetailedImagesSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.kinsectDetailedImagesSizer.Add(self.kinsectImageLabel, 1, wx.ALIGN_CENTER)
		
		self.kinsectDetailedSizer.Add(self.kinsectImageLabel, 1, wx.EXPAND)
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
			kinsects.append(k.Kinsect(row))

		kinsectNodes = {}
		for kin in kinsects:
			if kin.previousID is None:
				self.populateKinsectTree(root, kin, kinsectNodes)
			else:
				self.populateKinsectTree(kinsectNodes[kin.previousID], kin, kinsectNodes)


		self.kinsectTree.ExpandAll()


	def populateKinsectTree(self, kinsectNode: wxTreeListItem, kin: kKinsect, kinsectNodes: Dict[int, wxTreeListItem]) -> None:
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
		self.kinsectDetailList = cgr.HeaderBitmapGrid(self.kinsectDetailPanel)
		self.kinsectDetailList.Bind(wx.EVT_SIZE, self.onSize)
		self.kinsectDetailList.EnableEditing(False)
		self.kinsectDetailList.EnableDragRowSize(False)
		self.kinsectDetailSizer.Add(self.kinsectDetailList, 1, wx.EXPAND)

		self.kinsectDetailList.CreateGrid(len(self.kinsectDetail) + 1, 2)
		self.kinsectDetailList.SetDefaultRowSize(24, resizeExistingRows=True)
		self.kinsectDetailList.SetColSize(0, 302)
		self.kinsectDetailList.SetColSize(1, 155 - 20)
		self.kinsectDetailList.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
		self.kinsectDetailList.SetColLabelSize(2)
		self.kinsectDetailList.SetRowLabelSize(1)

		self.kinsectMaterialList = wx.ListCtrl(self.kinsectDetailPanel, style=wx.LC_REPORT
																		| wx.LC_VRULES
																		| wx.LC_HRULES
																		)
		self.kinsectMaterialList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
		self.kinsectDetailSizer.Add(self.kinsectMaterialList, 1, wx.EXPAND)

		self.loadKinsectDetails()	


	def loadKinsectDetails(self):
		self.root.Freeze()
		self.kinsectDetailList.DeleteRows(0, self.kinsectDetailList.GetNumberRows())
		self.kinsectDetailList.AppendRows(len(self.kinsectDetail) + 1)

		self.kinsectMaterialList.ClearAll()
		self.il.RemoveAll()

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

		kinsectDetail = {
			0: str(kin.name),
			1: str(kin.rarity),
			2: str(kin.attackType),
			3: str(kin.dustEffect),
			4: str(kin.power),
			5: str(kin.speed),
			6: str(kin.heal),
		}

		imageOffset = 55
		self.kinsectImageLabel.SetBitmap(wx.Bitmap(f"images/kinsects/{kin.name}.jpg"))
		rarityIcon = wx.Bitmap(f"images/kinsects/{kin.attackType.lower()}-rarity-24/{kin.rarity}.png")
		self.kinsectDetailList.SetCellValue(0, 0, "Name")
		self.kinsectDetailList.SetCellValue(0, 1, kin.name)
		for num in range(1, len(kinsectDetail)):
			if num == 1:
				self.kinsectDetailList.SetCellRenderer(num, 0,
									cgr.ImageTextCellRenderer(
																rarityIcon,
																self.kinsectDetail[num][1],
																imageOffset=imageOffset,
															))
				self.kinsectDetailList.SetCellBackgroundColour(num, 1, util.hexToRGB(self.rarityColors[kin.rarity]))
			else:
				self.kinsectDetailList.SetCellRenderer(num, 0,
									cgr.ImageTextCellRenderer(
										wx.Bitmap(self.kinsectDetail[num][0]), 
										self.kinsectDetail[num][1], 
										imageOffset=imageOffset
										))

			if kinsectDetail[num] == None:
				self.kinsectDetailList.SetCellValue(num, 1, "-")
			else:
				self.kinsectDetailList.SetCellValue(num, 1, str(kinsectDetail[num]))

		self.loadKinsectMaterials()


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
			ORDER BY i.id
		"""

		conn = sqlite3.connect("mhw.db")
		data = conn.execute(sql, ("en", self.currentlySelectedKinsectID))
		data = data.fetchall()

		materials = []
		for row in data:
			materials.append(k.KinsectMaterial(row))

		for mat in materials:
			img = self.il.Add(wx.Bitmap(f"images/items-24/{mat.iconName}{mat.iconColor}.png"))
			index = self.kinsectMaterialList.InsertItem(self.kinsectMaterialList.GetItemCount(), mat.name, self.test)
			self.kinsectMaterialList.SetItem(index, 1, f"{mat.quantity}")

		width, height = self.kinsectPanel.GetSize()
		self.kinsectPanel.SetSize(width + 1, height + 1)
		self.kinsectPanel.SetSize(width, height)
		self.root.Thaw()
		

	def onKinsectSelection(self, event):
		"""
		When a specific kinsect is selected in the tree, the detail view gets populated with the information from the database.
		"""
		self.currentlySelectedKinsectID = self.kinsectTree.GetItemText(event.GetItem(), 6)

		self.loadKinsectDetails()


	def onSize(self, event):
		"""
		When the application window is resized some columns's width gets readjusted.
		"""

		try:
			self.kinsectDetailList.SetColSize(0, self.kinsectDetailPanel.GetSize()[0] * 0.66)
			self.kinsectDetailList.SetColSize(1, self.kinsectDetailPanel.GetSize()[0] * 0.34 - 20)
			self.kinsectMaterialList.SetColumnWidth(0, self.kinsectDetailPanel.GetSize()[0] * 0.66)
			self.kinsectMaterialList.SetColumnWidth(1, self.kinsectDetailPanel.GetSize()[0] * 0.34 - 40)
		except:
			pass
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
import Decoration as d
import DecorationDetail as dd

class DecorationsTab:

	def __init__(self, root, mainNotebook):
		self.root = root
		self.mainNotebook = mainNotebook
		self.currentDecorationID = 1
		self.testIcon = wx.Bitmap("images/unknown.png", wx.BITMAP_TYPE_ANY)
		self.initItemTab()


	def initItemTab(self):
		self.itemPanel = wx.Panel(self.mainNotebook)
		self.mainNotebook.AddPage(self.itemPanel, "Decorations")
		self.itemsSizer = wx.BoxSizer(wx.HORIZONTAL)

		self.itemListSizer = wx.BoxSizer(wx.VERTICAL) 
		
		self.itemDetailedSizer = wx.BoxSizer(wx.VERTICAL)
		self.itemImage = wx.Bitmap("images/weapons/great-sword/Buster Sword I.png", wx.BITMAP_TYPE_ANY)
		self.itemImageLabel = wx.StaticBitmap(self.itemPanel, bitmap=self.itemImage, size=(160, 160))

		self.itemDetailsNotebook = wx.Notebook(self.itemPanel)
		self.itemDetailPanel = wx.Panel(self.itemDetailsNotebook)

		self.itemDetailSizer = wx.BoxSizer(wx.VERTICAL)
		self.itemDetailsNotebook.AddPage(self.itemDetailPanel, "Detail")
		self.itemDetailPanel.SetSizer(self.itemDetailSizer)
		
		self.itemDetailedSizer.Add(self.itemImageLabel, 1, wx.ALIGN_CENTER)
		self.itemDetailedSizer.Add(self.itemDetailsNotebook, 3, wx.EXPAND)

		self.itemsSizer.Add(self.itemListSizer, 1, wx.EXPAND)
		self.itemsSizer.Add(self.itemDetailedSizer, 1, wx.EXPAND)

		self.itemPanel.SetSizer(self.itemsSizer)

		self.initItemList()
		self.loadItemList()

		self.initItemDetail()
		self.loadItemDetail()

		self.root.SetSize(self.root.windowWidth, self.root.windowHeight)


	def initItemList(self):
		self.itemList = wx.ListCtrl(self.itemPanel, style=wx.LC_REPORT
														| wx.LC_VRULES
														| wx.LC_HRULES
														)
		self.itemListSizer.Add(self.itemList, 1, wx.EXPAND)
		self.itemList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onDecorationSelected)

		isz = (24, 24)
		self.il = wx.ImageList(isz[0], isz[1])
		self.test = self.il.Add(self.testIcon)
		self.itemList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)


	def loadItemList(self):
		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = ""
		self.itemList.InsertColumn(0, info)
		self.itemList.SetColumnWidth(0, 680)
		self.itemList.InsertColumn(1, info)
		self.itemList.SetColumnWidth(1, 0)


		sql = """
			SELECT d.id, dt.name, d.slot, d.icon_color
			FROM decoration d
				JOIN decoration_text dt
					ON dt.id = d.id
					AND dt.lang_id = :langId
			ORDER BY dt.name
		"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, ("en", ))
		data = data.fetchall()

		decorations = []
		for row in data:
			decorations.append(d.Decoration(row))

		for deco in decorations:
			index = self.itemList.InsertItem(self.itemList.GetItemCount(), deco.name, self.test)
			self.itemList.SetItem(index, 1, f"{deco.id}")


	def initItemDetail(self):
		self.skillList = wx.ListCtrl(self.itemDetailPanel, style=wx.LC_REPORT
														| wx.LC_VRULES
														| wx.LC_HRULES
														)
		self.itemDetailSizer.Add(self.skillList, 1, wx.EXPAND)
		self.skillList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.dropList = wx.ListCtrl(self.itemDetailPanel, style=wx.LC_REPORT
														| wx.LC_VRULES
														| wx.LC_HRULES
														)
		self.itemDetailSizer.Add(self.dropList, 7, wx.EXPAND)
		self.dropList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)


	def loadItemDetail(self):
		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = "Skill"
		self.skillList.InsertColumn(0, info)
		self.skillList.SetColumnWidth(0, 580)
		info = wx.ListItem()

		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = ""
		self.skillList.InsertColumn(1, info)
		self.skillList.SetColumnWidth(1, 100)


		sql = """
			SELECT d.*, dtext.name,
				s.id skill_id, stext.name skill_name, s.max_level skill_max_level, s.icon_color skill_icon_color,
				skill.level
			FROM decoration d
				JOIN decoration_text dtext
					ON dtext.id = d.id
				JOIN skilltree s
					ON s.id = d.skilltree_id
				JOIN skilltree_text stext
					ON stext.id = s.id
					AND stext.lang_id = dtext.lang_id
				JOIN skill
					ON skill.skilltree_id = d.skilltree_id
			WHERE d.id = :decorationId
			AND dtext.lang_id = :langId
		"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, (self.currentDecorationID, "en"))
		data = data.fetchone()

		deco = dd.DecorationDetail(data)
		print(data)
		print(deco)
		lvl = deco.skillLevel * "◈"
		maxLvl = (deco.skillMaxLevel - deco.skillLevel) * "◇"
		index = self.skillList.InsertItem(self.skillList.GetItemCount(), deco.skillName, self.test)
		self.skillList.SetItem(index, 1, f"{lvl}{maxLvl}")

		self.loadDecorationDrop(deco)


	def loadDecorationDrop(self, Decoration):
		deco = Decoration

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = "Drop"
		self.dropList.InsertColumn(0, info)
		self.dropList.SetColumnWidth(0, 580)
		info = wx.ListItem()

		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = ""
		self.dropList.InsertColumn(1, info)
		self.dropList.SetColumnWidth(1, 100)

		index = self.dropList.InsertItem(self.dropList.GetItemCount(), "Mysterious Feystone", self.test)
		self.dropList.SetItem(index, 1, f"{deco.mysteriousFeystonePercent}%")
		index = self.dropList.InsertItem(self.dropList.GetItemCount(), "Glowing Feystone", self.test)
		self.dropList.SetItem(index, 1, f"{deco.glowingFeystonePercent}%")
		index = self.dropList.InsertItem(self.dropList.GetItemCount(), "Worn Feystone", self.test)
		self.dropList.SetItem(index, 1, f"{deco.wornFeystonePercent}%")
		index = self.dropList.InsertItem(self.dropList.GetItemCount(), "Warped Feystone", self.test)
		self.dropList.SetItem(index, 1, f"{deco.warpedFeystonePercent}%")


	def onDecorationSelected(self, event):
		self.currentDecorationID = self.itemList.GetItemText(event.GetEventObject().GetFirstSelected(), 1)
		if int(self.currentDecorationID) > 0:
			self.skillList.ClearAll()
			self.dropList.ClearAll()
		self.loadItemDetail()
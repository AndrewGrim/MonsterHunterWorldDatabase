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

import DecorationsTab as d
import Links as link

class DecorationsTab:

	def __init__(self, root, mainNotebook, link):
		self.root = root
		self.mainNotebook = mainNotebook
		self.link = link

		self.currentDecorationID = 1
		self.testIcon = wx.Bitmap("images/unknown.png", wx.BITMAP_TYPE_ANY)
		self.initItemTab()


	def initItemTab(self):
		self.decorationPanel = wx.Panel(self.mainNotebook)
		self.mainNotebook.AddPage(self.decorationPanel, "Decorations")
		self.decorationSizer = wx.BoxSizer(wx.HORIZONTAL)

		self.decorationListSizer = wx.BoxSizer(wx.VERTICAL) 
		
		self.decorationDetailedSizer = wx.BoxSizer(wx.VERTICAL)
		self.decorationImage = wx.Bitmap("images/items-160/FeystoneViolet.png", wx.BITMAP_TYPE_ANY)
		self.decorationImageLabel = wx.StaticBitmap(self.decorationPanel, bitmap=self.decorationImage, size=(160, 160))

		self.decorationDetailsNotebook = wx.Notebook(self.decorationPanel)
		self.decorationDetailPanel = wx.Panel(self.decorationDetailsNotebook)

		self.decorationDetailSizer = wx.BoxSizer(wx.VERTICAL)
		self.decorationDetailsNotebook.AddPage(self.decorationDetailPanel, "Detail")
		self.decorationDetailPanel.SetSizer(self.decorationDetailSizer)
		
		self.decorationDetailedSizer.Add(self.decorationImageLabel, 1, wx.ALIGN_CENTER)
		self.decorationDetailedSizer.Add(self.decorationDetailsNotebook, 3, wx.EXPAND)

		self.decorationSizer.Add(self.decorationListSizer, 1, wx.EXPAND)
		self.decorationSizer.Add(self.decorationDetailedSizer, 1, wx.EXPAND)

		self.decorationPanel.SetSizer(self.decorationSizer)

		self.initSearch()
		self.initDecorationList()
		self.initDecorationDetail()
		self.loadDecorationList()

		self.decorationList.Bind(wx.EVT_SIZE, self.onSize)

	
	def initSearch(self):
		self.searchName = wx.TextCtrl(self.decorationPanel, name="byName")
		self.searchName.SetHint("  search by name")
		self.searchName.Bind(wx.EVT_TEXT, self.onSearchTextEnter)

		self.searchSkill = wx.TextCtrl(self.decorationPanel, name="bySkill")
		self.searchSkill.SetHint("  search by skill")
		self.searchSkill.Bind(wx.EVT_TEXT, self.onSearchTextEnter)

		self.currentSearch = self.searchName

		self.searchSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.searchSizer.Add(self.searchName)
		self.searchSizer.Add(self.searchSkill)

		self.decorationListSizer.Add(self.searchSizer)


	def onSearchTextEnter(self, event):
		self.currentSearch = event.GetEventObject()
		self.loadDecorationList()


	def initDecorationList(self):
		self.decorationList = wx.ListCtrl(self.decorationPanel, style=wx.LC_REPORT
														| wx.LC_VRULES
														| wx.LC_HRULES
														)
		self.decorationListSizer.Add(self.decorationList, 1, wx.EXPAND)
		self.decorationList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onDecorationSelected)

		self.il = wx.ImageList(24, 24)
		self.test = self.il.Add(self.testIcon)
		self.decorationList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)


	def loadDecorationList(self):
		try:
			self.decorationList.ClearAll()
		except:
			pass

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = ""
		self.decorationList.InsertColumn(0, info)
		self.decorationList.SetColumnWidth(0, 680)
		self.decorationList.InsertColumn(1, info)
		self.decorationList.SetColumnWidth(1, 0)

		searchText = self.currentSearch.GetValue()

		if len(searchText) == 0 or searchText == " ":
			sql = """
				SELECT d.id, dt.name, d.slot, d.icon_color
				FROM decoration d
					JOIN decoration_text dt
						ON dt.id = d.id
						AND dt.lang_id = :langId
				ORDER BY dt.name
			"""
		else:
			if self.currentSearch.GetName() == "bySkill":
				sql = f"""
					SELECT d.id, dt.name, d.slot, d.icon_color, stt.name
					FROM decoration d
						JOIN decoration_text dt
							ON dt.id = d.id
							AND dt.lang_id = :langId
						JOIN skilltree_text stt
							ON stt.id = d.skilltree_id
							AND stt.lang_id = :langId
						WHERE stt.name LIKE '%{searchText}%'
					ORDER BY dt.name
				"""
			else:
				sql = f"""
					SELECT d.id, dt.name, d.slot, d.icon_color
					FROM decoration d
						JOIN decoration_text dt
							ON dt.id = d.id
							AND dt.lang_id = :langId
						WHERE dt.name LIKE '%{searchText}%'
					ORDER BY dt.name
				"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, ("en", ))
		data = data.fetchall()

		decorations = []
		for row in data:
			decorations.append(d.Decoration(row))

		if len(decorations) != 0:
			self.il.RemoveAll()

		for deco in decorations:
			if deco.iconColor != None:
				img = self.il.Add(wx.Bitmap(f"images/items-24/Feystone{deco.iconColor}.png"))
			else:
				img = self.test
			index = self.decorationList.InsertItem(self.decorationList.GetItemCount(), deco.name, img)
			self.decorationList.SetItem(index, 1, f"{deco.id}")

		if self.decorationList.GetItemCount() != 0:
			self.decorationList.Select(0)


	def initDecorationDetail(self):
		self.decorationNameLabel = wx.StaticText(self.decorationDetailPanel, label = "placeholder")
		self.decorationNameLabel.SetFont(self.decorationNameLabel.GetFont().Bold())
		self.decorationDetailSizer.Add(self.decorationNameLabel, 1, wx.EXPAND)

		self.skillList = wx.ListCtrl(self.decorationDetailPanel, style=wx.LC_REPORT
														| wx.LC_VRULES
														| wx.LC_HRULES
														)
		self.skillList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onSkillDoubleClick)
		self.decorationDetailSizer.Add(self.skillList, 1, wx.EXPAND)
		self.skillList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.dropList = wx.ListCtrl(self.decorationDetailPanel, style=wx.LC_REPORT
														| wx.LC_VRULES
														| wx.LC_HRULES
														)
		self.decorationDetailSizer.Add(self.dropList, 7, wx.EXPAND)
		self.dropList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)


	def loadDecorationDetail(self):
		self.root.Freeze()

		self.skillList.ClearAll()
		
		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = "Skill"
		self.skillList.InsertColumn(0, info)
		self.skillList.SetColumnWidth(0, self.decorationDetailPanel.GetSize()[0] * 0.66)
		info = wx.ListItem()

		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = ""
		self.skillList.InsertColumn(1, info)
		self.skillList.SetColumnWidth(1, self.decorationDetailPanel.GetSize()[0] * 0.34 - 20)

		self.skillList.InsertColumn(2, info)
		self.skillList.SetColumnWidth(2, 0)

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

		deco = d.DecorationDetail(data)
		if self.root.pref.unicodeSymbols:
			lvl = deco.skillLevel * "◈"
			maxLvl = (deco.skillMaxLevel - deco.skillLevel) * "◇"
		else:
			lvl = f"{deco.skillLevel}/"
			maxLvl = deco.skillMaxLevel
		self.decorationImageLabel.SetBitmap(wx.Bitmap(f"images/items-160/Feystone{deco.iconColor}.png"))
		self.decorationNameLabel.SetLabelText(f"\n{deco.name}\n")
		if deco.iconColor != None:
			img = self.il.Add(wx.Bitmap(f"images/skills-24/Skill{deco.skillIconColor}.png"))
		else:
			img = self.test
		index = self.skillList.InsertItem(self.skillList.GetItemCount(), deco.skillName, img)
		self.skillList.SetItem(index, 1, f"{lvl}{maxLvl}")
		self.skillList.SetItem(index, 2, f"{deco.skillTreeID}")

		self.loadDecorationDrop(deco)


	def loadDecorationDrop(self, Decoration):
		self.dropList.ClearAll()

		deco = Decoration

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = "Drop"
		self.dropList.InsertColumn(0, info)
		self.dropList.SetColumnWidth(0, self.decorationDetailPanel.GetSize()[0] * 0.66)
		info = wx.ListItem()

		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = ""
		self.dropList.InsertColumn(1, info)
		self.dropList.SetColumnWidth(1, self.decorationDetailPanel.GetSize()[0] * 0.34 - 20)

		
		img = self.il.Add(wx.Bitmap(f"images/items-24/FeystoneGray.png"))
		index = self.dropList.InsertItem(self.dropList.GetItemCount(), "Mysterious Feystone", img)
		self.dropList.SetItem(index, 1, f"{deco.mysteriousFeystonePercent}%")
		img = self.il.Add(wx.Bitmap(f"images/items-24/FeystoneBlue.png"))
		index = self.dropList.InsertItem(self.dropList.GetItemCount(), "Glowing Feystone", img)
		self.dropList.SetItem(index, 1, f"{deco.glowingFeystonePercent}%")
		img = self.il.Add(wx.Bitmap(f"images/items-24/FeystoneBeige.png"))
		index = self.dropList.InsertItem(self.dropList.GetItemCount(), "Worn Feystone", img)
		self.dropList.SetItem(index, 1, f"{deco.wornFeystonePercent}%")
		img = self.il.Add(wx.Bitmap(f"images/items-24/FeystoneRed.png"))
		index = self.dropList.InsertItem(self.dropList.GetItemCount(), "Warped Feystone", img)
		self.dropList.SetItem(index, 1, f"{deco.warpedFeystonePercent}%")

		self.root.Thaw()


	def onDecorationSelected(self, event):
		self.currentDecorationID = self.decorationList.GetItemText(event.GetEventObject().GetFirstSelected(), 1)
		if int(self.currentDecorationID) > 0:
			self.loadDecorationDetail()

	
	def onSkillDoubleClick(self, event):
		materialInfo = event.GetEventObject().GetItemText(event.GetEventObject().GetFirstSelected(), 2)
		self.link.event = True
		self.link.eventType = "skill"
		self.link.info =  link.GenericSingleLink(materialInfo)
		self.root.followLink()
		self.link.reset()


	def onSize(self, event):
		self.skillList.SetColumnWidth(0, self.decorationDetailPanel.GetSize()[0] * 0.66)
		self.skillList.SetColumnWidth(1, self.decorationDetailPanel.GetSize()[0] * 0.34 - 20)
		self.dropList.SetColumnWidth(0, self.decorationDetailPanel.GetSize()[0] * 0.66)
		self.dropList.SetColumnWidth(1, self.decorationDetailPanel.GetSize()[0] * 0.34 - 20)
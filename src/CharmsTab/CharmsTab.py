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

import CharmsTab as c
from Utilities import debug
import Links as link

class CharmsTab:

	def __init__(self, root, mainNotebook, link):
		self.root = root
		self.mainNotebook = mainNotebook
		self.link = link

		self.currentCharmID = 1
		self.currentCharmName = "Poison Charm I"
		self.testIcon = wx.Bitmap("images/unknown.png", wx.BITMAP_TYPE_ANY)
		self.initSkillTab()


	def initSkillTab(self):
		self.charmPanel = wx.Panel(self.mainNotebook)
		self.mainNotebook.AddPage(self.charmPanel, "Charms")
		self.charmSizer = wx.BoxSizer(wx.HORIZONTAL)

		self.charmListSizer = wx.BoxSizer(wx.VERTICAL) 
		
		self.charmDetailedSizer = wx.BoxSizer(wx.VERTICAL)
		self.charmImage = wx.Bitmap("images/charms/Artillery Charm I.png", wx.BITMAP_TYPE_ANY)
		self.charmImageLabel = wx.StaticBitmap(self.charmPanel, bitmap=self.charmImage, size=(160, 160))
		self.charmImageLabel.SetBackgroundColour((0, 0, 0))

		self.charmDetailsNotebook = wx.Notebook(self.charmPanel)
		self.charmDetailPanel = wx.Panel(self.charmDetailsNotebook)

		self.charmDetailSizer = wx.BoxSizer(wx.VERTICAL)
		self.charmDetailsNotebook.AddPage(self.charmDetailPanel, "Detail")
		self.charmDetailPanel.SetSizer(self.charmDetailSizer)
		
		self.charmDetailedSizer.Add(self.charmImageLabel, 1, wx.EXPAND)
		self.charmDetailedSizer.Add(self.charmDetailsNotebook, 3, wx.EXPAND)

		self.charmSizer.Add(self.charmListSizer, 1, wx.EXPAND)
		self.charmSizer.Add(self.charmDetailedSizer, 1, wx.EXPAND)

		self.charmPanel.SetSizer(self.charmSizer)

		self.initSearch()
		self.initCharmList()
		self.initCharmDetail()
		self.loadCharmList()

		self.charmList.Bind(wx.EVT_SIZE, self.onSize)


	def initSearch(self):
		self.searchName = wx.TextCtrl(self.charmPanel, name="byName")
		self.searchName.SetHint("  search by name")
		self.searchName.Bind(wx.EVT_TEXT, self.onSearchTextEnter)

		self.searchSkill = wx.TextCtrl(self.charmPanel, name="bySkill")
		self.searchSkill.SetHint("  search by skill")
		self.searchSkill.Bind(wx.EVT_TEXT, self.onSearchTextEnter)

		self.currentSearch = self.searchName

		self.searchSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.searchSizer.Add(self.searchName)
		self.searchSizer.Add(self.searchSkill)

		self.charmListSizer.Add(self.searchSizer)


	def onSearchTextEnter(self, event):
		self.currentSearch = event.GetEventObject()
		self.loadCharmList()


	def initCharmList(self):
		self.charmList = wx.ListCtrl(self.charmPanel, style=wx.LC_REPORT
														| wx.LC_VRULES
														| wx.LC_HRULES
														)
		self.charmListSizer.Add(self.charmList, 1, wx.EXPAND)
		self.charmList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onCharmSelected)

		self.il = wx.ImageList(24, 24)
		self.test = self.il.Add(self.testIcon)
		self.charmList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)


	def loadCharmList(self):
		try:
			self.charmList.ClearAll()
		except:
			pass

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = ""
		self.charmList.InsertColumn(0, info)
		self.charmList.SetColumnWidth(0, 680)
		self.charmList.InsertColumn(1, info)
		self.charmList.SetColumnWidth(1, 0)

		searchText = self.currentSearch.GetValue()

		if len(searchText) == 0 or searchText == " ":
			sql = """
				SELECT c.*, ct.name
				FROM charm c
					JOIN charm_text ct
						ON ct.id = c.id
						AND ct.lang_id = :langId
				ORDER BY ct.name
			"""
		else:
			if self.currentSearch.GetName() == "bySkill":
				sql = f"""
					SELECT c.*, ct.name, stt.name
					FROM charm c
						JOIN charm_text ct
							ON ct.id = c.id
							AND ct.lang_id = :langId
						JOIN charm_skill cs
							ON cs.charm_id = c.id
						JOIN skilltree_text stt
							ON stt.id = cs.skilltree_id
							AND stt.lang_id = :langId
						WHERE stt.name LIKE '%{searchText}%'
					ORDER BY ct.name
				"""
			else:
				sql = f"""
					SELECT c.*, ct.name
					FROM charm c
						JOIN charm_text ct
							ON ct.id = c.id
							AND ct.lang_id = :langId
							AND ct.name LIKE '%{searchText}%'
					ORDER BY ct.name
				"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, ("en", ))
		data = data.fetchall()

		charms = []
		for row in data:
			charms.append(c.Charm(row))

		if len(charms) != 0:
			self.il.RemoveAll()

		for charm in charms:
			img = self.il.Add(wx.Bitmap(f"images/charms-24/{charm.rarity}.png"))
			index = self.charmList.InsertItem(self.charmList.GetItemCount(), charm.name, img)
			self.charmList.SetItem(index, 1, f"{charm.id}")

		if self.charmList.GetItemCount() != 0:
			self.charmList.Select(0)


	def initCharmDetail(self):
		self.charmNameLabel = wx.StaticText(self.charmDetailPanel, label = "placeholder")
		self.charmDetailSizer.Add(self.charmNameLabel, 1, wx.EXPAND)

		self.charmSkillList = wx.ListCtrl(self.charmDetailPanel, style=wx.LC_REPORT
																| wx.LC_VRULES
																| wx.LC_HRULES
																)
		self.charmSkillList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onSkillDoubleClick)
		self.charmDetailSizer.Add(self.charmSkillList, 1, wx.EXPAND)
		self.charmSkillList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.materialList = wx.ListCtrl(self.charmDetailPanel, style=wx.LC_REPORT
																| wx.LC_VRULES
																| wx.LC_HRULES
																)
		self.materialList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onMaterialDoubleClick)
		self.charmDetailSizer.Add(self.materialList, 7, wx.EXPAND)
		self.materialList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)


	def loadCharmDetail(self):
		self.charmSkillList.ClearAll()
		self.materialList.ClearAll()

		self.charmNameLabel.SetLabelText(f"\n{self.currentCharmName}")

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = "Skills"
		self.charmSkillList.InsertColumn(0, info)
		self.charmSkillList.SetColumnWidth(0, self.charmDetailPanel.GetSize()[0] * 0.66)

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = ""
		self.charmSkillList.InsertColumn(1, info)
		self.charmSkillList.SetColumnWidth(1, self.charmDetailPanel.GetSize()[0] * 0.34 - 20)

		self.charmSkillList.InsertColumn(2, info)
		self.charmSkillList.SetColumnWidth(2, 0)

		sql = """
			SELECT s.id skill_id, stt.name skill_name, s.max_level skill_max_level,
				s.icon_color skill_icon_color, cs.level level
			FROM charm_skill cs
				JOIN skilltree s
					ON cs.skilltree_id = s.id
				JOIN skilltree_text stt
					ON stt.id = s.id
			WHERE stt.lang_id = :langId
			AND cs.charm_id = :charmId
		"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, ("en", self.currentCharmID))
		data = data.fetchall()

		skills = []
		for row in data:
			skills.append(c.CharmSkill(row))
		for skill in skills:
			lvl = skill.level * "◈"
			maxLvl = (skill.maxLevel - skill.level) * "◇"
			img = self.il.Add(wx.Bitmap(f"images/skills-24/Skill{skill.iconColor}.png"))
			index = self.charmSkillList.InsertItem(self.charmSkillList.GetItemCount(), skill.name, img)
			self.charmSkillList.SetItem(index, 1, f"{lvl}{maxLvl}")
			self.charmSkillList.SetItem(index, 2, f"{skill.id}")

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = "Req. Materials"
		self.materialList.InsertColumn(0, info)
		self.materialList.SetColumnWidth(0, self.charmDetailPanel.GetSize()[0] * 0.66)
		info = wx.ListItem()

		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = ""
		self.materialList.InsertColumn(1, info)
		self.materialList.SetColumnWidth(1, self.charmDetailPanel.GetSize()[0] * 0.34 - 20)

		self.materialList.InsertColumn(2, info)
		self.materialList.SetColumnWidth(2, 0)

		sql = """
			SELECT i.id item_id, it.name item_name, i.icon_name item_icon_name,
				i.category item_category, i.icon_color item_icon_color, cr.quantity
			FROM charm_recipe cr
				JOIN item i
					ON i.id = cr.item_id
				JOIN item_text it
					ON it.id = i.id
			WHERE it.lang_id = :langId
			AND cr.charm_id = :charmId
		"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, ("en", self.currentCharmID))
		data = data.fetchall()

		materials = []
		for row in data:
			materials.append(c.CharmMaterial(row))
		for mat in materials:
			img = self.il.Add(wx.Bitmap(f"images/materials-24/{mat.iconName}{mat.iconColor}.png"))
			index = self.materialList.InsertItem(self.materialList.GetItemCount(), mat.name, img)
			self.materialList.SetItem(index, 1, f"{mat.quantity}")
			self.materialList.SetItem(index, 2, f"{mat.id},{mat.category}")


	def onCharmSelected(self, event):
		self.currentCharmName = self.charmList.GetItemText(event.GetEventObject().GetFirstSelected(), 0)
		self.currentCharmID = self.charmList.GetItemText(event.GetEventObject().GetFirstSelected(), 1)
		if int(self.currentCharmID) > 0:	
			self.loadCharmDetail()


	def onSkillDoubleClick(self, event):
		materialInfo = event.GetEventObject().GetItemText(event.GetEventObject().GetFirstSelected(), 2)
		self.link.event = True
		self.link.eventType = "skill"
		self.link.info =  link.GenericSingleLink(materialInfo)
		self.root.followLink()
		self.link.reset()

	
	def onMaterialDoubleClick(self, event):
		materialInfo = self.materialList.GetItemText(event.GetEventObject().GetFirstSelected(), 2)
		materialInfo = materialInfo.split(",")
		self.link.event = True
		self.link.eventType = "item"
		self.link.info =  link.GenericDoubleLink(materialInfo)
		self.root.followLink()
		self.link.reset()


	def onSize(self, event):
		self.charmSkillList.SetColumnWidth(0, self.charmDetailPanel.GetSize()[0] * 0.66)
		self.charmSkillList.SetColumnWidth(1, self.charmDetailPanel.GetSize()[0] * 0.34 - 20)
		self.materialList.SetColumnWidth(0, self.charmDetailPanel.GetSize()[0] * 0.66)
		self.materialList.SetColumnWidth(1, self.charmDetailPanel.GetSize()[0] * 0.34 - 20)
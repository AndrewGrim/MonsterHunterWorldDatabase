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

class CharmsTab:

	def __init__(self, root, mainNotebook):
		self.root = root
		self.mainNotebook = mainNotebook
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

		self.charmDetailsNotebook = wx.Notebook(self.charmPanel)
		self.charmDetailPanel = wx.Panel(self.charmDetailsNotebook)

		self.charmDetailSizer = wx.BoxSizer(wx.VERTICAL)
		self.charmDetailsNotebook.AddPage(self.charmDetailPanel, "Detail")
		self.charmDetailPanel.SetSizer(self.charmDetailSizer)
		
		self.charmDetailedSizer.Add(self.charmImageLabel, 1, wx.ALIGN_CENTER)
		self.charmDetailedSizer.Add(self.charmDetailsNotebook, 3, wx.EXPAND)

		self.charmSizer.Add(self.charmListSizer, 1, wx.EXPAND)
		self.charmSizer.Add(self.charmDetailedSizer, 1, wx.EXPAND)

		self.charmPanel.SetSizer(self.charmSizer)

		self.initCharmList()
		self.loadCharmList()

		self.initCharmDetail()
		self.loadCharmDetail()


	def initCharmList(self):
		self.charmList = wx.ListCtrl(self.charmPanel, style=wx.LC_REPORT
														| wx.LC_VRULES
														| wx.LC_HRULES
														)
		self.charmListSizer.Add(self.charmList, 1, wx.EXPAND)
		self.charmList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSkillSelected)

		self.il = wx.ImageList(24, 24)
		self.test = self.il.Add(self.testIcon)
		self.charmList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)


	def loadCharmList(self):
		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = ""
		self.charmList.InsertColumn(0, info)
		self.charmList.SetColumnWidth(0, 680)
		self.charmList.InsertColumn(1, info)
		self.charmList.SetColumnWidth(1, 0)


		sql = """
			SELECT c.*, ct.name
			FROM charm c
				JOIN charm_text ct
					ON ct.id = c.id
					AND ct.lang_id = :langId
			ORDER BY ct.name
		"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, ("en", ))
		data = data.fetchall()

		charms = []
		for row in data:
			charms.append(c.Charm(row))

		for charm in charms:
			img = self.il.Add(wx.Bitmap(f"images/charms-24/{charm.rarity}.png"))
			index = self.charmList.InsertItem(self.charmList.GetItemCount(), charm.name, img)
			self.charmList.SetItem(index, 1, f"{charm.id}")


	def initCharmDetail(self):
		self.charmNameLabel = wx.StaticText(self.charmDetailPanel, label = "placeholder")
		self.charmDetailSizer.Add(self.charmNameLabel, 1, wx.EXPAND)

		self.charmSkillList = wx.ListCtrl(self.charmDetailPanel, style=wx.LC_REPORT
																| wx.LC_VRULES
																| wx.LC_HRULES
																)
		self.charmDetailSizer.Add(self.charmSkillList, 1, wx.EXPAND)
		self.charmSkillList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.materialList = wx.ListCtrl(self.charmDetailPanel, style=wx.LC_REPORT
																| wx.LC_VRULES
																| wx.LC_HRULES
																)
		self.charmDetailSizer.Add(self.materialList, 7, wx.EXPAND)
		self.materialList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)


	def loadCharmDetail(self):
		self.charmNameLabel.SetLabelText(f"\n{self.currentCharmName}")

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = "Skills"
		self.charmSkillList.InsertColumn(0, info)
		self.charmSkillList.SetColumnWidth(0, 580)
		info = wx.ListItem()

		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = ""
		self.charmSkillList.InsertColumn(1, info)
		self.charmSkillList.SetColumnWidth(1, 100)

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

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = "Req. Materials"
		self.materialList.InsertColumn(0, info)
		self.materialList.SetColumnWidth(0, 580)
		info = wx.ListItem()

		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = ""
		self.materialList.InsertColumn(1, info)
		self.materialList.SetColumnWidth(1, 100)

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


	def onSkillSelected(self, event):
		self.currentCharmName = self.charmList.GetItemText(event.GetEventObject().GetFirstSelected(), 0)
		self.currentCharmID = self.charmList.GetItemText(event.GetEventObject().GetFirstSelected(), 1)
		if int(self.currentCharmID) > 0:
			self.charmSkillList.ClearAll()
			self.materialList.ClearAll()
		self.loadCharmDetail()
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
import Skill as s
import SkillDetail as sd

class SkillsTab:

	def __init__(self, root, mainNotebook):
		self.root = root
		self.mainNotebook = mainNotebook
		self.currentSkillID = 1
		self.testIcon = wx.Bitmap("images/unknown.png", wx.BITMAP_TYPE_ANY)
		self.initSkillTab()


	def initSkillTab(self):
		self.skillPanel = wx.Panel(self.mainNotebook)
		self.mainNotebook.AddPage(self.skillPanel, "Skills")
		self.skillSizer = wx.BoxSizer(wx.HORIZONTAL)

		self.skillListSizer = wx.BoxSizer(wx.VERTICAL) 
		
		self.skillDetailedSizer = wx.BoxSizer(wx.VERTICAL)
		self.skillImage = wx.Bitmap("images/weapons/great-sword/Buster Sword I.png", wx.BITMAP_TYPE_ANY)
		self.skillImageLabel = wx.StaticBitmap(self.skillPanel, bitmap=self.skillImage, size=(160, 160))

		self.skillDetailsNotebook = wx.Notebook(self.skillPanel)
		self.skillDetailPanel = wx.Panel(self.skillDetailsNotebook)

		self.skillDetailSizer = wx.BoxSizer(wx.VERTICAL)
		self.skillDetailsNotebook.AddPage(self.skillDetailPanel, "Detail")
		self.skillDetailPanel.SetSizer(self.skillDetailSizer)
		
		self.skillDetailedSizer.Add(self.skillImageLabel, 1, wx.ALIGN_CENTER)
		self.skillDetailedSizer.Add(self.skillDetailsNotebook, 3, wx.EXPAND)

		self.skillSizer.Add(self.skillListSizer, 1, wx.EXPAND)
		self.skillSizer.Add(self.skillDetailedSizer, 1, wx.EXPAND)

		self.skillPanel.SetSizer(self.skillSizer)

		self.initSkillList()
		self.loadSkillList()

		self.initSkillDetail()
		self.loadSkillDetail()


	def initSkillList(self):
		self.skillList = wx.ListCtrl(self.skillPanel, style=wx.LC_REPORT
														| wx.LC_VRULES
														| wx.LC_HRULES
														)
		self.skillListSizer.Add(self.skillList, 1, wx.EXPAND)
		self.skillList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSkillSelected)

		isz = (24, 24)
		self.il = wx.ImageList(isz[0], isz[1])
		self.test = self.il.Add(self.testIcon)
		self.skillList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)


	def loadSkillList(self):
		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = ""
		self.skillList.InsertColumn(0, info)
		self.skillList.SetColumnWidth(0, 680)
		self.skillList.InsertColumn(1, info)
		self.skillList.SetColumnWidth(1, 0)


		sql = """
			SELECT id, name, max_level, description, icon_color
			FROM skilltree s join skilltree_text st USING (id)
			WHERE lang_id = :langId
			ORDER BY name 
		"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, ("en", ))
		data = data.fetchall()

		skills = []
		for row in data:
			skills.append(s.Skill(row))

		for skill in skills:
			index = self.skillList.InsertItem(self.skillList.GetItemCount(), skill.name, self.test)
			self.skillList.SetItem(index, 1, f"{skill.id}")


	def initSkillDetail(self):
		self.skillDescriptionLabel = wx.StaticText(self.skillDetailPanel, label = "placeholder")
		self.skillDetailSizer.Add(self.skillDescriptionLabel, 1, wx.EXPAND)

		self.skillDetailList = wx.ListCtrl(self.skillDetailPanel, style=wx.LC_REPORT
														| wx.LC_VRULES
														| wx.LC_HRULES
														)
		self.skillDetailSizer.Add(self.skillDetailList, 1, wx.EXPAND)
		self.skillDetailList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.foundList = wx.ListCtrl(self.skillDetailPanel, style=wx.LC_REPORT
														| wx.LC_VRULES
														| wx.LC_HRULES
														)
		self.skillDetailSizer.Add(self.foundList, 7, wx.EXPAND)
		self.foundList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)


	def loadSkillDetail(self):
		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = ""
		self.skillDetailList.InsertColumn(0, info)
		self.skillDetailList.SetColumnWidth(0, 100)
		info = wx.ListItem()

		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = ""
		self.skillDetailList.InsertColumn(1, info)
		self.skillDetailList.SetColumnWidth(1, 580)


		sql = """
			SELECT st.id, stt.name skilltree_name, stt.description skilltree_description,
				st.max_level, s.level, s.description, st.icon_color
			FROM skilltree st
				JOIN skilltree_text stt
					ON stt.id = st.id
					AND stt.lang_id = :langId
				JOIN skill s
					ON s.skilltree_id = st.id
					AND s.lang_id = :langId
			WHERE st.id = :skillTreeId
		"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, ("en", self.currentSkillID))
		data = data.fetchall()

		skills = []
		for row in data:
			skills.append(sd.SkillDetail(row))
	
		for skill in skills:
			lvl = skill.skillLevel * "◈"
			maxLvl = (skill.skillMaxLevel - skill.skillLevel) * "◇"
			index = self.skillDetailList.InsertItem(self.skillDetailList.GetItemCount(), f"{lvl}{maxLvl}", self.test)
			self.skillDetailList.SetItem(index, 1, skill.skillLevelDescription)
		if skills[0].skillMaxLevel == 1:
			self.skillDescriptionLabel.SetLabelText(f"\n{skills[0].skillLevelDescription}")
		else:
			self.skillDescriptionLabel.SetLabelText(f"\n{skills[0].description}")

		self.loadSkillDrop(skill)


	def loadSkillDrop(self, Skill):
		"""skill = Skill

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = "Drop"
		self.foundList.InsertColumn(0, info)
		self.foundList.SetColumnWidth(0, 580)
		info = wx.ListItem()

		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = ""
		self.foundList.InsertColumn(1, info)
		self.foundList.SetColumnWidth(1, 100)

		index = self.foundList.InsertItem(self.foundList.GetItemCount(), "Mysterious Feystone", self.test)
		self.foundList.SetItem(index, 1, f"{skill.mysteriousFeystonePercent}%")
		index = self.foundList.InsertItem(self.foundList.GetItemCount(), "Glowing Feystone", self.test)
		self.foundList.SetItem(index, 1, f"{skill.glowingFeystonePercent}%")
		index = self.foundList.InsertItem(self.foundList.GetItemCount(), "Worn Feystone", self.test)
		self.foundList.SetItem(index, 1, f"{skill.wornFeystonePercent}%")
		index = self.foundList.InsertItem(self.foundList.GetItemCount(), "Warped Feystone", self.test)
		self.foundList.SetItem(index, 1, f"{skill.warpedFeystonePercent}%")"""


	def onSkillSelected(self, event):
		self.currentSkillID = self.skillList.GetItemText(event.GetEventObject().GetFirstSelected(), 1)
		if int(self.currentSkillID) > 0:
			self.skillDetailList.ClearAll()
			#self.foundList.ClearAll()
		self.loadSkillDetail()
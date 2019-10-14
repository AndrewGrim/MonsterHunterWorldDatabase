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
import SkillDecoration as sdeco
import SkillCharm as sch
import SkillArmor as aarm

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
			self.skillDescriptionLabel.SetLabelText(f"\n{skills[0].name}:\n{skills[0].skillLevelDescription}")
		else:
			self.skillDescriptionLabel.SetLabelText(f"\n{skills[0].name}:\n{skills[0].description}")

		self.loadSkillFound()


	def loadSkillFound(self):
		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = "Found In"
		self.foundList.InsertColumn(0, info)
		self.foundList.SetColumnWidth(0, 580)
		info = wx.ListItem()

		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = ""
		self.foundList.InsertColumn(1, info)
		self.foundList.SetColumnWidth(1, 100)

		self.loadSkillDecorations()
		self.loadSkillCharms()
		self.loadSkillArmor()
		self.loadSkillArmorSetBonuses()

	def loadSkillDecorations(self):
		sql = """
			SELECT
				stt.id skill_id, stext.name skill_name, stt.max_level skill_max_level,
				d.id deco_id, dt.name deco_name, d.slot deco_slot, d.icon_color deco_icon_color,
				1 level
			FROM decoration d
				JOIN decoration_text dt USING (id)
				JOIN skilltree stt ON (stt.id = d.skilltree_id)
				JOIN skilltree_text stext
					ON stext.id = stt.id
					AND stext.lang_id = dt.lang_id
			WHERE d.skilltree_id = :skillTreeId
			AND dt.lang_id = :langId
			ORDER BY dt.name ASC
		"""
		# ICEBORNE the final select here "1 level" will not be compatible with iceborne as
		# the game introduces lvl 4 deco which can give 2 lvls of a skill or 1 lvl of 2 separate skill!

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, (self.currentSkillID, "en"))
		data = data.fetchall()

		decorations = []
		for row in data:
			decorations.append(sdeco.SkillDecoration(row))
	
		for deco in decorations:
			lvl = deco.skillLevel * "◈"
			maxLvl = (deco.skillMaxLevel - deco.skillLevel) * "◇"
			index = self.foundList.InsertItem(self.foundList.GetItemCount(), deco.decorationName, self.test)
			self.foundList.SetItem(index, 1, f"{lvl}{maxLvl}")

		
	def loadSkillCharms(self):
		sql = """
			SELECT c.id AS charm_id, c.rarity AS charm_rarity, ct.name AS charm_name,
				st.id skill_id, stext.name skill_name, st.max_level skill_max_level,
				cs.level level
			FROM charm c
				JOIN charm_text ct USING (id)
				JOIN charm_skill cs ON (c.id = charm_id)
				JOIN skilltree st ON (st.id = skilltree_id)
				JOIN skilltree_text stext
				ON stext.id = st.id
				AND stext.lang_id = ct.lang_id
			WHERE ct.lang_id = :langId
				AND cs.skilltree_id = :skillTreeId
		"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, ("en", self.currentSkillID))
		data = data.fetchall()

		charms = []
		for row in data:
			charms.append(sch.SkillCharm(row))
	
		for charm in charms:
			lvl = charm.skillLevel * "◈"
			maxLvl = (charm.skillMaxLevel - charm.skillLevel) * "◇"
			index = self.foundList.InsertItem(self.foundList.GetItemCount(), charm.name, self.test)
			self.foundList.SetItem(index, 1, f"{lvl}{maxLvl}")


	def loadSkillArmor(self):
		sql = """
			SELECT stt.id skill_id, stt.max_level skill_max_level,
				a.id armor_id, at.name armor_name, a.rarity armor_rarity, a.armor_type armor_armor_type,
				askill.level level
			FROM armor a
				JOIN armor_text at ON a.id = at.id
				JOIN armor_skill askill ON a.id = askill.armor_id
				JOIN skilltree stt ON askill.skilltree_id = stt.id
				JOIN skilltree_text stext
					ON stext.id = stt.id
					AND stext.lang_id = at.lang_id
			WHERE at.lang_id = :langId
			AND askill.skilltree_id = :skillTreeId
			ORDER BY a.id ASC
		"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, ("en", self.currentSkillID))
		data = data.fetchall()

		armor = []
		for row in data:
			armor.append(aarm.SkillArmor(row))
	
		for arm in armor:
			lvl = arm.skillLevel * "◈"
			maxLvl = (arm.skillMaxLevel - arm.skillLevel) * "◇"
			index = self.foundList.InsertItem(self.foundList.GetItemCount(), arm.armorName, self.test)
			self.foundList.SetItem(index, 1, f"{lvl}{maxLvl}")


	def loadSkillArmorSetBonuses(self):
		pass


	def onSkillSelected(self, event):
		self.currentSkillID = self.skillList.GetItemText(event.GetEventObject().GetFirstSelected(), 1)
		if int(self.currentSkillID) > 0:
			self.skillDetailList.ClearAll()
			self.foundList.ClearAll()
		self.loadSkillDetail()
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

import SkillsTab as s
import Utilities as util
import Links as link

class SkillsTab:

	def __init__(self, root, mainNotebook, link):
		self.root = root
		self.mainNotebook = mainNotebook
		self.link = link
		
		self.currentSkillID = 1
		self.testIcon = wx.Bitmap("images/unknown.png", wx.BITMAP_TYPE_ANY)
		self.initSkillTab()


	def initSkillTab(self):
		self.skillPanel = wx.Panel(self.mainNotebook)
		self.mainNotebook.AddPage(self.skillPanel, "Skills")
		self.skillSizer = wx.BoxSizer(wx.HORIZONTAL)

		self.skillListSizer = wx.BoxSizer(wx.VERTICAL) 
		
		self.skillDetailedSizer = wx.BoxSizer(wx.VERTICAL)
		self.skillImage = wx.Bitmap("images/skills-160/SkillViolet.png", wx.BITMAP_TYPE_ANY)
		self.skillImageLabel = wx.StaticBitmap(self.skillPanel, bitmap=self.skillImage, size=(160, 160))

		self.skillDetailsNotebook = wx.Notebook(self.skillPanel)
		self.skillDetailPanel = wx.Panel(self.skillDetailsNotebook)

		self.skillDetailSizer = wx.BoxSizer(wx.VERTICAL)
		self.skillDetailsNotebook.AddPage(self.skillDetailPanel, "Detail")
		self.skillDetailPanel.SetSizer(self.skillDetailSizer)
		
		self.skillDetailedSizer.Add(self.skillImageLabel, 1, wx.ALIGN_CENTER)
		self.skillDetailedSizer.Add(self.skillDetailsNotebook, 3, wx.EXPAND)

		self.skillSizer.Add(self.skillListSizer, 0, wx.EXPAND)
		self.skillSizer.Add(self.skillDetailedSizer, 1, wx.EXPAND)

		self.skillPanel.SetSizer(self.skillSizer)

		self.initSearch()
		self.initSkillList()
		self.initSkillDetail()
		self.loadSkillList()

		self.skillList.Bind(wx.EVT_SIZE, self.onSize)


	def initSearch(self):
		self.search = wx.TextCtrl(self.skillPanel, style=wx.TE_PROCESS_ENTER, size=(124, -1))
		self.search.SetHint("  search by name")
		self.search.Bind(wx.EVT_TEXT_ENTER, self.onSearchTextEnter)

		self.searchSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.searchSizer.Add(self.search)
		self.searchSizer.Add(592, 0, 0)

		self.skillListSizer.Add(self.searchSizer)

	def onSearchTextEnter(self, event):
		self.loadSkillList()


	def initSkillList(self):
		self.skillList = wx.ListCtrl(self.skillPanel, style=wx.LC_REPORT
														| wx.LC_VRULES
														| wx.LC_HRULES
														)
		self.skillListSizer.Add(self.skillList, 1, wx.EXPAND)
		self.skillList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSkillSelected)

		self.il = wx.ImageList(24, 24)
		self.test = self.il.Add(self.testIcon)
		self.skillList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)


	def loadSkillList(self):
		try:
			self.skillList.ClearAll()
		except:
			pass

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = ""
		self.skillList.InsertColumn(0, info)
		self.skillList.SetColumnWidth(0, 680)
		self.skillList.InsertColumn(1, info)
		self.skillList.SetColumnWidth(1, 0)

		searchText = self.search.GetValue().replace("'", "''")

		if len(searchText) == 0 or searchText == " ":
			sql = """
				SELECT id, name, max_level, description, icon_color
				FROM skilltree s join skilltree_text st USING (id)
				WHERE lang_id = :langId
				ORDER BY name 
			"""
		else:
			sql = f"""
				SELECT id, name, max_level, description, icon_color
				FROM skilltree s join skilltree_text st USING (id)
				WHERE lang_id = :langId
				AND name LIKE '%{searchText}%'
				ORDER BY name 
			"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, ("en", ))
		data = data.fetchall()

		skills = []
		for row in data:
			skills.append(s.Skill(row))

		if len(skills) != 0:
			self.il.RemoveAll()

		for skill in skills:
			if skill.iconColor != None:
				img = self.il.Add(wx.Bitmap(f"images/skills-24/Skill{skill.iconColor}.png"))
			else:
				img = self.il.Add(wx.Bitmap(f"images/unknown.png"))
			index = self.skillList.InsertItem(self.skillList.GetItemCount(), skill.name, img)
			self.skillList.SetItem(index, 1, f"{skill.id}")
		
		if self.skillList.GetItemCount() != 0:
			self.skillList.Select(0)


	def initSkillDetail(self):
		self.skillNameLabel = wx.StaticText(self.skillDetailPanel, label = "placeholder")
		self.skillNameLabel.SetFont(self.skillNameLabel.GetFont().Bold())
		self.skillDetailSizer.Add(self.skillNameLabel, 0.2, wx.EXPAND)
		self.skillDescriptionLabel = wx.StaticText(self.skillDetailPanel, label="Description", style=wx.ALIGN_LEFT)
		self.skillDetailSizer.Add(self.skillDescriptionLabel, 0.5, wx.EXPAND)

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
		self.foundList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onFoundInDoubleClick)
		self.skillDetailSizer.Add(self.foundList, 7, wx.EXPAND)
		self.foundList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)


	def loadSkillDetail(self):
		self.root.Freeze()

		try:
			self.skillDetailList.ClearAll()
		except:
			pass
			
		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = ""
		self.skillDetailList.InsertColumn(0, info)
		self.skillDetailList.SetColumnWidth(0, self.skillDetailPanel.GetSize()[0] * 0.20)
		info = wx.ListItem()

		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = ""
		self.skillDetailList.InsertColumn(1, info)
		self.skillDetailList.SetColumnWidth(1, self.skillDetailPanel.GetSize()[0] * 0.80 - 20)

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
			skills.append(s.SkillDetail(row))
	
		for skill in skills:
			if self.root.pref.unicodeSymbols:
				lvl = skill.skillLevel * "◈"
				maxLvl = (skill.skillMaxLevel - skill.skillLevel) * "◇"
			else:
				lvl = f"{skill.skillLevel}/"
				maxLvl = skill.skillMaxLevel
			img = self.il.Add(wx.Bitmap(f"images/skills-24/Skill{skill.iconColor}.png"))
			index = self.skillDetailList.InsertItem(self.skillDetailList.GetItemCount(), f"{lvl}{maxLvl}", img)
			self.skillDetailList.SetItem(index, 1, skill.skillLevelDescription)
		self.skillImageLabel.SetBitmap(wx.Bitmap(f"images/skills-160/Skill{skill.iconColor}.png"))
		if skills[0].skillMaxLevel == 1:
			self.skillNameLabel.SetLabelText(f"\n{skills[0].name}:")
			self.skillDescriptionLabel.SetLabelText(f"{skills[0].skillLevelDescription}\n")
		else:
			self.skillNameLabel.SetLabelText(f"\n{skills[0].name}:")
			self.skillDescriptionLabel.SetLabelText(f"{skills[0].description}\n")

		self.loadSkillFound()


	def loadSkillFound(self):
		try:
			self.foundList.ClearAll()
		except:
			pass
		
		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = "Found In"
		self.foundList.InsertColumn(0, info)
		self.foundList.SetColumnWidth(0, self.skillDetailPanel.GetSize()[0] * 0.66)
		info = wx.ListItem()

		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_CENTER
		info.Text = ""
		self.foundList.InsertColumn(1, info)
		self.foundList.SetColumnWidth(1, self.skillDetailPanel.GetSize()[0] * 0.34 - 20)

		self.foundList.InsertColumn(2, info)
		self.foundList.SetColumnWidth(2, 0)

		self.loadSkillDecorations()
		self.loadSkillCharms()
		self.loadSkillArmor()
		self.loadSkillArmorSetBonuses()

		self.root.Thaw()
		

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
			decorations.append(s.SkillDecoration(row))
	
		for deco in decorations:
			if self.root.pref.unicodeSymbols:
				lvl = deco.skillLevel * "◈"
				maxLvl = (deco.skillMaxLevel - deco.skillLevel) * "◇"
			else:
				lvl = f"{deco.skillLevel}/"
				maxLvl = deco.skillMaxLevel
			img = self.il.Add(wx.Bitmap(f"images/items-24/Feystone{deco.decorationIconColor}.png"))
			index = self.foundList.InsertItem(self.foundList.GetItemCount(), deco.decorationName, img)
			self.foundList.SetItem(index, 1, f"{lvl}{maxLvl}")
			self.foundList.SetItem(index, 2, f"decoration,{deco.decorationID}")

		
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
			charms.append(s.SkillCharm(row))
	
		for charm in charms:
			if self.root.pref.unicodeSymbols:
				lvl = charm.skillLevel * "◈"
				maxLvl = (charm.skillMaxLevel - charm.skillLevel) * "◇"
			else:
				lvl = f"{charm.skillLevel}/"
				maxLvl = charm.skillMaxLevel
			img = self.il.Add(wx.Bitmap(f"images/charms-24/{charm.rarity}.png"))
			index = self.foundList.InsertItem(self.foundList.GetItemCount(), charm.name, img)
			self.foundList.SetItem(index, 1, f"{lvl}{maxLvl}")
			self.foundList.SetItem(index, 2, f"charm,{charm.id}")


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
			armor.append(s.SkillArmor(row))
	
		for arm in armor:
			if self.root.pref.unicodeSymbols:
				lvl = arm.skillLevel * "◈"
				maxLvl = (arm.skillMaxLevel - arm.skillLevel) * "◇"
			else:
				lvl = f"{arm.skillLevel}/"
				maxLvl = arm.skillMaxLevel
			img = self.il.Add(wx.Bitmap(f"images/armor/{arm.armorType}/rarity-24/{arm.armorRarity}.png"))
			index = self.foundList.InsertItem(self.foundList.GetItemCount(), arm.armorName, img)
			self.foundList.SetItem(index, 1, f"{lvl}{maxLvl}")
			self.foundList.SetItem(index, 2, f"armor,{arm.armorID}")


	def loadSkillArmorSetBonuses(self):
		sql = """
			SELECT stt.id skilltree_id, stext.name skill_name, stt.max_level skilltree_max_level,
				abs.setbonus_id as id, abt.name, abs.required
			FROM armorset_bonus_skill abs
				JOIN armorset_bonus_text abt ON (abt.id = abs.setbonus_id)
				JOIN skilltree stt ON (stt.id = abs.skilltree_id)
				JOIN skilltree_text stext
					ON stext.id = stt.id
					AND stext.lang_id = abt.lang_id
			WHERE abs.skilltree_id = :skillTreeId
			AND abt.lang_id = :langId
			ORDER BY abt.name ASC
		"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, (self.currentSkillID, "en"))
		data = data.fetchall()

		setBonuses = []
		for row in data:
			setBonuses.append(s.SkillArmorSetBonus(row))
	
		for bonus in setBonuses:
			img = self.il.Add(wx.Bitmap(f"images/skills-24/{util.setBonusColors[bonus.setBonusName]}"))
			index = self.foundList.InsertItem(self.foundList.GetItemCount(), f"{bonus.name} / {bonus.setBonusName}", img)
			self.foundList.SetItem(index, 1, f"Req. {bonus.setBonusRequired}")
			self.foundList.SetItem(index, 2, f"skill,{bonus.id}")


	def onSkillSelected(self, event):
		self.currentSkillID = self.skillList.GetItemText(event.GetEventObject().GetFirstSelected(), 1)
		if int(self.currentSkillID) > 0:
			self.loadSkillDetail()


	def onFoundInDoubleClick(self, event):
		materialInfo = event.GetEventObject().GetItemText(event.GetEventObject().GetFirstSelected(), 2).split(",")
		self.link.event = True
		self.link.eventType = materialInfo[0]
		self.link.info = link.GenericSingleLink(materialInfo[1])
		self.root.followLink()
		self.link.reset()


	def onSize(self, event):
		self.skillDetailList.SetColumnWidth(0, self.skillDetailPanel.GetSize()[0] * 0.20)
		self.skillDetailList.SetColumnWidth(1, self.skillDetailPanel.GetSize()[0] * 0.80 - 20)
		self.foundList.SetColumnWidth(0, self.skillDetailPanel.GetSize()[0] * 0.66)
		self.foundList.SetColumnWidth(1, self.skillDetailPanel.GetSize()[0] * 0.34 - 20)
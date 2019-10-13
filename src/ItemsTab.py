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
import Item as i
import CharmUsage as c
import ArmorUsage as a
import WeaponUsage as w
import CombinationObtaining as combo
import LocationObtaining as l
import RewardObtaining as r

class ItemsTab:

	def __init__(self, root, mainNotebook):
		self.root = root
		self.mainNotebook = mainNotebook

		self.currentlySelectedItemID = 1
		self.currentItemName = "Potion"
		self.currentItemCategory = "item"
		self.currentUsageRow = 0
		self.currentObtainingRow = 0
		self.testIcon = wx.Bitmap("images/unknown.png", wx.BITMAP_TYPE_ANY)
		self.testIcon36 = wx.Bitmap("images/unknown36.png", wx.BITMAP_TYPE_ANY)
		self.testIcon48 = wx.Bitmap("images/unknown48.png", wx.BITMAP_TYPE_ANY)

		self.initItemTab()


	def initItemTab(self):
		self.itemPanel = wx.Panel(self.mainNotebook)
		self.mainNotebook.AddPage(self.itemPanel, "Items")
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
		
		self.initItemButtons()

		self.initItemList()
		self.loadItemList()

		self.initItemDetail()
		self.loadItemDetail()

		self.initItemUsage()
		self.loadItemUsage()

		self.initItemObtaining()
		self.loadItemObtaining()

		self.root.SetSize(self.root.windowWidth, self.root.windowHeight)


	def initItemButtons(self):
		self.itemsButton = wx.Button(self.itemPanel, label="Items", name="item")
		self.itemsButton.SetBitmap(wx.Bitmap("images/unknown.png"))
		self.materialsButton = wx.Button(self.itemPanel, label="Materials", name="material")
		self.materialsButton.SetBitmap(wx.Bitmap("images/unknown.png"))
		self.ammoButton = wx.Button(self.itemPanel, label="Ammo", name="ammo")
		self.ammoButton.SetBitmap(wx.Bitmap("images/unknown.png"))
		self.miscButton = wx.Button(self.itemPanel, label="Misc.", name="misc")
		self.miscButton.SetBitmap(wx.Bitmap("images/unknown.png"))
		self.craftingButton = wx.Button(self.itemPanel, label="Crafting", name="crafting")
		self.craftingButton.SetBitmap(wx.Bitmap("images/unknown.png"))

		self.itemsButton.Bind(wx.EVT_BUTTON, self.onItemTypeSelection)
		self.materialsButton.Bind(wx.EVT_BUTTON, self.onItemTypeSelection)
		self.ammoButton.Bind(wx.EVT_BUTTON, self.onItemTypeSelection)
		self.miscButton.Bind(wx.EVT_BUTTON, self.onItemTypeSelection)
		self.craftingButton.Bind(wx.EVT_BUTTON, self.onItemTypeSelection)
	
		self.itemButtonsSizer = wx.BoxSizer(wx.HORIZONTAL)

		self.itemButtonsSizer.Add(self.itemsButton)
		self.itemButtonsSizer.Add(self.materialsButton)
		self.itemButtonsSizer.Add(self.ammoButton)
		self.itemButtonsSizer.Add(self.miscButton)
		self.itemButtonsSizer.Add(self.craftingButton)

		self.itemListSizer.Add(self.itemButtonsSizer)


	def initItemList(self):
		self.itemList = cgr.HeaderBitmapGrid(self.itemPanel)
		self.itemList.Bind(wx.EVT_SIZE, self.onSize)
		self.itemList.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.onItemSelection)
		self.itemListSizer.Add(self.itemList, 1, wx.EXPAND)

		self.itemList.CreateGrid(1, 4)
		self.itemList.SetDefaultRowSize(48, resizeExistingRows=True)
		self.itemList.SetColSize(0, 48)
		self.itemList.SetColSize(1, 628)
		self.itemList.SetColSize(2, 0)
		self.itemList.SetColSize(3, 0)
		self.itemList.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
		self.itemList.SetDefaultCellFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False))
		self.itemList.SetColLabelSize(2)
		self.itemList.SetRowLabelSize(1)



	def loadItemList(self):
		self.itemList.DeleteRows(0, self.itemList.GetNumberRows())
		
		sql = """
			SELECT i.*, it.name, it.description
			FROM item i
				JOIN item_text it
					ON it.id = i.id
					AND it.lang_id = :langId
			WHERE (:category IS NULL AND i.category != 'hidden') OR i.category = :category
			ORDER BY i.id
		"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, ("en", self.currentItemCategory))
		data = data.fetchall()

		items = []
		for row in data:
			items.append(i.Item(row))
		self.itemList.AppendRows(len(items))

		for row, item in enumerate(items):
			self.itemList.SetCellRenderer(row, 0,cgr.ImageCellRenderer(self.testIcon48))
			self.itemList.SetCellValue(row, 1, item.name)
			self.itemList.SetCellValue(row, 2, f"{item.iconName}{item.iconColor}.png")
			self.itemList.SetCellValue(row, 3, str(item.id))


	def loadCraftingList(self):
		self.itemList.DeleteRows(0, self.itemList.GetNumberRows())

		sql = """
			SELECT c.id,
			r.id result_id, rt.name result_name, r.icon_name result_icon_name, r.icon_color result_icon_color, r.category result_category,
			f.id first_id, ft.name first_name, f.icon_name first_icon_name, f.icon_color first_icon_color, f.category first_category,
			s.id second_id, st.name second_name, s.icon_name second_icon_name, s.icon_color second_icon_color, s.category second_category,
			c.quantity quantity
			FROM item_combination c
				JOIN item r
					ON r.id = c.result_id
				JOIN item_text rt
					ON rt.id = r.id
					AND rt.lang_id = :langId
				JOIN item f
					ON f.id = c.first_id
				JOIN item_text ft
					ON ft.id = f.id
					AND ft.lang_id = :langId
				LEFT JOIN item s
					ON s.id = c.second_id
				LEFT JOIN item_text st
					ON st.id = s.id
					AND st.lang_id = :langId
			WHERE :itemId IS NULL
				OR c.result_id = :itemId
				OR c.first_id = :itemId
				OR c.second_id = :itemId
			ORDER BY c.id ASC
		"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, ("en", None))
		data = data.fetchall()

		combinations = []
		for row in data:
			combinations.append(combo.CombinationObtaining(row))
		self.itemList.AppendRows(len(combinations))

		for row, com in enumerate(combinations):
			self.itemList.SetCellRenderer(row, 0,cgr.ImageCellRenderer(self.testIcon36))
			if com.secondName != None:
				self.itemList.SetCellValue(row, 1, f"{com.resultName} = {com.firstName} + {com.secondName}")
			else:
				self.itemList.SetCellValue(row, 1, f"{com.resultName} = {com.firstName}")
			self.itemList.SetCellValue(row, 2, f"{com.resultIconName}{com.resultIconColor}.png")
			self.itemList.SetCellValue(row, 3, str(com.resultID))


	def initItemDetail(self):
		self.itemNameLabel = wx.StaticText(self.itemDetailPanel, label="Name", style=wx.ALIGN_LEFT)
		self.itemNameLabel.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False))
		self.itemDetailSizer.Add(self.itemNameLabel, 1, wx.EXPAND)
		self.itemDescriptionLabel = wx.StaticText(self.itemDetailPanel, label="Description", style=wx.ALIGN_LEFT)
		self.itemDescriptionLabel.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False))
		self.itemDetailSizer.Add(self.itemDescriptionLabel, 2, wx.EXPAND)

		self.itemDetailList = cgr.HeaderBitmapGrid(self.itemDetailPanel)
		self.itemDetailSizer.Add(self.itemDetailList, 3, wx.EXPAND)

		self.itemDetailList.CreateGrid(2, 6)
		self.itemDetailList.SetDefaultRowSize(36, resizeExistingRows=True)
		self.itemDetailList.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
		self.itemDetailList.SetDefaultCellFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False))
		self.itemDetailList.SetColLabelSize(2)
		self.itemDetailList.SetRowLabelSize(1)


	def loadItemDetail(self):
		sql = """
			SELECT i.*, it.name, it.description
			FROM item i
			JOIN item_text it
				ON it.id = i.id
				AND it.lang_id = :langId
			WHERE i.id = :itemId
		"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, ("en", self.currentlySelectedItemID))
		data = data.fetchone()

		item = i.Item(data)
		
		self.itemNameLabel.SetLabelText(item.name)
		self.itemDescriptionLabel.SetLabelText(item.description)
		self.itemDescriptionLabel.Wrap(650)
		self.itemDetailList.SetCellValue(0, 0, f"Rarity {item.rarity}")
		self.itemDetailList.SetCellValue(0, 1, "")
		self.itemDetailList.SetCellValue(0, 2, "")
		self.itemDetailList.SetCellValue(0, 3, "Buy")
		self.itemDetailList.SetCellValue(0, 4, str(item.buyPrice))
		self.itemDetailList.SetCellRenderer(0, 5,cgr.ImageTextCellRenderer(self.testIcon36, imageOffset=0))
		self.itemDetailList.SetCellValue(1, 0, "Carry")
		self.itemDetailList.SetCellValue(1, 1, str(item.carryLimit))
		self.itemDetailList.SetCellRenderer(1, 2,cgr.ImageTextCellRenderer(self.testIcon36, imageOffset=0))
		self.itemDetailList.SetCellValue(1, 3, "Sell")
		self.itemDetailList.SetCellValue(1, 4, str(item.sellPrice))
		self.itemDetailList.SetCellRenderer(1, 5,cgr.ImageTextCellRenderer(self.testIcon36, imageOffset=0))

	def initItemUsage(self):
		self.itemUsageLabel = wx.StaticText(self.itemDetailPanel, label="Usage", style=wx.ALIGN_LEFT)
		self.itemUsageLabel.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False))
		self.itemDetailSizer.Add(self.itemUsageLabel, 1, wx.EXPAND)

		self.itemUsageList = cgr.HeaderBitmapGrid(self.itemDetailPanel)
		self.itemDetailSizer.Add(self.itemUsageList, 8, wx.EXPAND)

		self.itemUsageList.CreateGrid(1, 3)
		self.itemUsageList.SetDefaultRowSize(36, resizeExistingRows=True)
		self.itemUsageList.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
		self.itemUsageList.SetDefaultCellFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False))
		self.itemUsageList.SetColLabelSize(2)
		self.itemUsageList.SetRowLabelSize(1)


	def loadItemUsage(self):
		try:
			self.itemUsageList.DeleteRows(0, self.itemList.GetNumberRows())
		except:
			pass

		self.currentUsageRow = 0

		self.loadUsageCharms()
		self.loadUsageArmor()
		self.loadUsageWeapons()

		
	def loadUsageCharms(self):
		sql = """
			SELECT c.id, c.rarity, ctext.name, cr.quantity
			FROM charm_recipe cr
				JOIN charm c
					ON c.id = cr.charm_id
				JOIN charm_text ctext
					ON ctext.id = c.id
			WHERE cr.item_id = :itemId
			AND ctext.lang_id = :langId
		"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, (self.currentlySelectedItemID, "en"))
		data = data.fetchall()

		charms = []
		for row in data:
			charms.append(c.CharmUsage(row))
		self.itemUsageList.AppendRows(len(charms))

		for charm in charms:
			self.itemUsageList.SetCellRenderer(self.currentUsageRow, 0,cgr.ImageCellRenderer(self.testIcon36))
			self.itemUsageList.SetCellValue(self.currentUsageRow, 1, charm.name)
			self.itemUsageList.SetCellValue(self.currentUsageRow, 2, str(charm.quantity))
			self.currentUsageRow += 1


	def loadUsageArmor(self):
		sql = """
			SELECT armor_id id, name, armor_type, rarity, ar.quantity
			FROM armor_recipe ar
				JOIN armor a
					ON ar.armor_id = a.id
				JOIN armor_text atext
					ON a.id = atext.id
			WHERE ar.item_id = :itemId
				AND atext.lang_id = :langId
		"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, (self.currentlySelectedItemID, "en"))
		data = data.fetchall()

		armor = []
		for row in data:
			armor.append(a.ArmorUsage(row))
		self.itemUsageList.AppendRows(len(armor))

		for arm in armor:
			self.itemUsageList.SetCellRenderer(self.currentUsageRow, 0,cgr.ImageCellRenderer(self.testIcon36))
			self.itemUsageList.SetCellValue(self.currentUsageRow, 1, arm.name)
			self.itemUsageList.SetCellValue(self.currentUsageRow, 2, str(arm.quantity))
			self.currentUsageRow += 1


	def loadUsageWeapons(self):
		sql = """
			SELECT w.id, w.rarity, w.weapon_type, wt.id, wt.name, wr.quantity
			FROM weapon w
				JOIN weapon_text wt USING (id)
				JOIN weapon_recipe wr ON w.id = wr.weapon_id
			WHERE wt.lang_id = :langId
				AND wr.item_id = :itemId
		"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, ("en", self.currentlySelectedItemID))
		data = data.fetchall()

		weapons = []
		for row in data:
			weapons.append(w.WeaponUsage(row))
		self.itemUsageList.AppendRows(len(weapons))

		for weapon in weapons:
			self.itemUsageList.SetCellRenderer(self.currentUsageRow, 0,cgr.ImageCellRenderer(self.testIcon36))
			self.itemUsageList.SetCellValue(self.currentUsageRow, 1, weapon.name)
			self.itemUsageList.SetCellValue(self.currentUsageRow, 2, str(weapon.quantity))
			self.currentUsageRow += 1


	def initItemObtaining(self):
		self.itemObtainingLabel = wx.StaticText(self.itemDetailPanel, label="Obtaining", style=wx.ALIGN_LEFT)
		self.itemObtainingLabel.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False))
		self.itemDetailSizer.Add(self.itemObtainingLabel, 1, wx.EXPAND)

		self.itemObtainingList = cgr.HeaderBitmapGrid(self.itemDetailPanel)
		self.itemDetailSizer.Add(self.itemObtainingList, 8, wx.EXPAND)

		self.itemObtainingList.CreateGrid(1, 3)
		self.itemObtainingList.SetDefaultRowSize(36, resizeExistingRows=True)
		self.itemObtainingList.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
		self.itemObtainingList.SetDefaultCellFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False))
		self.itemObtainingList.SetColLabelSize(2)
		self.itemObtainingList.SetRowLabelSize(1)


	def loadItemObtaining(self):
		try:
			self.itemObtainingList.DeleteRows(0, self.itemList.GetNumberRows())
		except:
			pass

		self.currentObtainingRow = 0

		self.loadObtainingCombination()
		self.loadObtainingLocations()
		self.loadObtainingRewards()


	def loadObtainingCombination(self):
		# TODO add this to UsageList as well!
		sql = """
			SELECT c.id,
			r.id result_id, rt.name result_name, r.icon_name result_icon_name, r.icon_color result_icon_color, r.category result_category,
			f.id first_id, ft.name first_name, f.icon_name first_icon_name, f.icon_color first_icon_color, f.category first_category,
			s.id second_id, st.name second_name, s.icon_name second_icon_name, s.icon_color second_icon_color, s.category second_category,
			c.quantity quantity
			FROM item_combination c
				JOIN item r
					ON r.id = c.result_id
				JOIN item_text rt
					ON rt.id = r.id
					AND rt.lang_id = :langId
				JOIN item f
					ON f.id = c.first_id
				JOIN item_text ft
					ON ft.id = f.id
					AND ft.lang_id = :langId
				LEFT JOIN item s
					ON s.id = c.second_id
				LEFT JOIN item_text st
					ON st.id = s.id
					AND st.lang_id = :langId
			WHERE :itemId IS NULL
				OR c.result_id = :itemId
				OR c.first_id = :itemId
				OR c.second_id = :itemId
			ORDER BY c.id ASC
		"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, ("en", self.currentlySelectedItemID))
		data = data.fetchall()

		combinations = []
		for row in data:
			if row[2] == self.currentItemName:
				combinations.append(combo.CombinationObtaining(row))
		self.itemObtainingList.AppendRows(len(combinations))

		for com in combinations:
			self.itemObtainingList.SetCellRenderer(self.currentObtainingRow, 0,cgr.ImageCellRenderer(self.testIcon36))
			if com.secondName != None:
				self.itemObtainingList.SetCellValue(self.currentObtainingRow, 1, f"{com.resultName} = {com.firstName} + {com.secondName}")
			else:
				self.itemObtainingList.SetCellValue(self.currentObtainingRow, 1, f"{com.resultName} = {com.firstName}")
			self.itemObtainingList.SetCellValue(self.currentObtainingRow, 2, f"x{com.quantity}")
			self.currentObtainingRow += 1


	def loadObtainingLocations(self):
		sql = """
			SELECT li.location_id, lt.name location_name,
				li.rank, li.area, li.stack, li.percentage, li.nodes
			FROM location_item li
				JOIN location_text lt
					ON lt.id = li.location_id
			WHERE li.item_id = :itemId
				AND lt.lang_id = :langId
		"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, (self.currentlySelectedItemID, "en"))
		data = data.fetchall()

		locations = []
		for row in data:
			locations.append(l.LocationObtaining(row))
		self.itemObtainingList.AppendRows(len(locations))

		for local in locations:
			self.itemObtainingList.SetCellRenderer(self.currentObtainingRow, 0,cgr.ImageCellRenderer(self.testIcon36))
			self.itemObtainingList.SetCellValue(self.currentObtainingRow, 1, f"{local.name} - Area {local.area}")
			self.itemObtainingList.SetCellValue(self.currentObtainingRow, 2, f"{local.stack} x {local.percentage}%")
			self.currentObtainingRow += 1


	def loadObtainingRewards(self):
		sql = """
			SELECT r.monster_id, mtext.name monster_name, m.size monster_size,
				rtext.name condition_name, r.rank, r.stack, r.percentage
			FROM monster_reward r
				JOIN monster_reward_condition_text rtext
					ON rtext.id = r.condition_id
				JOIN monster m
					ON m.id = r.monster_id
				JOIN monster_text mtext
					ON mtext.id = m.id
					AND mtext.lang_id = rtext.lang_id
			WHERE r.item_id = :itemId
			AND rtext.lang_id = :langId
			ORDER BY m.id ASC, r.percentage DESC
		"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, (self.currentlySelectedItemID, "en"))
		data = data.fetchall()

		rewards = []
		for row in data:
			rewards.append(r.RewardObtaining(row))
		self.itemObtainingList.AppendRows(len(rewards))

		for reward in rewards:
			self.itemObtainingList.SetCellRenderer(self.currentObtainingRow, 0,cgr.ImageCellRenderer(self.testIcon36))
			self.itemObtainingList.SetCellValue(self.currentObtainingRow, 1, f"{reward.monsterName} - {reward.rank} {reward.rewardName}")
			self.itemObtainingList.SetCellValue(self.currentObtainingRow, 2, f"{reward.stack} x {reward.percentage}%")
			self.currentObtainingRow += 1


	def onItemTypeSelection(self, event):
		"""
		When an item type button at the top of the screen is pressed the item list is reloaded with the new item type information.
		"""

		if event.GetEventObject().GetName() != "crafting":
			self.currentItemCategory = event.GetEventObject().GetName()
			self.loadItemList()
		else:
			self.currentItemCategory = event.GetEventObject().GetName()
			self.loadCraftingList()


	def onItemSelection(self, event):
		"""
		When a specific item is selected in the list, the detail view gets populated with the information from the database.
		"""
		if self.itemList.GetCellValue(event.GetRow(), 3) != "":
			self.currentlySelectedItemID = self.itemList.GetCellValue(event.GetRow(), 3)
			if self.currentItemCategory == "crafting":
				name = self.itemList.GetCellValue(event.GetRow(), 1)
				self.currentItemName = name[:name.find(" =")]
			else:
				self.currentItemName = self.itemList.GetCellValue(event.GetRow(), 1)
			"""iconFile = self.itemList.GetCellValue(event.GetRow(), 2)
			self.itemImage = wx.Bitmap(f"images/items/{category}/{iconFile}", wx.BITMAP_TYPE_ANY)
			self.itemImageLabel.SetBitmap(self.itemImage)"""
			self.loadItemDetail()
			self.loadItemUsage()
			self.loadItemObtaining()


	def onSize(self, event):
		"""
		When the application window is resized some columns's width gets readjusted.
		"""
		try:
			self.itemList.SetColSize(1, self.itemPanel.GetSize()[0] * 0.50 - 70)
		except:
			self.itemList.SetColSize(1, 623)
		try:
			colWidth = self.itemDetailPanel.GetSize()[0] / 6 + 40
			self.itemDetailList.SetColSize(0, colWidth)
			self.itemDetailList.SetColSize(1, colWidth)
			self.itemDetailList.SetColSize(2, 36)
			self.itemDetailList.SetColSize(3, colWidth)
			self.itemDetailList.SetColSize(4, colWidth)
			self.itemDetailList.SetColSize(5, 36)
			try:
				self.itemUsageList.SetColSize(0, 36)
				self.itemUsageList.SetColSize(1, self.itemDetailPanel.GetSize()[0] - 36 - 90 - 20)
				self.itemUsageList.SetColSize(2, 90)
				try:
					self.itemObtainingList.SetColSize(0, 36)
					self.itemObtainingList.SetColSize(1, self.itemDetailPanel.GetSize()[0] - 36 - 90 - 20)
					self.itemObtainingList.SetColSize(2, 90)
				except:
					pass
			except:
				pass
		except:
			pass
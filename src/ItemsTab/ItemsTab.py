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

import ItemsTab as i
import CharmsTab as c
import ArmorTab as a
import WeaponsTab as w
import LocationsTab as l
import Links as link
from Debug.debug import debug

class ItemsTab:

	def __init__(self, root, mainNotebook, link):
		self.root = root
		self.mainNotebook = mainNotebook
		self.link = link

		self.currentlySelectedItemID = 1
		self.currentItemName = "Potion"
		self.currentItemCategory = "item"
		self.currentUsageRow = 0
		self.currentObtainingRow = 0
		self.testIcon = wx.Bitmap("images/unknown.png", wx.BITMAP_TYPE_ANY)

		self.initItemTab()


	def initItemTab(self):
		self.itemPanel = wx.Panel(self.mainNotebook)
		self.mainNotebook.AddPage(self.itemPanel, "Items")
		self.itemsSizer = wx.BoxSizer(wx.HORIZONTAL)

		self.itemListSizer = wx.BoxSizer(wx.VERTICAL) 
		
		self.itemDetailedSizer = wx.BoxSizer(wx.VERTICAL)
		self.itemImage = wx.Bitmap("images/items-160/LiquidGreen.png", wx.BITMAP_TYPE_ANY)
		self.itemImageLabel = wx.StaticBitmap(self.itemPanel, bitmap=self.itemImage, size=(160, 160))

		self.itemDetailsNotebook = wx.Notebook(self.itemPanel)
		self.itemDetailPanel = wx.ScrolledWindow(self.itemDetailsNotebook)

		self.itemDetailSizer = wx.BoxSizer(wx.VERTICAL)
		self.itemDetailsNotebook.AddPage(self.itemDetailPanel, "Detail")
		self.itemDetailPanel.SetSizer(self.itemDetailSizer)
		
		self.itemDetailedSizer.Add(self.itemImageLabel, 1, wx.ALIGN_CENTER)
		self.itemDetailedSizer.Add(self.itemDetailsNotebook, 5, wx.EXPAND)

		self.itemsSizer.Add(self.itemListSizer, 0, wx.EXPAND)
		self.itemsSizer.Add(self.itemDetailedSizer, 1, wx.EXPAND)

		self.itemPanel.SetSizer(self.itemsSizer)
		
		self.initItemButtons()
		self.initSearch()
		self.initItemList()
		self.initItemDetail()
		self.initItemUsage()
		self.initItemObtaining()
		self.loadItemList()
		self.loadItemDetailAll()

		self.itemList.Bind(wx.EVT_SIZE, self.onSize)

		self.itemDetailPanel.SetScrollRate(20, 20)

	
	def loadItemDetailAll(self):
		self.root.Freeze()
		self.loadItemDetail()
		self.root.Thaw()


	def initItemButtons(self):
		self.itemsButton = wx.Button(self.itemPanel, label="Items", name="item")
		self.itemsButton.SetBitmap(wx.Bitmap("images/items-24/LiquidGreen.png"))
		self.materialsButton = wx.Button(self.itemPanel, label="Materials", name="material")
		self.materialsButton.SetBitmap(wx.Bitmap("images/items-24/BoneYellow.png"))
		self.ammoButton = wx.Button(self.itemPanel, label="Ammo", name="ammo")
		self.ammoButton.SetBitmap(wx.Bitmap("images/items-24/AmmoWhite.png"))
		self.miscButton = wx.Button(self.itemPanel, label="Misc.", name="misc")
		self.miscButton.SetBitmap(wx.Bitmap("images/items-24/SmokeRed.png"))
		self.craftingButton = wx.Button(self.itemPanel, label="Crafting", name="crafting")
		self.craftingButton.SetBitmap(wx.Bitmap("images/items-24/CraftingLightBeige.png"))

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

		self.itemListSizer.Add(self.itemButtonsSizer, 0, wx.EXPAND)


	def initSearch(self):
		self.search = wx.TextCtrl(self.itemPanel, style=wx.TE_PROCESS_ENTER)
		self.search.SetHint("search by name")
		self.search.Bind(wx.EVT_TEXT_ENTER, self.onSearchTextEnter)
		self.itemButtonsSizer.Add(self.search, 1, wx.EXPAND)


	def onSearchTextEnter(self, event):
		if self.currentItemCategory == "crafting":
			self.loadCraftingList()
		else:
			self.loadItemList()


	def initItemList(self):
		self.itemList = wx.ListCtrl(self.itemPanel, style=wx.LC_REPORT
													| wx.LC_VRULES
													| wx.LC_HRULES
													)
		self.itemList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelection)
		self.itemListSizer.Add(self.itemList, 1, wx.EXPAND)

		isz = (24, 24)
		self.il = wx.ImageList(isz[0], isz[1])
		
		self.itemList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)


	def loadItemList(self):
		try:
			self.itemList.ClearAll()
		except:
			pass
		self.test = self.il.Add(self.testIcon)
		
		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_CENTER
		info.Text = ""
		self.itemList.InsertColumn(0, info)
		self.itemList.SetColumnWidth(0, 680)
		self.itemList.InsertColumn(1, info)
		self.itemList.SetColumnWidth(1, 0)
		
		searchText = self.search.GetValue().replace("'", "''")

		if len(searchText) == 0 or searchText == " ":
			sql = """
				SELECT i.*, it.name, it.description
				FROM item i
					JOIN item_text it
						ON it.id = i.id
						AND it.lang_id = :langId
				WHERE (:category IS NULL AND i.category != 'hidden') OR i.category = :category
				ORDER BY i.id
			"""
		else:
			sql = f"""
				SELECT i.*, it.name, it.description
				FROM item i
					JOIN item_text it
						ON it.id = i.id
						AND it.lang_id = :langId
				WHERE (:category IS NULL AND i.category != 'hidden') OR i.category = :category
				AND it.name LIKE '%{searchText}%'
				ORDER BY i.id
			"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, ("en", self.currentItemCategory))
		data = data.fetchall()

		items = []
		for row in data:
			items.append(i.Item(row))

		if len(items) != 0:
			self.il.RemoveAll()

		for item in items:
			if os.path.exists(f"images/items-24/{item.iconName}{item.iconColor}.png"):
				img = self.il.Add(wx.Bitmap(f"images/items-24/{item.iconName}{item.iconColor}.png"))
			else:
				img = self.il.Add(wx.Bitmap(f"images/unknown.png"))
			index = self.itemList.InsertItem(self.itemList.GetItemCount(), f"{item.name}", img)
			self.itemList.SetItem(index, 1, f"{item.id}")

		if self.itemList.GetItemCount() != 0:
			self.itemList.Select(0)


	def loadCraftingList(self):
		try:
			self.itemList.ClearAll()
		except:
			pass
		self.test = self.il.Add(self.testIcon)

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_CENTER
		info.Text = ""
		self.itemList.InsertColumn(0, info)
		self.itemList.SetColumnWidth(0, 680)
		self.itemList.InsertColumn(1, info)
		self.itemList.SetColumnWidth(1, 0)

		searchText = self.search.GetValue().replace("'", "''")

		if len(searchText) == 0 or searchText == " ":
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
		else:
			sql = f"""
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
					AND result_name LIKE '%{searchText}%'
				ORDER BY c.id ASC
			"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, ("en", None))
		data = data.fetchall()

		combinations = []
		for row in data:
			combinations.append(i.CombinationObtaining(row))

		if len(combinations) != 0:
			self.il.RemoveAll()

		for com in combinations:
			if com.secondName != None:
				img = self.il.Add(wx.Bitmap(f"images/items-24/{com.resultIconName}{com.resultIconColor}.png"))
				index = self.itemList.InsertItem(self.itemList.GetItemCount(), f"{com.resultName} = {com.firstName} + {com.secondName}", img)
			else:
				img = self.il.Add(wx.Bitmap(f"images/items-24/{com.resultIconName}{com.resultIconColor}.png"))
				index = self.itemList.InsertItem(self.itemList.GetItemCount(), f"{com.resultName} = {com.firstName}", img)
			self.itemList.SetItem(index, 1, f"{com.resultID}")
		
		if self.itemList.GetItemCount() != 0:
			self.itemList.Select(0)


	def initItemDetail(self):
		self.itemNameLabel = wx.StaticText(self.itemDetailPanel, label="Name:", style=wx.ALIGN_LEFT)
		self.itemNameLabel.SetFont(self.itemNameLabel.GetFont().Bold())
		self.itemDetailSizer.Add(self.itemNameLabel, 0.2, wx.EXPAND)
		self.itemDescriptionLabel = wx.StaticText(self.itemDetailPanel, label="Description", style=wx.ALIGN_LEFT)
		self.itemDetailSizer.Add(self.itemDescriptionLabel, 0.5, wx.EXPAND)

		self.itemDetailList = wx.ListCtrl(self.itemDetailPanel, size=(600, 124), style=wx.LC_REPORT
																		| wx.LC_VRULES
																		| wx.LC_HRULES
																		| wx.LC_NO_HEADER
																		)
		self.itemDetailList.Bind(wx.EVT_MOUSEWHEEL, self.onScroll)
		self.itemDetailList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
		self.itemDetailSizer.Add(self.itemDetailList, 0.8, wx.EXPAND)


	def loadItemDetail(self):
		self.itemDetailList.ClearAll()

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = ""
		self.itemDetailList.InsertColumn(0, info)
		self.itemDetailList.SetColumnWidth(0, self.itemDetailPanel.GetSize()[0] * 0.66)

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_CENTER
		info.Text = ""
		self.itemDetailList.InsertColumn(1, info)
		self.itemDetailList.SetColumnWidth(1, self.itemDetailPanel.GetSize()[0] * 0.34 - 20)

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

		if os.path.exists(f"images/items-160/{item.iconName}{item.iconColor}.png"):
			self.itemImageLabel.SetBitmap(wx.Bitmap(f"images/items-160/{item.iconName}{item.iconColor}.png"))
		else:
			self.itemImageLabel.SetBitmap(wx.Bitmap(f"images/items-160/QuestionWhite.png"))
		
		self.itemNameLabel.SetLabelText(f"\n{item.name}:")
		self.itemDescriptionLabel.SetLabelText(f"{item.description}\n")
		self.itemDescriptionLabel.Wrap(650)

		img = self.il.Add(wx.Bitmap(f"images/item-rarity-24/{item.rarity}.png"))
		index = self.itemDetailList.InsertItem(self.itemDetailList.GetItemCount(), "Rarity", img)
		self.itemDetailList.SetItem(index, 1, f"{item.rarity}")
		if item.subcategory == "account":
			img = self.il.Add(wx.Bitmap("images/points.png"))
			index = self.itemDetailList.InsertItem(self.itemDetailList.GetItemCount(), "Buy", img)
			self.itemDetailList.SetItem(index, 1, "-")
			index = self.itemDetailList.InsertItem(self.itemDetailList.GetItemCount(), "Sell", img)
			self.itemDetailList.SetItem(index, 1, f"{item.points}")
		else:
			img = self.il.Add(wx.Bitmap("images/zenny.png"))
			index = self.itemDetailList.InsertItem(self.itemDetailList.GetItemCount(), "Buy", img)
			if item.buyPrice != 0:
				self.itemDetailList.SetItem(index, 1, f"{item.buyPrice}")
			else:
				self.itemDetailList.SetItem(index, 1, "-")
			if item.points > 0:
				index = self.itemDetailList.InsertItem(self.itemDetailList.GetItemCount(), "Sell", img)
			else:
				index = self.itemDetailList.InsertItem(self.itemDetailList.GetItemCount(), "Sell", img)
			if item.sellPrice != 0:
				self.itemDetailList.SetItem(index, 1, f"{item.sellPrice}")
			else:
				self.itemDetailList.SetItem(index, 1, "-")
		img = self.il.Add(wx.Bitmap("images/itemBox.png"))
		index = self.itemDetailList.InsertItem(self.itemDetailList.GetItemCount(), "Carry", img)
		if item.carryLimit != 0:
			self.itemDetailList.SetItem(index, 1, f"{item.carryLimit}")
		else:
			self.itemDetailList.SetItem(index, 1, "-")

		self.loadItemUsage()


	def initItemUsage(self):
		self.itemUsageList = wx.ListCtrl(self.itemDetailPanel, style=wx.LC_REPORT
																| wx.LC_VRULES
																| wx.LC_HRULES
																)
		self.itemUsageList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
		self.itemUsageList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onUsageOrObtainingDoubleClick)
		self.itemDetailSizer.Add(self.itemUsageList, 6, wx.EXPAND)


	def loadItemUsage(self):
		self.itemUsageList.ClearAll()

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = "Usage"
		self.itemUsageList.InsertColumn(0, info)
		self.itemUsageList.SetColumnWidth(0, self.itemDetailPanel.GetSize()[0] * 0.66)

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_CENTER
		info.Text = ""
		self.itemUsageList.InsertColumn(1, info)
		self.itemUsageList.SetColumnWidth(1, self.itemDetailPanel.GetSize()[0] * 0.34 - 40)

		self.itemUsageList.InsertColumn(2, info)
		self.itemUsageList.SetColumnWidth(2, 0)

		self.loadUsageCombinations()
		self.loadUsageCharms()
		self.loadUsageArmor()
		self.loadUsageWeapons()
		self.loadUsagePalico()
		self.loadUsageKinsects()

		self.loadItemObtaining()


	def loadUsageCombinations(self):
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
				OR c.first_id = :itemId
				OR c.second_id = :itemId
			ORDER BY c.id ASC
		"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, ("en", self.currentlySelectedItemID))
		data = data.fetchall()

		combinations = []
		for row in data:
			if row[2] != self.currentItemName:
				combinations.append(i.CombinationObtaining(row))

		for com in combinations:
			if com.secondName != None:
				img = self.il.Add(wx.Bitmap(f"images/items-24/{com.resultIconName}{com.resultIconColor}.png"))
				index = self.itemUsageList.InsertItem(self.itemUsageList.GetItemCount(), f"{com.resultName} = {com.firstName} + {com.secondName}", img)
			else:
				img = self.il.Add(wx.Bitmap(f"images/items-24/{com.resultIconName}{com.resultIconColor}.png"))
				index = self.itemUsageList.InsertItem(self.itemUsageList.GetItemCount(), f"{com.resultName} = {com.firstName}", img)
			self.itemUsageList.SetItem(index, 1, f"x {com.quantity}")
			self.itemUsageList.SetItem(index, 2, f"item,{com.resultID},{com.resultCategory},{com.resultName}")


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

		for charm in charms:
			img = self.il.Add(wx.Bitmap(f"images/charms-24/{charm.rarity}.png"))
			index = self.itemUsageList.InsertItem(self.itemUsageList.GetItemCount(), charm.name, img)
			self.itemUsageList.SetItem(index, 1, f"{charm.quantity}")
			self.itemUsageList.SetItem(index, 2, f"charm,{charm.id}")


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

		for arm in armor:
			img = self.il.Add(wx.Bitmap(f"images/armor/{arm.armorType}/rarity-24/{arm.rarity}.png"))
			index = self.itemUsageList.InsertItem(self.itemUsageList.GetItemCount(), arm.name, img)
			self.itemUsageList.SetItem(index, 1, f"{arm.quantity}")
			self.itemUsageList.SetItem(index, 2, f"armor,{arm.id}")


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

		for weapon in weapons:
			img = self.il.Add(wx.Bitmap(f"images/weapons/{weapon.weaponType}/rarity-24/{weapon.rarity}.png"))
			index = self.itemUsageList.InsertItem(self.itemUsageList.GetItemCount(), weapon.name, img)
			self.itemUsageList.SetItem(index, 1, f"{weapon.quantity}")
			self.itemUsageList.SetItem(index, 2, f"weapon,{weapon.id},{weapon.weaponType}")
		

	def loadUsagePalico(self):
		sql = """
			SELECT p.id, p.name, p.attack_type, p.rarity, pr.quantity, p.rank
			FROM palico_weapon p
				JOIN palico_weapon_recipe pr
				ON p.id = pr.id
			WHERE pr.item_id = :palicoID
		"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, (self.currentlySelectedItemID,))
		data = data.fetchall()

		for wep in data:
			img = self.il.Add(wx.Bitmap(f"images/palico/{wep[2].lower()}-rarity-24/{wep[3]}.png"))
			index = self.itemUsageList.InsertItem(self.itemUsageList.GetItemCount(), wep[1], img)
			self.itemUsageList.SetItem(index, 1, f"{wep[4]}")
			self.itemUsageList.SetItem(index, 2, f"palico,{wep[0]},{wep[5]},weapon")

		sql = """
			SELECT p.id, p.name, p.rarity, pr.quantity, p.rank
			FROM palico_armor p
				JOIN palico_armor_recipe pr
				ON p.id = pr.id
			WHERE pr.item_id = :palicoID
		"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, (self.currentlySelectedItemID,))
		data = data.fetchall()

		for arm in data:
			if arm[0] % 3 == 2:
				img = self.il.Add(wx.Bitmap(f"images/palico/chest-rarity-24/{arm[2]}.png"))
			else:
				img = self.il.Add(wx.Bitmap(f"images/palico/head-rarity-24/{arm[2]}.png"))
			index = self.itemUsageList.InsertItem(self.itemUsageList.GetItemCount(), arm[1], img)
			self.itemUsageList.SetItem(index, 1, f"{arm[3]}")
			self.itemUsageList.SetItem(index, 2, f"palico,{arm[0]},{arm[4]},armor")


	def loadUsageKinsects(self):
		sql = """
			SELECT k.id, kt.name, k.attack_type, k.rarity, kr.quantity
			FROM kinsect k
				JOIN kinsect_text kt USING (id)
				JOIN kinsect_recipe kr ON k.id = kr.kinsect_id
			WHERE kt.lang_id = 'en'
				AND kr.item_id = :kinsectID
		"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, (self.currentlySelectedItemID,))
		data = data.fetchall()

		for kin in data:
			img = self.il.Add(wx.Bitmap(f"images/kinsects/{kin[2].lower()}-rarity-24/{kin[3]}.png"))
			index = self.itemUsageList.InsertItem(self.itemUsageList.GetItemCount(), kin[1], img)
			self.itemUsageList.SetItem(index, 1, f"{kin[4]}")
			self.itemUsageList.SetItem(index, 2, f"kinsect,{kin[0]}")


	def initItemObtaining(self):
		self.itemObtainingList = wx.ListCtrl(self.itemDetailPanel, style=wx.LC_REPORT
																	| wx.LC_VRULES
																	| wx.LC_HRULES
																	)
		self.itemObtainingList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onUsageOrObtainingDoubleClick)
		self.itemObtainingList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
		self.itemDetailSizer.Add(self.itemObtainingList, 4, wx.EXPAND)


	def loadItemObtaining(self):
		self.itemObtainingList.ClearAll()

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = "Obtaining"
		self.itemObtainingList.InsertColumn(0, info)
		self.itemObtainingList.SetColumnWidth(0, self.itemDetailPanel.GetSize()[0] * 0.66)

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_CENTER
		info.Text = ""
		self.itemObtainingList.InsertColumn(1, info)
		self.itemObtainingList.SetColumnWidth(1, self.itemDetailPanel.GetSize()[0] * 0.34 - 40)

		self.itemObtainingList.InsertColumn(2, info)
		self.itemObtainingList.SetColumnWidth(2, 0)

		self.loadObtainingCombination()
		self.loadObtainingLocations()
		self.loadObtainingRewards()


	def loadObtainingCombination(self):
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
			ORDER BY c.id ASC
		"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, ("en", self.currentlySelectedItemID))
		data = data.fetchall()

		combinations = []
		for row in data:
			if row[2] == self.currentItemName:
				combinations.append(i.CombinationObtaining(row))

		for com in combinations:
			if com.secondName != None:
				img = self.il.Add(wx.Bitmap(f"images/items-24/{com.resultIconName}{com.resultIconColor}.png"))
				index = self.itemObtainingList.InsertItem(self.itemObtainingList.GetItemCount(), f"{com.resultName} = {com.firstName} + {com.secondName}", img)
			else:
				img = self.il.Add(wx.Bitmap(f"images/items-24/{com.resultIconName}{com.resultIconColor}.png"))
				index = self.itemObtainingList.InsertItem(self.itemObtainingList.GetItemCount(), f"{com.resultName} = {com.firstName}", img)
			self.itemObtainingList.SetItem(index, 1, f"x {com.quantity}")
			self.itemObtainingList.SetItem(index, 2, f"item,{com.resultID}")


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

		for local in locations:
			img = self.il.Add(wx.Bitmap(f"images/locations-24/{local.name}.png"))
			index = self.itemObtainingList.InsertItem(self.itemObtainingList.GetItemCount(),
				f"{local.name} - Area {local.area}", img)
			self.itemObtainingList.SetItem(index, 1, f"{local.stack} x {local.percentage}%")
			self.itemObtainingList.SetItem(index, 2, f"location,{local.id},{local.name}")


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
			rewards.append(i.RewardObtaining(row))

		for reward in rewards:
			img = self.il.Add(wx.Bitmap(f"images/monsters/24/{reward.monsterName}.png"))
			index = self.itemObtainingList.InsertItem(self.itemObtainingList.GetItemCount(),
				f"{reward.monsterName} - {reward.rank} {reward.rewardName}", img)
			self.itemObtainingList.SetItem(index, 1, f"{reward.stack} x {reward.percentage}%")
			self.itemObtainingList.SetItem(index, 2, f"monster,{reward.id},{reward.monsterName}")


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

		self.currentlySelectedItemID = self.itemList.GetItemText(event.GetEventObject().GetFirstSelected(), 1)
		if self.currentlySelectedItemID != "":
			if self.currentItemCategory == "crafting":
				name = self.itemList.GetItemText(event.GetEventObject().GetFirstSelected(), 0)
				self.currentItemName = name[:name.find(" =")]
			else:
				self.currentItemName = self.itemList.GetItemText(event.GetEventObject().GetFirstSelected(), 0)
			self.loadItemDetailAll()


	def onUsageOrObtainingDoubleClick(self, event):
		materialInfo = event.GetEventObject().GetItemText(event.GetEventObject().GetFirstSelected(), 2).split(",")
		self.link.event = True
		self.link.eventType = materialInfo[0]
		if len(materialInfo) == 4:
			if self.link.eventType == "palico":
				self.root.palico.currentEquipmentCategory = materialInfo[-1]
			else:
				self.currentItemName = materialInfo[-1]
			materialInfo.remove(materialInfo[-1])
		materialInfo.remove(materialInfo[0])
		if len(materialInfo) == 1:
			self.link.info = link.GenericSingleLink(materialInfo[0])
		elif len(materialInfo) == 2:
			self.link.info = link.GenericDoubleLink(materialInfo)
		else:
			debug(materialInfo, "materialInfo", "materialInfo length is other than accounted for!")
		self.root.followLink()
		self.link.reset()


	def onSize(self, event):
		"""
		When the application window is resized some columns's width gets readjusted.
		"""

		self.itemDetailList.SetColumnWidth(0, self.itemDetailPanel.GetSize()[0] * 0.66)
		self.itemDetailList.SetColumnWidth(1, self.itemDetailPanel.GetSize()[0] * 0.34 - 20)
		self.itemUsageList.SetColumnWidth(0, self.itemDetailPanel.GetSize()[0] * 0.66)
		self.itemUsageList.SetColumnWidth(1, self.itemDetailPanel.GetSize()[0] * 0.34 - 40)
		self.itemObtainingList.SetColumnWidth(0, self.itemDetailPanel.GetSize()[0] * 0.66)
		self.itemObtainingList.SetColumnWidth(1, self.itemDetailPanel.GetSize()[0] * 0.34 - 40)
		event.Skip()


	def onScroll(self, event):
		"""
		On every scroll event in itemDetail, scrolls the parent ScrolledWindow by 3 in the appropriate direction.
		"""
		
		if event.GetWheelRotation() > 0:
			if self.itemDetailPanel.GetViewStart()[1] < 3:
				self.itemDetailPanel.Scroll(0, self.itemDetailPanel.GetViewStart()[1] + 1 * -1)
			else:
				self.itemDetailPanel.Scroll(0, self.itemDetailPanel.GetViewStart()[1] + 3 * -1)
		else:
			if self.itemDetailPanel.GetViewStart()[1] < 3:
				self.itemDetailPanel.Scroll(0, self.itemDetailPanel.GetViewStart()[1] + 1)
			else:
				self.itemDetailPanel.Scroll(0, self.itemDetailPanel.GetViewStart()[1] + 3)
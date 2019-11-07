import wx
import sqlite3

import CustomGridRenderer as cgr
from Debug.debug import debug
import Links as link

class SearchWindow:

	def __init__(self, root, link):
		self.root = root
		self.link = link
		self.init = True
		self.conn = sqlite3.connect("mhw.db")
		self.padding = " " * 8

		self.win = wx.Frame(root, title="Search")
		self.win.SetIcon(wx.Icon("images/Nergigante.png"))
		self.win.SetSize(700, 700)
		self.win.Center()
		self.win.Bind(wx.EVT_CLOSE, self.onClose)

		panel = wx.Panel(self.win)
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.searchName = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
		self.searchName.SetHint("  search by name")
		self.searchName.Bind(wx.EVT_TEXT_ENTER, self.searchByName)
		sizer.Add(self.searchName, 1, wx.EXPAND)

		self.searchSkill = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
		self.searchSkill.SetHint("  search by skill")
		self.searchSkill.Bind(wx.EVT_TEXT_ENTER, self.searchBySkill)
		sizer.Add(self.searchSkill, 1, wx.EXPAND)

		self.results = cgr.HeaderBitmapGrid(panel)
		self.results.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.onDoubleClick)
		self.results.Bind(wx.grid.EVT_GRID_TABBING, self.onTab)
		self.results.EnableEditing(False)
		self.results.EnableDragRowSize(False)
		self.results.CreateGrid(1, 2)
		self.results.SetDefaultRowSize(27, resizeExistingRows=True)
		self.results.HideRowLabels()
		self.results.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
		self.results.SetColLabelValue(0, "Name")
		self.results.SetColSize(0, 660)
		self.results.SetColSize(1, 0)
		sizer.Add(self.results, 120, wx.EXPAND)

		panel.SetSizer(sizer)
		self.makeMenuBar()
		self.win.Show()
		self.init = False

	
	def onTab(self, event):
		self.searchName.SetFocus()


	def onDoubleClick(self, event):
		materialInfo = self.results.GetCellValue(event.GetRow(), 1).split(",")
		self.link.event = True
		self.link.eventType = materialInfo[0]
		if len(materialInfo) == 4:
			if self.link.eventType == "item":
				self.root.items.currentItemName = materialInfo[-1]
			elif self.link.eventType == "armorset":
				self.root.armor.currentlySelectedArmorSetID = materialInfo[-1]
			else:
				debug(materialInfo, "self.link.eventType", "self.link.eventType unsupported eventType!")
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
		if not self.root.pref.keepSearchOpen:
			self.onClose(None)


	def searchByName(self, event):
		self.searchText = self.searchName.GetValue().replace("'", "''")

		try:
			self.results.DeleteRows(0, self.results.GetNumberRows())
		except:
			pass

		self.loadMonsters()
		self.loadWeapons()
		self.loadArmor()
		self.loadCharms()
		self.loadDecorations()
		self.loadSkills()
		self.loadItems()
		self.loadLocations()


	def searchBySkill(self, event):
		self.searchText = self.searchSkill.GetValue().replace("'", "''")

		try:
			self.results.DeleteRows(0, self.results.GetNumberRows())
		except:
			pass

		sql = f"""
			SELECT DISTINCT abs.setbonus_id, at.name, abt.name, stt.name, a.rarity, a.id, a.rank, a.armorset_id
			FROM armorset_bonus_skill abs
				JOIN armorset_bonus_text abt
					ON abt.id = abs.setbonus_id
				JOIN skilltree st
					ON abs.skilltree_id = st.id
				JOIN skilltree_text stt
					ON abs.skilltree_id = stt.id
				JOIN armor a
					ON a.armorset_bonus_id = abs.setbonus_id
				JOIN armorset_text at
					ON a.armorset_id = at.id
			WHERE abt.lang_id = 'en'
				AND stt.lang_id = 'en'
				AND at.lang_id = 'en'
				AND a.armor_type = 'head'
				AND stt.name LIKE '%{self.searchText}%'
			ORDER BY abs.setbonus_id
		"""

		data = self.conn.execute(sql,)
		data = data.fetchall()

		for row in data:
			self.results.AppendRows()
			r = self.results.GetNumberRows() - 1
			img = wx.Bitmap(f"images/armor/armorset/rarity-24/{row[4]}.png")
			self.results.SetCellRenderer(r, 0, cgr.ImageTextCellRenderer(img, f"{self.padding}{row[1]}", hAlign=wx.ALIGN_LEFT, imageOffset=320))
			self.results.SetCellValue(r, 1, f"armorset,{row[5]},{row[6]},{row[7]}")

		sql = f"""
			SELECT a.id, at.name, a.armor_type, a.rarity, a.rank
			FROM armor_skill askill
				JOIN armor a
					ON askill.armor_id = a.id
				JOIN skilltree s
					ON askill.skilltree_id = s.id
				JOIN skilltree_text stt
					ON askill.skilltree_id = stt.id
				JOIN armor_text at
					ON a.id = at.id
			WHERE at.lang_id = 'en'
				AND stt.lang_id = 'en'
				AND stt.name LIKE '%{self.searchText}%'
		"""

		data = self.conn.execute(sql,)
		data = data.fetchall()

		for row in data:
			self.results.AppendRows()
			r = self.results.GetNumberRows() - 1
			img = wx.Bitmap(f"images/armor/{row[2]}/rarity-24/{row[3]}.png")
			self.results.SetCellRenderer(r, 0, cgr.ImageTextCellRenderer(img, f"{self.padding}{row[1]}", hAlign=wx.ALIGN_LEFT, imageOffset=320))
			self.results.SetCellValue(r, 1, f"armor,{row[0]},{row[4]}")

		sql = f"""
			SELECT c.id, ct.name, c.rarity, stt.name 
			FROM charm c
				JOIN charm_text ct
					ON ct.id = c.id
					AND ct.lang_id = 'en'
				JOIN charm_skill cs
					ON cs.charm_id = c.id
				JOIN skilltree_text stt
					ON stt.id = cs.skilltree_id
					AND stt.lang_id = 'en'
				WHERE stt.name LIKE '%{self.searchText}%'
			ORDER BY ct.name
		"""

		data = self.conn.execute(sql,)
		data = data.fetchall()

		for row in data:
			self.results.AppendRows()
			r = self.results.GetNumberRows() - 1
			img = wx.Bitmap(f"images/charms-24/{row[2]}.png")
			self.results.SetCellRenderer(r, 0, cgr.ImageTextCellRenderer(img, f"{self.padding}{row[1]}", hAlign=wx.ALIGN_LEFT, imageOffset=320))
			self.results.SetCellValue(r, 1, f"charm,{row[0]}")

		sql = f"""
			SELECT d.id, dt.name, d.icon_color, stt.name
			FROM decoration d
				JOIN decoration_text dt
					ON dt.id = d.id
					AND dt.lang_id = 'en'
				JOIN skilltree_text stt
					ON stt.id = d.skilltree_id
					AND stt.lang_id = 'en'
				WHERE stt.name LIKE '%{self.searchText}%'
			ORDER BY dt.name
		"""

		data = self.conn.execute(sql,)
		data = data.fetchall()

		for row in data:
			self.results.AppendRows()
			r = self.results.GetNumberRows() - 1
			img = wx.Bitmap(f"images/items-24/Feystone{row[2]}.png")
			self.results.SetCellRenderer(r, 0, cgr.ImageTextCellRenderer(img, f"{self.padding}{row[1]}", hAlign=wx.ALIGN_LEFT, imageOffset=320))
			self.results.SetCellValue(r, 1, f"decoration,{row[0]}")

		self.loadSkills()

		
	def loadMonsters(self):
		sql = f"""
			SELECT m.id, mt.name
			FROM monster m
			JOIN monster_text mt
				ON m.id = mt.id
			WHERE mt.name LIKE '%{self.searchText}%'
				AND mt.lang_id = 'en'
		"""

		data = self.conn.execute(sql,)
		data = data.fetchall()

		for row in data:
			self.results.AppendRows()
			r = self.results.GetNumberRows() - 1
			img = wx.Bitmap(f"images/monsters/24/{row[1]}.png")
			self.results.SetCellRenderer(r, 0, cgr.ImageTextCellRenderer(img, f"{self.padding}{row[1]}", hAlign=wx.ALIGN_LEFT, imageOffset=320))
			self.results.SetCellValue(r, 1, f"monster,{row[0]},{row[1]}")

	
	def loadWeapons(self):
		sql = f"""
			SELECT w.id, w.weapon_type, w.rarity, wt.name
			FROM weapon w
				JOIN weapon_text wt USING (id)
			WHERE wt.lang_id = 'en'
				AND wt.name LIKE '%{self.searchText}%'
			ORDER BY w.id ASC
		"""

		data = self.conn.execute(sql,)
		data = data.fetchall()
		
		for row in data:
			self.results.AppendRows()
			r = self.results.GetNumberRows() - 1
			img = wx.Bitmap(f"images/weapons/{row[1]}/rarity-24/{row[2]}.png")
			self.results.SetCellRenderer(r, 0, cgr.ImageTextCellRenderer(img, f"{self.padding}{row[3]}", hAlign=wx.ALIGN_LEFT, imageOffset=320))
			self.results.SetCellValue(r, 1, f"weapon,{row[0]},{row[1]}")


	def loadArmor(self):
		sql = f"""
			SELECT DISTINCT a.id, ast.name, a.rank, a.rarity, a.armorset_id
			FROM armor a
				JOIN armor_text at
					ON at.id = a.id
					AND at.lang_id = 'en'
				JOIN armorset_text ast
					ON ast.id = a.armorset_id
					AND ast.lang_id = 'en'
			WHERE ast.name LIKE '%{self.searchText}%'
			AND a.armor_type = 'head'
		"""

		data = self.conn.execute(sql,)
		data = data.fetchall()

		for row in data:
			self.results.AppendRows()
			r = self.results.GetNumberRows() - 1
			img = wx.Bitmap(f"images/armor/armorset/rarity-24/{row[3]}.png")
			self.results.SetCellRenderer(r, 0, cgr.ImageTextCellRenderer(img, f"{self.padding}{row[1]}", hAlign=wx.ALIGN_LEFT, imageOffset=320))
			self.results.SetCellValue(r, 1, f"armorset,{row[0]},{row[2]},{row[4]}")

		sql = f"""
			SELECT a.id, at.name, a.armor_type, a.rarity, a.rank
			FROM armor a
				JOIN armor_text at USING (id)
			WHERE at.lang_id = 'en'
				AND at.name LIKE '%{self.searchText}%'
		"""

		data = self.conn.execute(sql,)
		data = data.fetchall()

		for row in data:
			self.results.AppendRows()
			r = self.results.GetNumberRows() - 1
			img = wx.Bitmap(f"images/armor/{row[2]}/rarity-24/{row[3]}.png")
			self.results.SetCellRenderer(r, 0, cgr.ImageTextCellRenderer(img, f"{self.padding}{row[1]}", hAlign=wx.ALIGN_LEFT, imageOffset=320))
			self.results.SetCellValue(r, 1, f"armor,{row[0]},{row[4]}")


	def loadCharms(self):
		sql = f"""
			SELECT c.id, ct.name, c.rarity
			FROM charm c
				JOIN charm_text ct
					ON ct.id = c.id
					AND ct.lang_id = 'en'
					AND ct.name LIKE '%{self.searchText}%'
		"""

		data = self.conn.execute(sql,)
		data = data.fetchall()

		for row in data:
			self.results.AppendRows()
			r = self.results.GetNumberRows() - 1
			img = wx.Bitmap(f"images/charms-24/{row[2]}.png")
			self.results.SetCellRenderer(r, 0, cgr.ImageTextCellRenderer(img, f"{self.padding}{row[1]}", hAlign=wx.ALIGN_LEFT, imageOffset=320))
			self.results.SetCellValue(r, 1, f"charm,{row[0]}")


	def loadDecorations(self):
		sql = f"""
			SELECT d.id, dt.name, d.icon_color
			FROM decoration d
				JOIN decoration_text dt
					ON dt.id = d.id
					AND dt.lang_id = 'en'
				WHERE dt.name LIKE '%{self.searchText}%'
		"""

		data = self.conn.execute(sql,)
		data = data.fetchall()

		for row in data:
			self.results.AppendRows()
			r = self.results.GetNumberRows() - 1
			img = wx.Bitmap(f"images/items-24/Feystone{row[2]}.png")
			self.results.SetCellRenderer(r, 0, cgr.ImageTextCellRenderer(img, f"{self.padding}{row[1]}", hAlign=wx.ALIGN_LEFT, imageOffset=320))
			self.results.SetCellValue(r, 1, f"decoration,{row[0]}")


	def loadSkills(self):
		sql = f"""
			SELECT id, name, icon_color
			FROM skilltree s join skilltree_text st USING (id)
			WHERE lang_id = 'en'
			AND name LIKE '%{self.searchText}%'
		"""

		data = self.conn.execute(sql,)
		data = data.fetchall()

		for row in data:
			self.results.AppendRows()
			r = self.results.GetNumberRows() - 1
			img = wx.Bitmap(f"images/skills-24/Skill{row[2]}.png")
			self.results.SetCellRenderer(r, 0, cgr.ImageTextCellRenderer(img, f"{self.padding}{row[1]}", hAlign=wx.ALIGN_LEFT, imageOffset=320))
			self.results.SetCellValue(r, 1, f"skill,{row[0]}")


	def loadItems(self):
		sql = f"""
			SELECT i.id, it.name, i.category, i.icon_name, i.icon_color
			FROM item i
				JOIN item_text it
					ON it.id = i.id
					AND it.lang_id = 'en'
			WHERE i.category != 'hidden'
				AND it.name LIKE '%{self.searchText}%'
		"""

		data = self.conn.execute(sql,)
		data = data.fetchall()

		for row in data:
			self.results.AppendRows()
			r = self.results.GetNumberRows() - 1
			img = wx.Bitmap(f"images/items-24/{row[3]}{row[4]}.png")
			self.results.SetCellRenderer(r, 0, cgr.ImageTextCellRenderer(img, f"{self.padding}{row[1]}", hAlign=wx.ALIGN_LEFT, imageOffset=320))
			self.results.SetCellValue(r, 1, f"item,{row[0]},{row[2]},{row[1]}")


	def loadLocations(self):
		sql = f"""
			SELECT id, name
			FROM location_text t
			WHERE t.lang_id = 'en'
				AND name LIKE '%{self.searchText}%'
		"""

		data = self.conn.execute(sql,)
		data = data.fetchall()

		for row in data:
			self.results.AppendRows()
			r = self.results.GetNumberRows() - 1
			img = wx.Bitmap(f"images/locations-24/{row[1]}.png")
			self.results.SetCellRenderer(r, 0, cgr.ImageTextCellRenderer(img, f"{self.padding}{row[1]}", hAlign=wx.ALIGN_LEFT, imageOffset=320))
			self.results.SetCellValue(r, 1, f"location,{row[0]},{row[1]}")


	def makeMenuBar(self):
		fileMenu = wx.Menu()
		closeItem = fileMenu.Append(-1, "&Close\tCtrl-F", "Closes the search window.")
		
		menuBar = wx.MenuBar()
		menuBar.Append(fileMenu, "&File")

		self.win.SetMenuBar(menuBar)

		self.win.Bind(wx.EVT_MENU, self.onClose, closeItem)


	def onClose(self, event):
		self.win.Destroy()
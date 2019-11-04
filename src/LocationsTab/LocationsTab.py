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

import LocationsTab as l
import Links as link

class LocationsTab:

	def __init__(self, root, mainNotebook, link):
		self.root = root
		self.mainNotebook = mainNotebook
		self.link = link

		self.currentLocationID = 1
		self.currentLocationName = "Ancient Forest"
		self.testIcon = wx.Bitmap("images/unknown.png", wx.BITMAP_TYPE_ANY)
		self.initLocationTab()


	def initLocationTab(self):
		self.locationPanel = wx.Panel(self.mainNotebook)
		self.mainNotebook.AddPage(self.locationPanel, "Locations")
		self.locationSizer = wx.BoxSizer(wx.HORIZONTAL)

		self.locationListSizer = wx.BoxSizer(wx.VERTICAL) 
		
		self.locationDetailedSizer = wx.BoxSizer(wx.VERTICAL)
		self.locationImage = wx.Bitmap("images/locations-160/Ancient Forest.png", wx.BITMAP_TYPE_ANY)
		self.locationImageLabel = wx.StaticBitmap(self.locationPanel, bitmap=self.locationImage, size=(160, 160))

		self.locationDetailsNotebook = wx.Notebook(self.locationPanel)
		self.locationDetailPanel = wx.Panel(self.locationDetailsNotebook)

		self.locationDetailSizer = wx.BoxSizer(wx.VERTICAL)
		self.locationDetailsNotebook.AddPage(self.locationDetailPanel, "Detail")
		self.locationDetailPanel.SetSizer(self.locationDetailSizer)
		
		self.locationDetailedSizer.Add(self.locationImageLabel, 1, wx.ALIGN_CENTER)
		self.locationDetailedSizer.Add(self.locationDetailsNotebook, 3, wx.EXPAND)

		self.locationSizer.Add(self.locationListSizer, 1, wx.EXPAND)
		self.locationSizer.Add(self.locationDetailedSizer, 1, wx.EXPAND)

		self.locationPanel.SetSizer(self.locationSizer)

		self.initLocationList()
		self.initLocationDetail()
		self.loadLocationList()
		self.loadLocationDetail()


	def initLocationList(self):
		self.locationList = wx.ListCtrl(self.locationPanel, style=wx.LC_REPORT
														| wx.LC_VRULES
														| wx.LC_HRULES
														)
		self.locationList.Bind(wx.EVT_SIZE, self.onSize)
		self.locationListSizer.Add(self.locationList, 1, wx.EXPAND)
		self.locationList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onLocationSelected)

		self.il = wx.ImageList(24, 24)
		self.test = self.il.Add(self.testIcon)
		self.locationList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)


	def loadLocationList(self):
		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = ""
		self.locationList.InsertColumn(0, info)
		self.locationList.SetColumnWidth(0, 680)
		self.locationList.InsertColumn(1, info)
		self.locationList.SetColumnWidth(1, 0)


		sql = """
			SELECT id, name
			FROM location_text t
			WHERE t.lang_id = :langId
			ORDER BY order_id ASC
		"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, ("en", ))
		data = data.fetchall()

		locations = []
		for row in data:
			locations.append(l.Location(row))

		for location in locations:
			img = self.il.Add(wx.Bitmap(f"images/locations-24/{location.name}.png"))
			index = self.locationList.InsertItem(self.locationList.GetItemCount(), location.name, img)
			self.locationList.SetItem(index, 1, f"{location.id}")


	def initLocationDetail(self):
		self.locationNameLabel = wx.StaticText(self.locationDetailPanel, label = "placeholder")
		self.locationNameLabel.SetFont(self.locationNameLabel.GetFont().Bold())
		self.locationDetailSizer.Add(self.locationNameLabel, 1, wx.EXPAND)

		self.baseCampList = wx.ListCtrl(self.locationDetailPanel, style=wx.LC_REPORT
																| wx.LC_VRULES
																| wx.LC_HRULES
																)
		self.baseCampList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
		self.locationDetailSizer.Add(self.baseCampList, 1, wx.EXPAND)

		self.materialList = wx.ListCtrl(self.locationDetailPanel, style=wx.LC_REPORT
																| wx.LC_VRULES
																| wx.LC_HRULES
																)
		self.materialList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onMaterialDoubleClick)
		self.materialList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
		self.locationDetailSizer.Add(self.materialList, 7, wx.EXPAND)


	def loadLocationDetail(self):
		self.root.Freeze()

		self.baseCampList.ClearAll()
		self.materialList.ClearAll()

		self.locationNameLabel.SetLabelText(f"\n{self.currentLocationName}")
		self.locationImageLabel.SetBitmap(wx.Bitmap(f"images/locations-160/{self.currentLocationName}.png"))

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = "Base Camps"
		self.baseCampList.InsertColumn(0, info)
		self.baseCampList.SetColumnWidth(0, self.locationDetailPanel.GetSize()[0] * 0.66)

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_CENTER
		info.Text = ""
		self.baseCampList.InsertColumn(1, info)
		self.baseCampList.SetColumnWidth(1, self.locationDetailPanel.GetSize()[0] * 0.34 - 20)

		sql = """
			SELECT lct.name, lct.area
			FROM location_camp_text lct
			WHERE lct.location_id = :locationId
			AND lct.lang_id = :langId
			ORDER BY lct.id ASC
		"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, (self.currentLocationID, "en"))
		data = data.fetchall()

		camps = []
		for row in data:
			camps.append(l.LocationBaseCamp(row))
		img = self.il.Add(wx.Bitmap(f"images/locations-24/camp.png"))
		for camp in camps:
			index = self.baseCampList.InsertItem(self.baseCampList.GetItemCount(), camp.name, img)
			self.baseCampList.SetItem(index, 1, f"Area {camp.area}")

		info = wx.ListItem()
		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_LEFT
		info.Text = "Gathering" # maybe "Materials"
		self.materialList.InsertColumn(0, info)
		self.materialList.SetColumnWidth(0, self.locationDetailPanel.GetSize()[0] * 0.66)
		info = wx.ListItem()

		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_CENTER
		info.Text = ""
		self.materialList.InsertColumn(1, info)
		self.materialList.SetColumnWidth(1, self.locationDetailPanel.GetSize()[0] * 0.22)

		info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
		info.Image = -1
		info.Align = wx.LIST_FORMAT_CENTER
		info.Text = ""
		self.materialList.InsertColumn(2, info)
		self.materialList.SetColumnWidth(2, self.locationDetailPanel.GetSize()[0] * 0.12 - 20)

		self.materialList.InsertColumn(3, info)
		self.materialList.SetColumnWidth(3, 0)

		sql = """
			SELECT i.id item_id, it.name item_name, i.icon_name item_icon_name, i.icon_color item_icon_color, i.category item_category,
				li.rank, li.area, li.stack, li.percentage, li.nodes
			FROM location_item li
				JOIN item i
					ON i.id = li.item_id
				JOIN item_text it
					ON it.id = i.id
			WHERE li.location_id = :locationId
			AND it.lang_id = :langId
			ORDER BY item_name
		"""

		conn = sqlite3.Connection("mhw.db")
		data = conn.execute(sql, (self.currentLocationID, "en"))
		data = data.fetchall()

		materials = []
		for row in data:
			materials.append(l.LocationMaterial(row))
		for mat in materials:
			img = self.il.Add(wx.Bitmap(f"images/materials-24/{mat.iconName}{mat.iconColor}.png"))
			index = self.materialList.InsertItem(self.materialList.GetItemCount(), mat.name, img)
			self.materialList.SetItem(index, 1, f"{mat.stack} x {mat.percentage}%")
			self.materialList.SetItem(index, 2, f"Area {mat.area}")
			self.materialList.SetItem(index, 3, f"{mat.id},{mat.category}")

		self.root.Thaw()


	def onMaterialDoubleClick(self, event):
		materialInfo = self.materialList.GetItemText(event.GetEventObject().GetFirstSelected(), 3)
		materialInfo = materialInfo.split(",")
		self.link.event = True
		self.link.eventType = "item"
		self.link.info =  link.GenericDoubleLink(materialInfo)
		self.root.followLink()
		self.link.reset()


	def onLocationSelected(self, event):
		self.currentLocationName = self.locationList.GetItemText(event.GetEventObject().GetFirstSelected(), 0)
		self.currentLocationID = self.locationList.GetItemText(event.GetEventObject().GetFirstSelected(), 1)
		if int(self.currentLocationID) > 0:
			self.loadLocationDetail()

		
	def onSize(self, event):
		self.baseCampList.SetColumnWidth(0, self.locationDetailPanel.GetSize()[0] * 0.66)
		self.baseCampList.SetColumnWidth(1, self.locationDetailPanel.GetSize()[0] * 0.34 - 20)
		self.materialList.SetColumnWidth(0, self.locationDetailPanel.GetSize()[0] * 0.66)
		self.materialList.SetColumnWidth(1, self.locationDetailPanel.GetSize()[0] * 0.22)
		self.materialList.SetColumnWidth(2, self.locationDetailPanel.GetSize()[0] * 0.12 - 20)
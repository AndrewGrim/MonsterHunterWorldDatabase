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

class ItemsTab:

	def __init__(self, root, mainNotebook):
		self.root = root
		self.mainNotebook = mainNotebook

		self.currentlySelectedItemID = 1
		self.testIcon = wx.Bitmap("images/unknown.png", wx.BITMAP_TYPE_ANY) # REMOVE since youll be using specific icons

		self.initItemTab()


	def initItemTab(self):
		self.itemsPanel = wx.Panel(self.mainNotebook)
		self.mainNotebook.AddPage(self.itemsPanel, "Items")
		self.itemsSizer = wx.BoxSizer(wx.HORIZONTAL)

		self.itemListSizer = wx.BoxSizer(wx.VERTICAL) 
		
		self.itemsDetailedSizer = wx.BoxSizer(wx.VERTICAL)
		self.itemImage = wx.Bitmap("images/weapons/great-sword/Buster Sword I.png", wx.BITMAP_TYPE_ANY)
		self.itemImageLabel = wx.StaticBitmap(self.itemsPanel, bitmap=self.itemImage, size=(160, 160))

		self.itemDetailsNotebook = wx.Notebook(self.itemsPanel)
		self.itemDetailPanel = wx.Panel(self.itemDetailsNotebook)
		self.itemUsagePanel = wx.Panel(self.itemDetailsNotebook)
		self.itemObtainingPanel = wx.Panel(self.itemDetailsNotebook)

		self.itemDetailSizer = wx.BoxSizer(wx.VERTICAL)
		self.itemDetailsNotebook.AddPage(self.itemDetailPanel, "Summary")
		self.itemDetailPanel.SetSizer(self.itemDetailSizer)

		self.itemUsageSizer = wx.BoxSizer(wx.VERTICAL)
		self.itemDetailsNotebook.AddPage(self.itemUsagePanel, "Usage")
		self.itemUsagePanel.SetSizer(self.itemUsageSizer)

		self.itemObtainingSizer = wx.BoxSizer(wx.VERTICAL)
		self.itemDetailsNotebook.AddPage(self.itemObtainingPanel, "Obtaining")
		self.itemObtainingPanel.SetSizer(self.itemObtainingSizer)
		
		self.itemsDetailedSizer.Add(self.itemImageLabel, 1, wx.ALIGN_CENTER)
		self.itemsDetailedSizer.Add(self.itemDetailsNotebook, 3, wx.EXPAND)

		self.itemsSizer.Add(self.itemListSizer, 1, wx.EXPAND)
		self.itemsSizer.Add(self.itemsDetailedSizer, 1, wx.EXPAND)

		self.itemsPanel.SetSizer(self.itemsSizer)
		
		self.initItemButtons()
		
		self.initItemList()
		self.loadItemList()

		self.initItemDetails()
		self.loadItemDetails()

		self.initItemUsage()
		self.loadItemUsage()

		self.initItemObtaining()
		self.loadItemObtaining()


	def initItemButtons(self):
		self.itemsButton = wx.Button(self.itemsPanel, label="Items", name="items")
		self.itemsButton.SetBitmap(wx.Bitmap("images/unknown.png"))
		self.materialsButton = wx.Button(self.itemsPanel, label="Materials", name="materials")
		self.materialsButton.SetBitmap(wx.Bitmap("images/unknown.png"))
		self.ammoButton = wx.Button(self.itemsPanel, label="Ammo", name="ammo")
		self.ammoButton.SetBitmap(wx.Bitmap("images/unknown.png"))
		self.miscButton = wx.Button(self.itemsPanel, label="Misc.", name="misc")
		self.miscButton.SetBitmap(wx.Bitmap("images/unknown.png"))

		self.itemsButton.Bind(wx.EVT_BUTTON, self.onItemTypeSelection)
		self.materialsButton.Bind(wx.EVT_BUTTON, self.onItemTypeSelection)
		self.ammoButton.Bind(wx.EVT_BUTTON, self.onItemTypeSelection)
		self.miscButton.Bind(wx.EVT_BUTTON, self.onItemTypeSelection)
	
		self.itemButtonsSizer = wx.BoxSizer(wx.HORIZONTAL)

		self.itemButtonsSizer.Add(self.itemsButton)
		self.itemButtonsSizer.Add(self.materialsButton)
		self.itemButtonsSizer.Add(self.ammoButton)
		self.itemButtonsSizer.Add(self.miscButton)

		self.itemListSizer.Add(self.itemButtonsSizer)


	def initItemList(self):
		pass


	def loadItemList(self):
		pass

	def initItemDetails(self):
		pass

	def loadItemDetails(self):
		pass

	def initItemUsage(self):
		pass

	def loadItemUsage(self):
		pass

	def initItemObtaining(self):
		pass

	def loadItemObtaining(self):
		pass


	def onItemTypeSelection(self, event):
		"""
		When an armor rank button at the top of the screen is pressed the armor tree is reloaded with the new armor rank information.
		"""

		"""self.currentitemList = event.GetEventObject().GetName()
		self.itemList.DeleteAllItems()
		self.loaditemList()"""


	def onItemSelection(self, event):
		"""
		When a specific armor piece is selected in the tree, the detail view gets populated with the information from the database.
		"""


	def onSize(self, event):
		"""
		When the application window is resized some columns's width gets readjusted.
		"""
		
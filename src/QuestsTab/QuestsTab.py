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

import Utilities as util
from Debug import debug
import QuestsTab as q

wxTreeListItem = NewType('wxTreeListItem', None)

class QuestsTab:

	def __init__(self, root, mainNotebook, link):
		self.root = root
		self.mainNotebook = mainNotebook
		self.init = True

		self.currentlySelectedQuestID = 0
		self.testIcon = wx.Bitmap("images/unknown.png", wx.BITMAP_TYPE_ANY)

		self.initQuestsTab()


	def initQuestsTab(self):
		self.questPanel = wx.Panel(self.mainNotebook)
		self.mainNotebook.AddPage(self.questPanel, "Quests")
		self.questSizer = wx.BoxSizer(wx.HORIZONTAL)

		self.questTreeSizer = wx.BoxSizer(wx.VERTICAL) 
		
		self.questDetailedSizer = wx.BoxSizer(wx.VERTICAL)
		questImage = wx.Bitmap("images/kinsects/Culldrone I.jpg", wx.BITMAP_TYPE_ANY)
		self.questImageLabel = wx.StaticBitmap(self.questPanel, bitmap=questImage, size=(160, 160))
		#self.questImageLabel.SetBackgroundColour((0, 0, 0))

		self.questDetailsNotebook = wx.Notebook(self.questPanel)
		self.questDetailPanel = wx.ScrolledWindow(self.questDetailsNotebook)
		
		self.questDetailSizer = wx.BoxSizer(wx.VERTICAL)
		self.questDetailsNotebook.AddPage(self.questDetailPanel, "Detail")
		self.questDetailPanel.SetSizer(self.questDetailSizer)

		self.questDetailedImagesSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.questDetailedImagesSizer.Add(self.questImageLabel, 1, wx.ALIGN_CENTER)
		
		self.questDetailedSizer.Add(self.questDetailedImagesSizer, 1, wx.EXPAND)
		self.questDetailedSizer.Add(self.questDetailsNotebook, 3, wx.EXPAND)

		self.questSizer.Add(self.questTreeSizer, 0, wx.EXPAND)
		self.questSizer.Add(self.questDetailedSizer, 1, wx.EXPAND)

		self.questPanel.SetSizer(self.questSizer)

		self.initQuestButtons()
		self.initSearch()
		self.initQuestTree()
		#self.initQuestDetailTab()

		#self.questDetailList.Bind(wx.EVT_SIZE, self.onSize)

		#self.questDetailPanel.SetScrollRate(20, 20)


	def initQuestButtons(self):
		weapons = ["assigned", "optional", "event", "special", "arena"]

		self.questButtonsSizer = wx.BoxSizer(wx.HORIZONTAL)
		for i, item in enumerate(weapons):
			button = wx.Button(self.questPanel, label=item.capitalize(), name=item)
			button.SetBitmap(wx.Bitmap(f"images/unknown.png"))
			self.questButtonsSizer.Add(button)
			#button.Bind(wx.EVT_BUTTON, self.onQuestTypeSelection)

		self.questTreeSizer.Add(self.questButtonsSizer)


	def initSearch(self):
		self.search = wx.TextCtrl(self.questPanel)
		self.search.SetHint("  search by name")
		self.search.Bind(wx.EVT_TEXT, self.onSearchTextEnter)
		self.questButtonsSizer.Add(150, 0, 0)
		self.questButtonsSizer.Add(self.search, 0, wx.ALIGN_CENTER_VERTICAL)


	def onSearchTextEnter(self, event):
		self.loadQuestTree()


	def initQuestTree(self):
		self.questTree = cgr.HeaderBitmapGrid(self.questPanel)
		self.questTree.EnableEditing(False)
		self.questTree.EnableDragRowSize(False)
		#self.questTree.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.onQuestSelection)
		self.questTreeSizer.Add(self.questTree, 1, wx.EXPAND)

		questTreeColumns = {
			"Name": [200, None],
			"Attack Type": [45, wx.Bitmap("images/weapon-detail-24/attacktype.png")],
			"Dust Effect": [57, wx.Bitmap("images/weapon-detail-24/dusteffect.png")],
			"Power": [35, wx.Bitmap("images/weapon-detail-24/power.png")],
			"Speed": [35, wx.Bitmap("images/weapon-detail-24/speed.png")],
			"Heal": [35, wx.Bitmap("images/weapon-detail-24/heal.png")],
			"id": [0,  None],
		}

		self.questTree.CreateGrid(1, len(questTreeColumns))
		self.questTree.SetDefaultRowSize(27, resizeExistingRows=True)
		self.questTree.HideRowLabels()
		self.questTree.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)

		for col, (k, v) in enumerate(questTreeColumns.items()):
			if v[1] == None:
				self.questTree.SetColLabelValue(col, k)
			else:
				self.questTree.SetColLabelRenderer(col, cgr.HeaderBitmapColLabelRenderer(v[1], ""))
			self.questTree.SetColSize(col, v[0])

		self.loadQuestTree()


	def loadQuestTree(self):
		self.init = True
		try:
			self.questTree.DeleteRows(0, self.questTree.GetNumberRows())
		except:
			pass
		self.init = False

import wx
import sys

import Debug as debug

class DebugWindow:

	def __init__(self, root):
		self.win = wx.Frame(root, title="Debug", style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
		self.win.SetIcon(wx.Icon("images/Nergigante.png"))
		self.win.SetSize(400, root.GetSize()[1])
		dis = wx.Display()
		if dis.GetCount() == 1:
			if dis.GetGeometry()[0] < 2560:
				self.win.Center()
		else:
			self.win.SetPosition((root.GetPosition()[0] - 385, root.GetPosition()[1]))
		self.win.Bind(wx.EVT_CLOSE, self.onClose)

		panel = wx.Panel(self.win)
		sizer = wx.BoxSizer()
		self.text = wx.TextCtrl(panel, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP)
		sizer.Add(self.text, 1, wx.EXPAND)
		panel.SetSizer(sizer)

		wx.Log.SetActiveTarget(wx.LogTextCtrl(self.text))
		redir=debug.RedirectText(self.text)
		sys.stdout=redir
		sys.stderr=redir

		self.makeMenuBar()

		self.win.Show()


	def makeMenuBar(self):
		fileMenu = wx.Menu()
		clearItem = fileMenu.Append(-1, "Clear", "Clears the debug log, deleting its previous contents.")
		saveAsItem = fileMenu.Append(-1, "&Save As...\tCtrl-S", "Saves the debug log as self.text file.")
		closeItem = fileMenu.Append(-1, "&Close\tCtrl-D", "Closes the debug window.")
		
		menuBar = wx.MenuBar()
		menuBar.Append(fileMenu, "&File")

		self.win.SetMenuBar(menuBar)

		self.win.Bind(wx.EVT_MENU, self.onClear,  clearItem)
		self.win.Bind(wx.EVT_MENU, self.onSaveAs, saveAsItem)
		self.win.Bind(wx.EVT_MENU, self.onClose, closeItem)


	def onClear(self, event):
		self.text.SetValue("")

	
	def onSaveAs(self, event):
		with wx.FileDialog(self.win, "Save As...", wildcard="Text files (*.txt)|*.txt",
						style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

			if fileDialog.ShowModal() == wx.ID_CANCEL:
				return     

			pathname = fileDialog.GetPath()
			try:
				with open(pathname, 'w') as file:
					file.write(self.text.GetValue())
			except IOError:
				wx.LogError("Cannot save current data in file '%s'." % pathname)


	def onClose(self, event):
		wx.Log.SetActiveTarget(None)
		sys.stdout=sys.__stdout__
		sys.stderr=sys.__stderr__
		self.win.Destroy()
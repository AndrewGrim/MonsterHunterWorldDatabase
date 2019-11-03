import wx
import sys

import Debug as debug

class DebugWindow:

	def __init__(self, root):
		self.win = wx.Frame(root, title="Debug", style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
		self.win.SetIcon(wx.Icon("images/Nergigante.png"))
		self.win.SetSize(400, root.GetSize()[1])
		self.win.SetPosition((root.GetPosition()[0] - 385, root.GetPosition()[1]))
		self.win.Bind(wx.EVT_CLOSE, self.onClose)

		panel = wx.Panel(self.win)
		sizer = wx.BoxSizer()
		text = wx.TextCtrl(panel, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP)
		sizer.Add(text, 1, wx.EXPAND)
		panel.SetSizer(sizer)
		self.win.Show()

		wx.Log.SetActiveTarget(wx.LogTextCtrl(text))
		redir=debug.RedirectText(text)
		sys.stdout=redir
		sys.stderr=redir


	def onClose(self, event):
		wx.Log.SetActiveTarget(None)
		sys.stdout=sys.__stdout__
		sys.stderr=sys.__stderr__
		self.win.Destroy()
import wx

class LoadingWindow:

	def __init__(self, root):
		self.root = root

		self.win = wx.Frame(root, title="Loading", style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
		self.win.SetIcon(wx.Icon("images/Nergigante.png"))
		self.win.SetSize(300, 80)
		self.win.Center()

		panel = wx.Panel(self.win)
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.loading = wx.Gauge(panel)
		self.loading.SetValue(0)
		sizer.Add(self.loading, 3, wx.EXPAND)
		panel.SetSizer(sizer)

		self.win.Show()
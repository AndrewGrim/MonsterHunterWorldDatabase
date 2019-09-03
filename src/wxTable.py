"""
Hello World, but with more meat.
"""

import wx
import wx.grid

class HelloFrame(wx.Frame): # frame would be a tk window
	"""
	A Frame that says Hello World
	"""

	def __init__(self, *args, **kw):
		# ensure the parent's __init__ is called
		super(HelloFrame, self).__init__(*args, **kw)

		# create a panel in the frame
		pnl = wx.Panel(self) # or frame in tk

		# put some text with a larger bold font on it
		#st = wx.StaticText(pnl, label="Hello World!") # static text ie label
		#font = st.GetFont()
		#font.PointSize += 10
		#font = font.Bold()
		#st.SetFont(font)

		# grid table
		table = wx.grid.Grid(pnl)
		table.CreateGrid(100, 10)
		table.SetRowSize(0, 60) # row index 0, width 60 something
		table.SetColSize(0, 120)
		table.SetCellValue(0, 0, "wxGrid is dope")
		#table.SetReadOnly(0, 0)
		table.SetCellTextColour(0, 0, wx.BLUE)
		table.SetCellBackgroundColour(0, 0, wx.YELLOW)
		table.SetColFormatFloat(5, 6, 2) # width 6, precision 2
		table.SetCellValue(0, 1, "3.1415")

		# and create a sizer to manage the layout of child widgets
		sizer = wx.BoxSizer(wx.VERTICAL)
		#sizer.Add(st, wx.SizerFlags().Border(wx.TOP|wx.LEFT, 25))
		sizer.Add(table)
		pnl.SetSizer(sizer)

		# create a menu bar
		self.makeMenuBar()

		# and a status bar
		self.CreateStatusBar()
		self.SetStatusText("Welcome to wxPython!")


	def makeMenuBar(self):
		"""
		A menu bar is composed of menus, which are composed of menu items.
		This method builds a set of menus and binds handlers to be called
		when the menu item is selected.
		"""

		# Make a file menu with Hello and Exit items
		fileMenu = wx.Menu()
		# The "\t..." syntax defines an accelerator key that also triggers
		# the same event
		helloItem = fileMenu.Append(-1, "&Hello...\tCtrl-H",
				"Help string shown in status bar for this menu item")
		fileMenu.AppendSeparator()
		# When using a stock ID we don't need to specify the menu item's
		# label
		exitItem = fileMenu.Append(wx.ID_EXIT)

		# Now a help menu for the about item
		helpMenu = wx.Menu()
		aboutItem = helpMenu.Append(wx.ID_ABOUT)

		# Make the menu bar and add the two menus to it. The '&' defines
		# that the next letter is the "mnemonic" for the menu item. On the
		# platforms that support it those letters are underlined and can be
		# triggered from the keyboard.
		menuBar = wx.MenuBar()
		menuBar.Append(fileMenu, "&File")
		menuBar.Append(helpMenu, "&Help")

		# Give the menu bar to the frame
		self.SetMenuBar(menuBar)

		# Finally, associate a handler function with the EVT_MENU event for
		# each of the menu items. That means that when that menu item is
		# activated then the associated handler function will be called.
		self.Bind(wx.EVT_MENU, self.OnHello, helloItem)
		self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)
		self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)


	def OnExit(self, event):
		"""Close the frame, terminating the application."""
		self.Close(True)


	def OnHello(self, event):
		"""Say hello to the user."""
		wx.MessageBox("Hello again from wxPython")


	def OnAbout(self, event):
		"""Display an About Dialog"""
		wx.MessageBox("This is a wxPython Hello World sample",
					  "About Hello World 2",
					  wx.OK|wx.ICON_INFORMATION)


if __name__ == '__main__':
	# When this module is run (not imported) then create the app, the
	# frame, show it, and start the event loop.
	app = wx.App()
	frm = HelloFrame(None, title='Hello World 2')
	frm.Show()
	app.MainLoop()
import wx.html
import webbrowser

class AboutWindow:

	def __init__(self, root):
		self.root = root

		self.win = wx.Frame(root, title="About", style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
		self.win.SetIcon(wx.Icon("images/Nergigante.png"))
		self.win.SetSize(700, 700)
		self.win.Center()

		panel = wx.Panel(self.win)
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.about = wx.html.HtmlWindow(panel, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.BORDER_NONE)
		self.about.Bind(wx.html.EVT_HTML_LINK_CLICKED, self.onURL)
		self.license = wx.TextCtrl(panel, style=wx.TE_MULTILINE|wx.TE_READONLY)
		sizer.Add(self.about, 1, wx.EXPAND)
		sizer.Add(self.license, 3, wx.EXPAND)
		panel.SetSizer(sizer)

		self.setAboutText()
		self.setLicenseText()

		self.win.Show()


	def onURL(self, event):
		link = event.GetLinkInfo()
		webbrowser.open(link.GetHref())


	def setAboutText(self):
		aboutText = """
<p>
	Created by <a href="https://github.com/AndrewGrim">AndrewGrim</a>.
</p>
<p>
This application uses the database and images from <a href="https://github.com/gatheringhallstudios">gatheringhallstudios</a> 
as well as some of their SQL queries and their sharpness adjust function.
</p>
<p>
	<a href="https://github.com/AndrewGrim/MonsterHunterWorldDatabase">https://github.com/AndrewGrim/MonsterHunterWorldDatabase</a><br/>
	<a href="https://github.com/gatheringhallstudios/MHWorldDatabase">https://github.com/gatheringhallstudios/MHWorldDatabase</a><br/>
	<a href="https://github.com/gatheringhallstudios/MHWorldData">https://github.com/gatheringhallstudios/MHWorldData</a>
</p>"""
		self.about.SetPage(aboutText)

	
	def setLicenseText(self):
		licenseText = """
MIT License

Copyright (c) 2019 Andrew Grim

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

==============================================================================

The MIT License (MIT)

Copyright (c) 2018 Gathering Hall Studios

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

==============================================================================

MIT License

Copyright (c) 2018 Carlos Fernandez

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""
		
		self.license.SetValue(licenseText)
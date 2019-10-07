import wx
import wx.lib.mixins.gridlabelrenderer as glr


class HeaderBitmapGrid(wx.grid.Grid, glr.GridWithLabelRenderersMixin):
	def __init__(self, *args, **kw):
		wx.grid.Grid.__init__(self, *args, **kw)
		glr.GridWithLabelRenderersMixin.__init__(self)


class ImageTextCellRenderer(wx.grid.GridCellRenderer):
	"""
	img = bitmap
	label = ""
	colour = (r,g,b)
	selectedColour = (r,g,b)
	"""
	def __init__(self, img, label = "", colour = wx.WHITE, selectedColour = wx.BLUE):
		wx.grid.GridCellRenderer.__init__(self)
		self.img = img
		self.colour = colour
		self.selectedColour = selectedColour
		self.label = label


	def Draw(self, grid, attr, dc, rect, row, col, isSelected):
		image = wx.MemoryDC()
		image.SelectObject(self.img)
		dc.SetBackgroundMode(wx.SOLID)
		if isSelected:
			dc.SetBrush(wx.Brush(self.selectedColour, wx.SOLID))
			dc.SetPen(wx.Pen(self.selectedColour, 1, wx.SOLID))
		else:
			dc.SetBrush(wx.Brush(self.colour, wx.SOLID))
			dc.SetPen(wx.Pen(self.colour, 1, wx.SOLID))
		dc.DrawRectangle(rect)
		width, height = self.img.GetWidth(), self.img.GetHeight()
		if width > rect.width-2:
			width = rect.width-2
		if height > rect.height-2:
			height = rect.height-2
		#dc.Blit(rect.x+1, rect.y+1, width, height, image, 0, 0, wx.COPY, True)
		x = rect.left + (rect.width - self.img.GetWidth()) / 2
		y = rect.top + (rect.height - self.img.GetHeight()) / 2
		dc.DrawBitmap(self.img, x - 50, y, True)
		self.DrawText(grid, dc, rect, self.label, wx.ALIGN_CENTER, wx.ALIGN_CENTER)


	def DrawText(self, grid, dc, rect, text, hAlign, vAlign):
		dc.SetBackgroundMode(wx.TRANSPARENT)
		dc.SetTextForeground(grid.GetLabelTextColour())
		dc.SetFont(grid.GetDefaultCellFont())
		rect = wx.Rect(*rect)
		rect.Deflate(2,2)
		grid.DrawTextRectangle(dc, text, rect, wx.ALIGN_CENTER, wx.ALIGN_CENTER)


class ImageCellRenderer(wx.grid.GridCellRenderer):
	"""
	img = bitmap
	colour = (r,g,b)
	selectedColour = (r,g,b)
	"""
	def __init__(self, img, colour = wx.WHITE, selectedColour = wx.BLUE):
		wx.grid.GridCellRenderer.__init__(self)
		self.img = img
		self.colour = colour
		self.selectedColour = selectedColour


	def Draw(self, grid, attr, dc, rect, row, col, isSelected):
		image = wx.MemoryDC()
		image.SelectObject(self.img)
		dc.SetBackgroundMode(wx.SOLID)
		if isSelected:
			dc.SetBrush(wx.Brush(self.selectedColour, wx.SOLID))
			dc.SetPen(wx.Pen(self.selectedColour, 1, wx.SOLID))
		else:
			dc.SetBrush(wx.Brush(self.colour, wx.SOLID))
			dc.SetPen(wx.Pen(self.colour, 1, wx.SOLID))
		dc.DrawRectangle(rect)
		width, height = self.img.GetWidth(), self.img.GetHeight()
		if width > rect.width-2:
			width = rect.width-2
		if height > rect.height-2:
			height = rect.height-2
		dc.Blit(rect.x+1, rect.y+1, width, height, image, 0, 0, wx.COPY, True)


class HeaderBitmapRowLabelRenderer(glr.GridLabelRenderer):

	def __init__(self, bgcolor):
		self._bgcolor = bgcolor


	def Draw(self, grid, dc, rect, row):
		dc.SetBrush(wx.Brush(self._bgcolor))
		dc.SetPen(wx.TRANSPARENT_PEN)
		dc.DrawRectangle(rect)
		hAlign, vAlign = wx.grid.GetRowLabelAlignment()
		text = wx.grid.GetRowLabelValue(row)
		self.DrawBorder(wx.grid, dc, rect)
		self.DrawText(wx.grid, dc, rect, text, hAlign, vAlign)


class HeaderBitmapColLabelRenderer(glr.GridLabelRenderer):

	def __init__(self, image, label = "default", imageAlignment = wx.ALIGN_CENTER):
		self._bmp = wx.Bitmap(image, wx.BITMAP_TYPE_ANY)
		self.imgAlign = imageAlignment
		self.label = label


	def Draw(self, grid, dc, rect, col):
		x = rect.left + (rect.width - self._bmp.GetWidth()) / 2
		y = rect.top + (rect.height - self._bmp.GetHeight()) / 2
		self.DrawBorder(grid, dc, rect)
		if self.imgAlign == wx.ALIGN_LEFT:
			dc.DrawBitmap(self._bmp, x - 40, y, True)
		elif self.imgAlign == wx.ALIGN_RIGHT:
			dc.DrawBitmap(self._bmp, x + 40, y, True)
		else:
			dc.DrawBitmap(self._bmp, x, y, True)
		hAlign, vAlign = grid.GetColLabelAlignment()
		if self.label == "default":
			self.DrawText(grid, dc, rect, grid.GetColLabelValue(col), hAlign, vAlign)
		else:
			self.DrawText(grid, dc, rect, self.label, hAlign, vAlign)


class HeaderBitmapCornerLabelRenderer(glr.GridLabelRenderer):

	def __init__(self, image):
		self._bmp = wx.Bitmap(image, wx.BITMAP_TYPE_ANY)


	def Draw(self, grid, dc, rect, rc):
		x = rect.left + (rect.width - self._bmp.GetWidth()) / 2
		y = rect.top + (rect.height - self._bmp.GetHeight()) / 2
		self.DrawBorder(grid, dc, rect)
		dc.DrawBitmap(self._bmp, x, y, True)
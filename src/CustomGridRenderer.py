import wx
import wx.lib.mixins.gridlabelrenderer as glr


class HeaderBitmapGrid(wx.grid.Grid, glr.GridWithLabelRenderersMixin):
	def __init__(self, *args, **kw):
		wx.grid.Grid.__init__(self, *args, **kw)
		glr.GridWithLabelRenderersMixin.__init__(self)


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
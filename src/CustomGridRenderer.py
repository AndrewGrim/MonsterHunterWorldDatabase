import wx
import wx.lib.mixins.gridlabelrenderer as glr

from typing import List
from typing import Union
from typing import Tuple
from typing import Dict
from typing import NewType

wxBitmap = NewType('wx.Bitmap()', None)
wxColour = NewType('wx.Colour()', None)
wxAlignment = NewType('wx.Alignment: Enum', None)
wxFont = NewType('wx.Font()', None)


class HeaderBitmapGrid(wx.grid.Grid, glr.GridWithLabelRenderersMixin):
	def __init__(self, *args, **kw):
		wx.grid.Grid.__init__(self, *args, **kw)
		glr.GridWithLabelRenderersMixin.__init__(self)


class ImageTextCellRenderer(wx.grid.GridCellRenderer):
	"""
	A custom cell renderer for drawing both an image and text.
	"""

	def __init__(self, img: wxBitmap, label = "", colour: wxColour = None, selectedColour: wxColour = None,
		autoImageOffset: bool = False, imageOffset: int = 50, hAlign: wxAlignment = wx.ALIGN_CENTER, font: wxFont = None) -> None:
		"""
		Args:\n
			img: wxBitmap = An image to draw as a wx.Bitmap().
			label: str = A text label to draw. Default is an empty string "".
			colour: wxColour or Tuple[int, int, int] = The background colour to draw in RGB. Default is derived from the system.
			selectedColour: wxColour or Tuple[int, int, int] = The background colour while selected to draw in RGB. Default is derived from the system.
			autoImageOffset: bool = Determine the imageOffset by using GetFullTextExtent(). Does not work very well. Default is False.
			imageOffset: int = The pixel offset of the img from the center of the cell. Gets overwritten when autoImageOffset is True. Default is 50.
			hAlign: wxAlignment = A wx.Alignment enumeration which specifies the text alignment. Left, right or center.
			font: wxFont = The font to be used by the label.

		Returns:\n
			None
		"""
		wx.grid.GridCellRenderer.__init__(self)
		self.img = img
		if colour == None:
			colour = wx.SystemSettings().GetColour(wx.SYS_COLOUR_WINDOW)
		self.colour = colour
		if selectedColour == None:
			selectedColour = wx.SystemSettings().GetColour(wx.SYS_COLOUR_HIGHLIGHT)
		self.selectedColour = selectedColour
		self.label = label
		self.autoImageOffset = autoImageOffset
		self.imageOffset = imageOffset
		self.hAlign = hAlign
		self.font = font


	def Draw(self, grid, attr, dc, rect, row, col, isSelected):
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
		x = rect.left + (rect.width - self.img.GetWidth()) / 2
		y = rect.top + (rect.height - self.img.GetHeight()) / 2
		if self.autoImageOffset:
			self.imageOffset = dc.GetFullTextExtent(self.label)
			dc.DrawBitmap(self.img, x - self.imageOffset[0], y, True)
		else:
			dc.DrawBitmap(self.img, x - self.imageOffset, y, True)
		self.DrawText(grid, dc, rect, self.label, self.hAlign, wx.ALIGN_CENTER)


	def DrawText(self, grid, dc, rect, text, hAlign, vAlign):
		dc.SetBackgroundMode(wx.TRANSPARENT)
		dc.SetTextForeground(grid.GetLabelTextColour())
		if self.font != None:
			dc.SetFont(self.font)
		else:
			dc.SetFont(grid.GetDefaultCellFont())
		rect = wx.Rect(*rect)
		rect.Deflate(2,2)
		grid.DrawTextRectangle(dc, text, rect, hAlign, wx.ALIGN_CENTER)


	def GetLabel(self):
		return self.label


class ImageCellRenderer(wx.grid.GridCellRenderer):
	"""
	A custom cell renderer for drawing an image.
	"""

	def __init__(self, img, colour = None, selectedColour = None):
		"""
		Args:\n
			img: wxBitmap = An image to draw as a wx.Bitmap().
			colour: wxColour or Tuple[int, int, int] = The background colour to draw in RGB. Default is derived from the system.
			selectedColour: wxColour or Tuple[int, int, int] = The background colour while selected to draw in RGB. Default is derived from the system.

		Returns:\n
			None
		"""

		wx.grid.GridCellRenderer.__init__(self)
		self.img = img
		if colour == None:
			colour = wx.SystemSettings().GetColour(wx.SYS_COLOUR_WINDOW)
		self.colour = colour
		if selectedColour == None:
			selectedColour = wx.SystemSettings().GetColour(wx.SYS_COLOUR_HIGHLIGHT)
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

	def __init__(self, image, label = None, imageAlignment = wx.ALIGN_CENTER):
		self.img = image
		self.imgAlign = imageAlignment
		self.label = label


	def Draw(self, grid, dc, rect, col):
		x = rect.left + (rect.width - self.img.GetWidth()) / 2
		y = rect.top + (rect.height - self.img.GetHeight()) / 2
		self.DrawBorder(grid, dc, rect)
		if self.imgAlign == wx.ALIGN_LEFT:
			dc.DrawBitmap(self.img, x - 40, y, True)
		elif self.imgAlign == wx.ALIGN_RIGHT:
			dc.DrawBitmap(self.img, x + 40, y, True)
		else:
			dc.DrawBitmap(self.img, x, y, True)
		hAlign, vAlign = grid.GetColLabelAlignment()
		if self.label == None:
			self.DrawText(grid, dc, rect, grid.GetColLabelValue(col), hAlign, vAlign)
		else:
			self.DrawText(grid, dc, rect, self.label, hAlign, vAlign)


class HeaderBitmapCornerLabelRenderer(glr.GridLabelRenderer):

	def __init__(self, image):
		self.img = image


	def Draw(self, grid, dc, rect, rc):
		x = rect.left + (rect.width - self.img.GetWidth()) / 2
		y = rect.top + (rect.height - self.img.GetHeight()) / 2
		self.DrawBorder(grid, dc, rect)
		dc.DrawBitmap(self.img, x, y, True)
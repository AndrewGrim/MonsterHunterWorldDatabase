import wx
import os
import sys

def addBorder():
    resizeImages = os.listdir(os.getcwd() + "/images/monsters/resize")
    for img in resizeImages:
        image = wx.Image()
        image.LoadFile("images/monsters/resize/" + img, wx.BITMAP_TYPE_PNG)
        image.Resize(wx.Size(1024, 1024), wx.Point(0, 0))
        image.Resize(wx.Size(650, 650), wx.Point(80, 75))
        image.Rescale(256, 256, wx.IMAGE_QUALITY_HIGH)
        image.SaveFile("images/monsters/256/" + img, wx.BITMAP_TYPE_PNG)


def rescaleTo256():
    originalImages = os.listdir(os.getcwd() + "/images/monsters/original")
    for img in originalImages:
        image = wx.Image()
        image.LoadFile("images/monsters/original/" + img, wx.BITMAP_TYPE_PNG)
        image.Rescale(256, 256, wx.IMAGE_QUALITY_HIGH)
        image.SaveFile("images/monsters/256/" + img, wx.BITMAP_TYPE_PNG)

    
def fixMosswine():
    image = wx.Image()
    image.LoadFile("images/monsters/resize/Mosswine.png", wx.BITMAP_TYPE_PNG)
    image.Resize(wx.Size(1024, 1024), wx.Point(0, 0))
    image.Resize(wx.Size(650, 650), wx.Point(80, 180))
    image.Rescale(256, 256, wx.IMAGE_QUALITY_HIGH)
    image.SaveFile("images/monsters/256/Mosswine.png", wx.BITMAP_TYPE_PNG)


def fixGrimalkyne():
    image = wx.Image()
    image.LoadFile("images/monsters/resize/Grimalkyne.png", wx.BITMAP_TYPE_PNG)
    image.Resize(wx.Size(1024, 1024), wx.Point(0, 0))
    image.Resize(wx.Size(650, 650), wx.Point(145, 60))
    image.Rescale(256, 256, wx.IMAGE_QUALITY_HIGH)
    image.SaveFile("images/monsters/256/Grimalkyne.png", wx.BITMAP_TYPE_PNG)
    

def fixVespoid():
    image = wx.Image()
    image.LoadFile("images/monsters/resize/Vespoid.png", wx.BITMAP_TYPE_PNG)
    image.Resize(wx.Size(1024, 1024), wx.Point(0, 0))
    image.Resize(wx.Size(650, 650), wx.Point(70, 90))
    image.Rescale(256, 256, wx.IMAGE_QUALITY_HIGH)
    image.SaveFile("images/monsters/256/Vespoid.png", wx.BITMAP_TYPE_PNG)
    

def fixGastodon():
    image = wx.Image()
    image.LoadFile("images/monsters/resize/Gastodon.png", wx.BITMAP_TYPE_PNG)
    image.Resize(wx.Size(1024, 1024), wx.Point(0, 0))
    image.Resize(wx.Size(650, 650), wx.Point(55, 80))
    image.Rescale(256, 256, wx.IMAGE_QUALITY_HIGH)
    image.SaveFile("images/monsters/256/Gastodon.png", wx.BITMAP_TYPE_PNG)
    

def rescaleFolder(size):
    folderPath = os.getcwd() + "/" + sys.argv[1]
    originalImages = os.listdir(folderPath)
    for img in originalImages:
        image = wx.Image()
        image.LoadFile(folderPath + "/" + img, wx.BITMAP_TYPE_PNG)
        image.Rescale(int(size), int(size), wx.IMAGE_QUALITY_HIGH)
        image.SaveFile(folderPath + "/" + size + "/" + img, wx.BITMAP_TYPE_PNG)


def rescaleImage(size):
    img = sys.argv[1]
    image = wx.Image()
    image.LoadFile(img, wx.BITMAP_TYPE_PNG)
    image.Rescale(int(size), int(size), wx.IMAGE_QUALITY_HIGH)
    image.SaveFile(img.split(".")[0] + size + ".png", wx.BITMAP_TYPE_PNG)


print(
    """
    Rescale a single image:
        python images.py <pathToImage> <rescaleSize>
    """
    )
#rescaleImage(sys.argv[2])
#rescaleFolder(sys.argv[2])

image = wx.Image()
image.LoadFile("images/monsters/original/Nergigante.png", wx.BITMAP_TYPE_PNG)
#image.SetMaskColour(255, 255, 255)
image.Rescale(325, 325, wx.IMAGE_QUALITY_HIGH)
image.SaveFile("images/monsters/325/Nergigante.png", wx.BITMAP_TYPE_PNG)

"""alpha = os.listdir(os.getcwd() + "/images/VectorDrawable2Svg-master/alpha")
alpha.remove("trans")
for img in alpha:
    image = wx.Image()
    image.LoadFile("images/VectorDrawable2Svg-master/alpha/" + img, wx.BITMAP_TYPE_PNG)
    image.SetMaskColour(255, 255, 255)
    image.Rescale(32, 32, wx.IMAGE_QUALITY_HIGH)
    image.SaveFile("images/VectorDrawable2Svg-master/alpha/trans/" + img, wx.BITMAP_TYPE_PNG)"""
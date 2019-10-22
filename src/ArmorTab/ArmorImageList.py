import wx

class ArmorImageList:

	def __init__(self):
		size = (24, 24)
		self.il = wx.ImageList(size[0], size[1])

		self.test = self.il.Add(wx.Bitmap("images/unknown.png", wx.BITMAP_TYPE_ANY))

		# TODO make this into a dict?? and have one for each of the armor pieces and the armor set icons, but also make them
		self.armorSet0 = self.il.Add(wx.Bitmap("images/armor/armorset/rarity-24/0.png", wx.BITMAP_TYPE_ANY))
		self.armorSet1 = self.il.Add(wx.Bitmap("images/armor/armorset/rarity-24/1.png", wx.BITMAP_TYPE_ANY))
		self.armorSet2 = self.il.Add(wx.Bitmap("images/armor/armorset/rarity-24/2.png", wx.BITMAP_TYPE_ANY))
		self.armorSet3 = self.il.Add(wx.Bitmap("images/armor/armorset/rarity-24/3.png", wx.BITMAP_TYPE_ANY))
		self.armorSet4 = self.il.Add(wx.Bitmap("images/armor/armorset/rarity-24/4.png", wx.BITMAP_TYPE_ANY))
		self.armorSet5 = self.il.Add(wx.Bitmap("images/armor/armorset/rarity-24/5.png", wx.BITMAP_TYPE_ANY))
		self.armorSet6 = self.il.Add(wx.Bitmap("images/armor/armorset/rarity-24/6.png", wx.BITMAP_TYPE_ANY))
		self.armorSet7 = self.il.Add(wx.Bitmap("images/armor/armorset/rarity-24/7.png", wx.BITMAP_TYPE_ANY))
		self.armorSet8 = self.il.Add(wx.Bitmap("images/armor/armorset/rarity-24/8.png", wx.BITMAP_TYPE_ANY))

		self.head0 = self.il.Add(wx.Bitmap("images/armor/head/rarity-24/0.png", wx.BITMAP_TYPE_ANY))
		self.head1 = self.il.Add(wx.Bitmap("images/armor/head/rarity-24/1.png", wx.BITMAP_TYPE_ANY))
		self.head2 = self.il.Add(wx.Bitmap("images/armor/head/rarity-24/2.png", wx.BITMAP_TYPE_ANY))
		self.head3 = self.il.Add(wx.Bitmap("images/armor/head/rarity-24/3.png", wx.BITMAP_TYPE_ANY))
		self.head4 = self.il.Add(wx.Bitmap("images/armor/head/rarity-24/4.png", wx.BITMAP_TYPE_ANY))
		self.head5 = self.il.Add(wx.Bitmap("images/armor/head/rarity-24/5.png", wx.BITMAP_TYPE_ANY))
		self.head6 = self.il.Add(wx.Bitmap("images/armor/head/rarity-24/6.png", wx.BITMAP_TYPE_ANY))
		self.head7 = self.il.Add(wx.Bitmap("images/armor/head/rarity-24/7.png", wx.BITMAP_TYPE_ANY))
		self.head8 = self.il.Add(wx.Bitmap("images/armor/head/rarity-24/8.png", wx.BITMAP_TYPE_ANY))

		self.chest0 = self.il.Add(wx.Bitmap("images/armor/chest/rarity-24/0.png", wx.BITMAP_TYPE_ANY))
		self.chest1 = self.il.Add(wx.Bitmap("images/armor/chest/rarity-24/1.png", wx.BITMAP_TYPE_ANY))
		self.chest2 = self.il.Add(wx.Bitmap("images/armor/chest/rarity-24/2.png", wx.BITMAP_TYPE_ANY))
		self.chest3 = self.il.Add(wx.Bitmap("images/armor/chest/rarity-24/3.png", wx.BITMAP_TYPE_ANY))
		self.chest4 = self.il.Add(wx.Bitmap("images/armor/chest/rarity-24/4.png", wx.BITMAP_TYPE_ANY))
		self.chest5 = self.il.Add(wx.Bitmap("images/armor/chest/rarity-24/5.png", wx.BITMAP_TYPE_ANY))
		self.chest6 = self.il.Add(wx.Bitmap("images/armor/chest/rarity-24/6.png", wx.BITMAP_TYPE_ANY))
		self.chest7 = self.il.Add(wx.Bitmap("images/armor/chest/rarity-24/7.png", wx.BITMAP_TYPE_ANY))
		self.chest8 = self.il.Add(wx.Bitmap("images/armor/chest/rarity-24/8.png", wx.BITMAP_TYPE_ANY))

		self.arms0 = self.il.Add(wx.Bitmap("images/armor/arms/rarity-24/0.png", wx.BITMAP_TYPE_ANY))
		self.arms1 = self.il.Add(wx.Bitmap("images/armor/arms/rarity-24/1.png", wx.BITMAP_TYPE_ANY))
		self.arms2 = self.il.Add(wx.Bitmap("images/armor/arms/rarity-24/2.png", wx.BITMAP_TYPE_ANY))
		self.arms3 = self.il.Add(wx.Bitmap("images/armor/arms/rarity-24/3.png", wx.BITMAP_TYPE_ANY))
		self.arms4 = self.il.Add(wx.Bitmap("images/armor/arms/rarity-24/4.png", wx.BITMAP_TYPE_ANY))
		self.arms5 = self.il.Add(wx.Bitmap("images/armor/arms/rarity-24/5.png", wx.BITMAP_TYPE_ANY))
		self.arms6 = self.il.Add(wx.Bitmap("images/armor/arms/rarity-24/6.png", wx.BITMAP_TYPE_ANY))
		self.arms7 = self.il.Add(wx.Bitmap("images/armor/arms/rarity-24/7.png", wx.BITMAP_TYPE_ANY))
		self.arms8 = self.il.Add(wx.Bitmap("images/armor/arms/rarity-24/8.png", wx.BITMAP_TYPE_ANY))

		self.waist0 = self.il.Add(wx.Bitmap("images/armor/waist/rarity-24/0.png", wx.BITMAP_TYPE_ANY))
		self.waist1 = self.il.Add(wx.Bitmap("images/armor/waist/rarity-24/1.png", wx.BITMAP_TYPE_ANY))
		self.waist2 = self.il.Add(wx.Bitmap("images/armor/waist/rarity-24/2.png", wx.BITMAP_TYPE_ANY))
		self.waist3 = self.il.Add(wx.Bitmap("images/armor/waist/rarity-24/3.png", wx.BITMAP_TYPE_ANY))
		self.waist4 = self.il.Add(wx.Bitmap("images/armor/waist/rarity-24/4.png", wx.BITMAP_TYPE_ANY))
		self.waist5 = self.il.Add(wx.Bitmap("images/armor/waist/rarity-24/5.png", wx.BITMAP_TYPE_ANY))
		self.waist6 = self.il.Add(wx.Bitmap("images/armor/waist/rarity-24/6.png", wx.BITMAP_TYPE_ANY))
		self.waist7 = self.il.Add(wx.Bitmap("images/armor/waist/rarity-24/7.png", wx.BITMAP_TYPE_ANY))
		self.waist8 = self.il.Add(wx.Bitmap("images/armor/waist/rarity-24/8.png", wx.BITMAP_TYPE_ANY))

		self.legs0 = self.il.Add(wx.Bitmap("images/armor/legs/rarity-24/0.png", wx.BITMAP_TYPE_ANY))
		self.legs1 = self.il.Add(wx.Bitmap("images/armor/legs/rarity-24/1.png", wx.BITMAP_TYPE_ANY))
		self.legs2 = self.il.Add(wx.Bitmap("images/armor/legs/rarity-24/2.png", wx.BITMAP_TYPE_ANY))
		self.legs3 = self.il.Add(wx.Bitmap("images/armor/legs/rarity-24/3.png", wx.BITMAP_TYPE_ANY))
		self.legs4 = self.il.Add(wx.Bitmap("images/armor/legs/rarity-24/4.png", wx.BITMAP_TYPE_ANY))
		self.legs5 = self.il.Add(wx.Bitmap("images/armor/legs/rarity-24/5.png", wx.BITMAP_TYPE_ANY))
		self.legs6 = self.il.Add(wx.Bitmap("images/armor/legs/rarity-24/6.png", wx.BITMAP_TYPE_ANY))
		self.legs7 = self.il.Add(wx.Bitmap("images/armor/legs/rarity-24/7.png", wx.BITMAP_TYPE_ANY))
		self.legs8 = self.il.Add(wx.Bitmap("images/armor/legs/rarity-24/8.png", wx.BITMAP_TYPE_ANY))
		
		self.armorIcons = {
			"armorset": [
						self.armorSet0,
						self.armorSet1,
						self.armorSet2,
						self.armorSet3,
						self.armorSet4,
						self.armorSet5,
						self.armorSet6,
						self.armorSet7,
						self.armorSet8,
						],

			"head": [
						self.head0,
						self.head1,
						self.head2,
						self.head3,
						self.head4,
						self.head5,
						self.head6,
						self.head7,
						self.head8,
						],

			"chest": [
						self.chest0,
						self.chest1,
						self.chest2,
						self.chest3,
						self.chest4,
						self.chest5,
						self.chest6,
						self.chest7,
						self.chest8,
						],

			"arms": [
						self.arms0,
						self.arms1,
						self.arms2,
						self.arms3,
						self.arms4,
						self.arms5,
						self.arms6,
						self.arms7,
						self.arms8,
						],

			"waist": [
						self.waist0,
						self.waist1,
						self.waist2,
						self.waist3,
						self.waist4,
						self.waist5,
						self.waist6,
						self.waist7,
						self.waist8,
						],

			"legs": [
						self.legs0,
						self.legs1,
						self.legs2,
						self.legs3,
						self.legs4,
						self.legs5,
						self.legs6,
						self.legs7,
						self.legs8,
						],
		}
		
		# TODO iceborne
		#self.rarity9 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/9.png", wx.BITMAP_TYPE_ANY))
		#self.rarity10 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/10.png", wx.BITMAP_TYPE_ANY))
		#self.rarity11 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/11.png", wx.BITMAP_TYPE_ANY))
		#self.rarity12 = self.il.Add(wx.Bitmap("images/weapons/" + self.currentWeaponTree + "/rarity-24/12.png", wx.BITMAP_TYPE_ANY))

		self.slots = self.il.Add(wx.Bitmap("images/weapon-detail-24/slots.png", wx.BITMAP_TYPE_ANY))
		self.slots1 = self.il.Add(wx.Bitmap("images/decoration-slots-24/1.png", wx.BITMAP_TYPE_ANY))
		self.slots2 = self.il.Add(wx.Bitmap("images/decoration-slots-24/2.png", wx.BITMAP_TYPE_ANY))
		self.slots3 = self.il.Add(wx.Bitmap("images/decoration-slots-24/3.png", wx.BITMAP_TYPE_ANY))

		self.slotIcons = {
			0: self.slots,
			1: self.slots1,
			2: self.slots2,
			3: self.slots3,
		}

		self.decorationSize = {
			1: wx.Bitmap("images/decoration-slots-24/1.png", wx.BITMAP_TYPE_ANY),
			2: wx.Bitmap("images/decoration-slots-24/2.png", wx.BITMAP_TYPE_ANY),
			3: wx.Bitmap("images/decoration-slots-24/3.png", wx.BITMAP_TYPE_ANY),
		}

		self.fire = self.il.Add(wx.Bitmap("images/damage-types-24/fire.png"))
		self.water = self.il.Add(wx.Bitmap("images/damage-types-24/water.png"))
		self.ice = self.il.Add(wx.Bitmap("images/damage-types-24/ice.png"))
		self.thunder = self.il.Add(wx.Bitmap("images/damage-types-24/thunder.png"))
		self.dragon = self.il.Add(wx.Bitmap("images/damage-types-24/dragon.png"))

		self.elementIcons = {
			"Fire": self.fire,
			"Water": self.water,
			"Ice": self.ice,
			"Thunder": self.thunder,
			"Dragon": self.dragon,
		}

		self.defense = self.il.Add(wx.Bitmap("images/weapon-detail-24/defense.png", wx.BITMAP_TYPE_ANY))
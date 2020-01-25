from PIL import Image

img = Image.open('BLOCK031.png')
print(img.size)

orb_width = 100
spacer = 4

x = 0
y = 0
fire = img.crop(box=(x, y, x + orb_width, y + orb_width))

x += orb_width
x += spacer
water = img.crop(box=(x, y, x + orb_width, y + orb_width))

x += orb_width
x += spacer
wood = img.crop(box=(x, y, x + orb_width, y + orb_width))

x += orb_width
x += spacer
light = img.crop(box=(x, y, x + orb_width, y + orb_width))

y += orb_width
y += spacer
x = 0
dark = img.crop(box=(x, y, x + orb_width, y + orb_width))

fire.save('fire.png')
water.save('water.png')
wood.save('wood.png')
light.save('light.png')
dark.save('dark.png')

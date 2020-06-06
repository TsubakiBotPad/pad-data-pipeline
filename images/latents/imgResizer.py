"""

Running "python3 imgResizer.py" will use all .png files in the same directory. 
Running "python3 imgResizer.py file1 file2 file3 ..." will use those files only 
    (it'll automatically add the .png extension)

If there are any output image files, they will be saved in ./out

Use the optional '-q' or '--quiet' flags to hide some of the printed "debug" text from printing. 
    However, it's better to leave it on in case you're wondering why a file isn't being edited. 

Examples:
python3 imgResizer.py -q
python3 imgResizer.py
python3 imgResizer.py --quiet file1 file2 ...
python3 imgResizer.py file1 file2 ...

"""

import sys
import os

from PIL import Image

"""
Begin constants
"""

# Pixels to grab from each end
N = 4

# Padding between the center part image and the ends
padding = 4

# New dimension(s) the images are to be fitted into. 
one_slot = (32, 32)
two_slot = (64 + padding, 32)
six_slot = (128 + 3 * padding, 32)

# Size of the images that are expected. If a size 1 image is passed, it'll do nothing. 
two_slot_default = (76, 32)
six_slot_default = (252, 32)

"""
End constants
"""

print()

args = sys.argv[1:]

quiet = False
if len(args) >= 1 and (args[0] == '--quiet' or args[0] == '-q'):
    quiet = True

if not args or len(args) == 1 and quiet:
    if not quiet:
        print("Using all *.png files in current directory")
    from os import listdir
    from os.path import isfile, join
    args = [f for f in listdir('.') if isfile(join('.', f)) and f[-4:] == '.png']
else:
    args = [x + '.png' for x in args if x != '--quiet' and x != '-q']

if not quiet:
    print("Images:", args)

# Store the name of the file excluding extension and the Image object for each file. 
imgs = [[x[:-4 or None], Image.open(x)] for x in args]
new_images = []

for ele in imgs:

    # Image object at index 1
    img = ele[1]

    if img.size == one_slot:
        if not quiet:
            print("Skipping {0} since it is already the smallest size.".format(ele[0]))
        continue

    # I don't know why we need this but we have it in PADImageDownload.py
    converted_img = img.convert('RGBA')

    new_img = Image.new("RGBA", one_slot)

    if img.size == two_slot_default:
        new_img2 = Image.new("RGBA", two_slot)
    elif img.size == six_slot_default:
        new_img2 = Image.new("RGBA", six_slot)
    else:
        if not quiet:
            print('Warning: {0} has dimensions {1} and does not match default size of {2} nor {3}'\
                    .format(ele[0], img.size, two_slot_default, six_slot_default))
        continue

    # Original image's width
    original_width = converted_img.size[0]

    new_img.paste(converted_img.crop((0, 0, N, 32)))
    new_img.paste(converted_img.crop((original_width / 2 - 16 + N, 0, 
                                        original_width / 2 + 16 - N, 32)), 
                                    (N, 0))
    new_img.paste(converted_img.crop((original_width - N, 0, original_width, 32)), 
                                    (one_slot[0] - N, 0))

    '''
    Image specific width: size 2 latents to be converted to a different size
    than size 6 latents
    '''
    specific_new_width = new_img2.size[0]

    new_img2.paste(converted_img.crop((0, 0, N, 32)))
    new_img2.paste(converted_img.crop((original_width / 2 - specific_new_width / 2 + N, 0, 
                                        original_width / 2 + specific_new_width / 2 - N, 32)),
                                    (N, 0))
    new_img2.paste(converted_img.crop((original_width - N, 0, original_width, 32)), 
                                    (specific_new_width - N, 0))

    new_images.append([ele[0], [new_img, new_img2]])

if not os.path.exists('./out') and new_images:
    os.makedirs('./out')

for ele in new_images:

    # Image name in index 0, Image object in index 1
    images = ele[1]
    for image in images:
        if image.size == one_slot:
            typ = "slim"
        elif image.size == two_slot:
            typ = "kslim"
        else:
            typ = "tslim"

        image.save("./out/{0}_{1}.png".format(ele[0], typ))

print()

if not quiet:
    print("Use '-q' or '--quiet' flag to hide warnings and other information")

if new_images:
    print("Saved output(s) to ./out/")

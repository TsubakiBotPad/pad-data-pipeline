"""
Automatically reformats the full latent images into single width and team display sizes.
"""
import os
import shutil

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


def process_file(file_name: str):
    team_file = os.path.join('..', 'team_display', file_name)
    print('processing', file_name, 'to', team_file)
    img = Image.open(file_name)
    if img.size == one_slot:
        # No processing needed
        shutil.copy2(file_name, team_file)
        return

    # # Shrink to single width size
    # # We don't need to do this any more! Fancy single widths are exported
    # new_img = Image.new("RGBA", one_slot)
    # original_width = img.size[0]
    #
    # new_img.paste(img.crop((0, 0, N, 32)))
    # new_img.paste(img.crop((original_width / 2 - 16 + N, 0,
    #                         original_width / 2 + 16 - N, 32)),
    #               (N, 0))
    # new_img.paste(img.crop((original_width - N, 0, original_width, 32)),
    #               (one_slot[0] - N, 0))
    # new_img.save(single_file)

    img = img.convert('RGBA')
    if img.size == two_slot_default:
        new_img = Image.new("RGBA", two_slot)
    elif img.size == six_slot_default:
        new_img = Image.new("RGBA", six_slot)
    else:
        print('Warning: {0} has unexpected dimensions {1}'.format(file_name, img.size))
        return

    original_width = img.size[0]
    specific_new_width = new_img.size[0]

    new_img.paste(img.crop((0, 0, N, 32)))
    new_img.paste(img.crop((original_width / 2 - specific_new_width / 2 + N, 0,
                            original_width / 2 + specific_new_width / 2 - N, 32)),
                  (N, 0))
    new_img.paste(img.crop((original_width - N, 0, original_width, 32)),
                  (specific_new_width - N, 0))

    new_img.save(team_file)


for f in [f for f in os.listdir('.') if f.endswith('.png')]:
    process_file(os.path.join(f))

print('done')

import argparse
import os
import tempfile

parser = argparse.ArgumentParser(
    description="Generates animated for pad monsters.", add_help=False)

inputGroup = parser.add_argument_group("Input")
inputGroup.add_argument("--raw_dir", required=True, help="Path to input BC files")
inputGroup.add_argument("--working_dir", required=True, help="Path to pad-resources project")

outputGroup = parser.add_argument_group("Output")
outputGroup.add_argument("--output_dir", required=True,
                         help="Path to a folder where output should be saved")

helpGroup = parser.add_argument_group("Help")
helpGroup.add_argument("-h", "--help", action="help", help="Displays this help message and exits.")
args = parser.parse_args()

GENERATE_GIF_CMD = """
ffmpeg -i {} \
  -filter_complex 'scale=400:244:flags=lanczos,split [o1] [o2];[o1] palettegen [p]; [o2] fifo [o3];[o3] [p] paletteuse' \
  -r 10 {}
"""

OPTIMIZE_GIF_CMD = """
gifsicle -O3 --lossy=80 {} -o {}
"""

RESIZE_VIDEO_CMD = """
ffmpeg -i {} -pix_fmt yuv420p -r 24 -c:v libx264 -filter:v "crop=640:390:0:60" {}
"""


def run_cmd(cmd, source_file, dest_file):
    final_cmd = cmd.format(source_file, dest_file).strip()
    print('running', final_cmd)
    os.system(final_cmd)
    print('done')


def process_animated(working_dir, pad_id, file_path):
    bin_file = 'mons_{}.bin'.format(pad_id)
    bin_path = os.path.join('data', 'HT', 'bin', bin_file)
    xvfb_prefix = 'xvfb-run -s "-ac -screen 0 640x640x24"'
    yarn_cmd = 'yarn --cwd={} render --bin {} --out {} --nobg --video'.format(
        working_dir, bin_path, file_path)

    full_cmd = '{} {}'.format(xvfb_prefix, yarn_cmd)
    print('running', full_cmd)
    os.system(full_cmd)
    print('done')


raw_dir = args.raw_dir
working_dir = args.working_dir
output_dir = args.output_dir

for file_name in sorted(os.listdir(raw_dir)):
    if 'isanimated' not in file_name:
        continue

    pad_id = file_name.rstrip('.isanimated').lstrip('mons_').lstrip('0')

    video_name = '{}.mp4'.format(pad_id)
    video_path = os.path.join(output_dir, video_name)

    if os.path.exists(video_path):
        print('skipping', video_path)
    else:
        print('processing', video_path)
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_video_path = os.path.join(temp_dir, video_name)
            process_animated(working_dir, pad_id, tmp_video_path)
            run_cmd(RESIZE_VIDEO_CMD, tmp_video_path, video_path)

    gif_name = '{}.gif'.format(pad_id)
    gif_path = os.path.join(output_dir, gif_name)

    if os.path.exists(gif_path):
        print('skipping', gif_path)
    else:
        print('processing', gif_path)
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_gif_path = os.path.join(temp_dir, gif_name)
            run_cmd(GENERATE_GIF_CMD, video_path, tmp_gif_path)
            run_cmd(OPTIMIZE_GIF_CMD, tmp_gif_path, gif_path)

print('done')

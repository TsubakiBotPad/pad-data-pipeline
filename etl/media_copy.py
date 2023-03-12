"""
Copies PAD media to the expected DadGuide locations.
"""
import argparse
import os
import shutil
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Creates DadGuide image repository.", add_help=False)
    input_group = parser.add_argument_group("Input")
    input_group.add_argument("--base_dir", required=True, help="Tsubaki image base dir")

    output_group = parser.add_argument_group("Output")
    output_group.add_argument("--output_dir", required=True,
                              help="Dir to write coalesced output data to")

    return parser.parse_args()


def do_copy(src_path, dest_path):
    for file in os.listdir(src_path):
        if not os.path.exists(dest_path / file):
            print(file)
            shutil.copy2(src_path / file, dest_path / file)


def copy_media(args):
    base_dir = args.base_dir
    output_dir = args.output_dir

    for server in ('na', 'jp'):
        for folder in ('portraits', 'icons', 'spine_files', 'hq_portraits'):
            # HQ Portraits don't exist in NA server
            if server == 'na' and folder == 'hq_portraits':
                continue
            from_dir = Path(base_dir, server, folder)
            to_dir = Path(output_dir, folder)
            to_dir.mkdir(parents=True, exist_ok=True)
            do_copy(from_dir, to_dir)


if __name__ == '__main__':
    copy_media(parse_args())

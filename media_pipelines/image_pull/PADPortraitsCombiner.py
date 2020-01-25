"""
This is a necessary hack. NA doesn't have all the latest cards, but Miru defaults
to pointing to the NA images. This script combines missing NA files with the JP
versions in a final directory.
"""

import argparse
import csv
import os
import re
import shutil
import sys
import time


parser = argparse.ArgumentParser(description="Combines NA/JP P&D portraits.", add_help=False)

inputGroup = parser.add_argument_group("Input")
inputGroup.add_argument("--na_dir", help="Path to a folder where NA portraits are")
inputGroup.add_argument("--jp_dir", help="Path to a folder where JP portraits are")


outputGroup = parser.add_argument_group("Output")
outputGroup.add_argument("--output_dir", help="Path to a folder where output should be saved")

helpGroup = parser.add_argument_group("Help")
helpGroup.add_argument("-h", "--help", action="help", help="Displays this help message and exits.")
args = parser.parse_args()


na_dir = args.na_dir
jp_dir = args.jp_dir
output_dir = args.output_dir

na_files = os.listdir(na_dir)
jp_files = os.listdir(jp_dir)

print('Copying {} na files'.format(len(na_files)))
for f in na_files:
    src = os.path.join(na_dir, f)
    dst = os.path.join(output_dir, f)
    shutil.copy2(src, dst)

for f in jp_files:
    if f in na_files:
        continue
    print('Copying backup file from jp: {}'.format(f))
    src = os.path.join(jp_dir, f)
    dst = os.path.join(output_dir, f)
    shutil.copy2(src, dst)

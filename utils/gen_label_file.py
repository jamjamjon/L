
from tqdm import tqdm 
from pathlib import Path
import argparse
import sys
import rich
import os
import shutil


def parse_opt():
	parser = argparse.ArgumentParser()
	parser.add_argument('--input', type=str, default='', help='img dir path(s)')
	parser.add_argument('--output', type=str, default='', help='output dir')

	opt = parser.parse_args()
	rich.print(opt, end="\n\n")
	return opt



def main(opt):
	img_list = [x for x in Path(opt.input).iterdir() if x.suffix.lower() in ['.png', '.jpg', '.jpeg']]
	rich.print(len(img_list))

	for img in tqdm(img_list):
		label_p = img.resolve().with_suffix('.txt')		
		label_p.touch()
	


if __name__ == "__main__":
    opt = parse_opt()
    main(opt)

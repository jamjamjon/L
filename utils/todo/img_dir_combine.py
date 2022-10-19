#!/usr/bin/env python
# -*- coding:utf-8 -*- 


# from slacking_box import video_tools
# from slacking_box import out
# import slacking_box as sb
from tqdm import tqdm 
from pathlib import Path
import argparse
import sys
import rich
import os
import shutil


#--------------------------------------------
#       PYTHON_PATH
#--------------------------------------------
FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # abs path => relative
# rich.print(list(FILE.parents))
# rich.print(f"[italic magenta]==>Current Python PATH: {ROOT}")
#--------------------------------------------



def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, default='./', help='img dir path(s)')
    parser.add_argument('--output', type=str, default='raw_video/img_combined', help='output dir')

    opt = parser.parse_args()
    rich.print(opt, end="\n\n")
    return opt



def main(opt):


	saveout_dir = Path(opt.output).resolve()

	# mkdir if now exists OR check if has data in exist dir
	if not saveout_dir.exists():
		rich.print("[italic magenta]==>Output dir is not exist! Create automaticlly.", end="\n")
		saveout_dir.mkdir()
	else:
		rich.print("[italic magenta]==>Output dir is exist!", end="\t")
		size = len([x for x in saveout_dir.iterdir()])
		if size > 1:
			rich.print("[bold red]And it has content, Break! Please check!")
			raise StopIteration
		else:
			rich.print("[green]No content in it. Don't worry about it")
		


	# input 
	imgs_dir_list = [x for x in Path(opt.input).iterdir() if x.is_dir() and x.resolve() != saveout_dir.resolve()]
	rich.print(f"[italic blue]==>Dir to be combined:[/italic blue]\n{imgs_dir_list}\n\n")

	# all dirs to be combined
	for d in tqdm(imgs_dir_list):
		dir_name = d.stem
		dir_path = d.resolve()
		images_list = list(Path(dir_path).iterdir())

		# images in every dir 
		for img in images_list:
			img_path = img.resolve()
			des_path = saveout_dir.resolve() / (str(dir_name) + "_" + img.name)
			# rich.print(des_path)
			shutil.copy(str(img_path), str(des_path))

		# break
			


if __name__ == "__main__":
    opt = parse_opt()
    main(opt)

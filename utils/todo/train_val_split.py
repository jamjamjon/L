# encoding: utf-8

import os
import shutil
import sys
import random
import rich
from pathlib import Path
from tqdm import tqdm
import argparse


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


# train_val split
def train_val_split(img_folder, ann_folder=None, 
					rate=0.8, 
					seed=777, 
					cp_mv = "cp", 
					# ann_suffix=".txt",
					saveout_dir="train_val",
					# train_images_dir = "train/images",
					# val_images_dir = "val/images",
					# train_ann_dir = "train/labels",	
					# val_ann_dir = "val/labels",
					):
	'''
	==> split one or two folders into 2 folders: [train] [val], especially for [img_folder] and [ann_folder] two folders, [ann_folder] is the annotation of [img_folder].

	├── train_val
	│   ├── train
	│   │   ├── images
	│   │   │   ├── 0a96c6d2-ed93-4dec-8562-1c69af136ca7.jpg
	│   │   │   ├── 0aa20ec0-3ff3-41d4-a3a7-65c03c383851.jpg
	│   │   │   ├── 0aecd409-8466-42bb-824a-e43ece9a4ec2.jpg
	│   │   │   ├── 0b689368-c1c5-4b33-92d5-ccf83cbc44bc.jpg
	│   │   │   ├── 0bb3c0c6-744d-4b31-be3f-d0cdbc844de1.jpg
	│   │   │   ├── 0c88dc20-e845-4bac-bae0-a8d86ce1d47a.jpg
	│   │   │   ├── 0ce61215-6d34-49f9-aa6d-5f0feed430f8.jpg
	│   │   │   └── 0cf08ae1-3067-41bb-a3e1-e964cb55da32.jpg
	│   │   └── labels
	│   │       ├── 0a96c6d2-ed93-4dec-8562-1c69af136ca7.xml
	│   │       ├── 0aa20ec0-3ff3-41d4-a3a7-65c03c383851.xml
	│   │       ├── 0aecd409-8466-42bb-824a-e43ece9a4ec2.xml
	│   │       ├── 0b689368-c1c5-4b33-92d5-ccf83cbc44bc.xml
	│   │       ├── 0bb3c0c6-744d-4b31-be3f-d0cdbc844de1.xml
	│   │       ├── 0c88dc20-e845-4bac-bae0-a8d86ce1d47a.xml
	│   │       ├── 0ce61215-6d34-49f9-aa6d-5f0feed430f8.xml
	│   │       └── 0cf08ae1-3067-41bb-a3e1-e964cb55da32.xml
	│   └── val
	│       ├── images
	│       │   ├── 00000.jpg
	│       │   ├── 0bf735a1-bab3-4de4-9174-d938f5d7f64d.jpg
	│       │   ├── 0c6a5567-8804-44a6-ba91-864ca6e7f8a2.jpg
	│       │   └── 0ca430be-57db-49c9-801a-47d95f6b1f60.jpg
	│       └── labels
	│           ├── 00000.xml
	│           ├── 0bf735a1-bab3-4de4-9174-d938f5d7f64d.xml
	│           ├── 0c6a5567-8804-44a6-ba91-864ca6e7f8a2.xml
	│           └── 0ca430be-57db-49c9-801a-47d95f6b1f60.xml

	'''
	
	# check if valid 
	assert rate <= 1, "==>rate should be less than 1."

	# input dirs: imgs & labels
	images_dir = Path(img_folder).resolve()		# return abs-path
	
	if ann_folder:	
		annotations_dir = Path(ann_folder).resolve()

	# clean dir before make save out dirs
	if Path(saveout_dir).resolve().exists():
		shutil.rmtree(Path(saveout_dir).resolve())

	# make save dirs for train_val_images
	train_images_dir = Path(saveout_dir).joinpath("train/images")
	val_images_dir = Path(saveout_dir).joinpath("val/images")

	Path(train_images_dir).resolve().mkdir(parents=True, exist_ok=True)
	Path(val_images_dir).resolve().mkdir(parents=True, exist_ok=True)	

	# make save dirs for train_val_labels
	if ann_folder:
		train_ann_dir = Path(saveout_dir).joinpath("train/labels")
		val_ann_dir = Path(saveout_dir).joinpath("val/labels")
		Path(train_ann_dir).resolve().mkdir(parents=True, exist_ok=True)
		Path(val_ann_dir).resolve().mkdir(parents=True, exist_ok=True)	
	
	# 
	all_images = [x for x in Path(images_dir).iterdir() if x.suffix in ['.jpeg', '.jpg', '.png']]	
	num_images = len(all_images)					# num of all images
	num_train_images = int(num_images * rate)		# num of train images
	num_val_images = num_images - num_train_images	# num of val images

	# info
	rich.print(f"[bold magenta]==>All element: {num_images} | Train number: {num_train_images} | Val number: {num_val_images}")


	# random select
	random.seed(seed)
	train_samples_id = random.sample(range(num_images), num_train_images)
	val_samples_id = list(set(range(num_images)) - set(train_samples_id))
	
	# train dir
	for train_id in tqdm(train_samples_id):
		
		image = all_images[train_id]	
		if cp_mv == "cp":
			shutil.copy(image, train_images_dir)
			if ann_folder:
				ann_path = annotations_dir / Path(str(image.stem) + '.txt')
				shutil.copy(ann_path, train_ann_dir)
		elif cp_mv == "mv":
			shutil.move(str(image), train_images_dir)
			if ann_folder:
				ann_path = annotations_dir / Path(str(image.stem) + '.txt')
				shutil.move(str(ann_path), train_ann_dir)

	# val dir
	for val_id in tqdm(val_samples_id):

		image = all_images[val_id]	
		if cp_mv == "cp":
			shutil.copy(image, val_images_dir)
			if ann_folder:
				ann_path = annotations_dir / Path(str(image.stem) + '.txt')	
				shutil.copy(ann_path, val_ann_dir)
		elif cp_mv == "mv":
			shutil.move(str(image), val_images_dir)
			if ann_folder:			
				ann_path = annotations_dir / Path(str(image.stem) + '.txt')
				shutil.move(str(ann_path), val_ann_dir)

	rich.print(f"==>saved at: {Path(saveout_dir).resolve()}")


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-img', type=str, default='', help='img dir path(s)')
    parser.add_argument('--input-label', type=str, default='', help='label dir path')
    parser.add_argument('--saveout-dir', type=str, default='new_save_out', help='label dir path')

    parser.add_argument('--cp-mv', type=str, default='cp', help='img suffix')
    parser.add_argument('--rate', type=float, default=0.8, help='N frame')
    parser.add_argument('--seed', type=int, default=777, help='seed')

    # parser.add_argument('--train_images_dir', type=str, default='train_val/train/images', help='label dir path')
    # parser.add_argument('--val_images_dir', type=str, default='train_val/val/images', help='label dir path')
    # parser.add_argument('--train_ann_dir', type=str, default='train_val/train/labels', help='label dir path')
    # parser.add_argument('--val_ann_dir', type=str, default='train_val/val/labels', help='label dir path')

    opt = parser.parse_args()
    rich.print(opt, end="\n\n")
    return opt




def main(opt):

	train_val_split(
					img_folder=opt.input_img, 
					ann_folder=opt.input_label,
					rate=opt.rate, 
					seed=opt.seed,
					# ann_suffix=".txt", 
					cp_mv=opt.cp_mv,
					saveout_dir=opt.saveout_dir,
					# train_images_dir = opt.train_images_dir,
					# val_images_dir = opt.val_images_dir,
					# train_ann_dir = opt.train_ann_dir,	
					# val_ann_dir = opt.val_ann_dir,
					)



if __name__ == "__main__":
    opt = parse_opt()
    main(opt)








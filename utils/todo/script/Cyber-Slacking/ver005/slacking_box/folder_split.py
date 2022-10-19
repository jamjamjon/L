# encoding: utf-8

import os
import shutil
import sys
import random
import rich
from pathlib import Path


# train val test split
def tvt_split(	img_folder, ann_folder=None, 
				rate=[0.6, 0.3, 0.1], 
				seed=777, 
				cp_mv = "cp", 
				ann_suffix=".txt",
				train_images_dir = "train_val_test/train/images",
				val_images_dir = "train_val_test/val/images",
				test_images_dir = "train_val_test/test/images",				
				train_ann_dir = "train_val_test/train/labels",	
				val_ann_dir = "train_val_test/val/labels",
				test_ann_dir = "train_val_test/test/labels",
			  ):

	'''
		==> split one or two folders into 3 folders: [train] [val] [test], especially for [img_folder] and [ann_folder] two folders, [ann_folder] is the annotation of [img_folder].
	├── train_val_test
	│   ├── test
	│   │   ├── images
	│   │   │   ├── 0c6a5567-8804-44a6-ba91-864ca6e7f8a2.jpg
	│   │   │   └── 0cf08ae1-3067-41bb-a3e1-e964cb55da32.jpg
	│   │   └── labels
	│   │       ├── 0c6a5567-8804-44a6-ba91-864ca6e7f8a2.xml
	│   │       └── 0cf08ae1-3067-41bb-a3e1-e964cb55da32.xml
	│   ├── train
	│   │   ├── images
	│   │   │   ├── 0a96c6d2-ed93-4dec-8562-1c69af136ca7.jpg
	│   │   │   ├── 0aa20ec0-3ff3-41d4-a3a7-65c03c383851.jpg
	│   │   │   ├── 0aecd409-8466-42bb-824a-e43ece9a4ec2.jpg
	│   │   │   ├── 0c88dc20-e845-4bac-bae0-a8d86ce1d47a.jpg
	│   │   │   └── 0ce61215-6d34-49f9-aa6d-5f0feed430f8.jpg
	│   │   └── labels
	│   │       ├── 0a96c6d2-ed93-4dec-8562-1c69af136ca7.xml
	│   │       ├── 0aa20ec0-3ff3-41d4-a3a7-65c03c383851.xml
	│   │       ├── 0aecd409-8466-42bb-824a-e43ece9a4ec2.xml
	│   │       ├── 0c88dc20-e845-4bac-bae0-a8d86ce1d47a.xml
	│   │       └── 0ce61215-6d34-49f9-aa6d-5f0feed430f8.xml
	│   └── val
	│       ├── images
	│       │   ├── 0b689368-c1c5-4b33-92d5-ccf83cbc44bc.jpg
	│       │   └── 0bb3c0c6-744d-4b31-be3f-d0cdbc844de1.jpg
	│       └── labels
	│           ├── 0b689368-c1c5-4b33-92d5-ccf83cbc44bc.xml
	│           └── 0bb3c0c6-744d-4b31-be3f-d0cdbc844de1.xml

	'''

	
	# check if valid 
	assert sum(rate) <= 1, "==> sum of these rate should be less than 1."

	# input dirs: imgs & labels
	images_dir = Path(img_folder).resolve()		# return abs-path
	
	if ann_folder:	
		annotations_dir = Path(ann_folder).resolve()

	# clean dir before make save out dirs
	if Path("train_val_test").resolve().exists():
		shutil.rmtree(Path("train_val_test").resolve())

	# make save dirs for train_val_images
	Path(train_images_dir).resolve().mkdir(parents=True, exist_ok=True)
	Path(val_images_dir).resolve().mkdir(parents=True, exist_ok=True)	
	Path(test_images_dir).resolve().mkdir(parents=True, exist_ok=True)	

	# make save dirs for train_val_labels
	if ann_folder:
		Path(train_ann_dir).resolve().mkdir(parents=True, exist_ok=True)
		Path(val_ann_dir).resolve().mkdir(parents=True, exist_ok=True)
		Path(test_ann_dir).resolve().mkdir(parents=True, exist_ok=True)	
	


	# 
	all_images = list(Path(images_dir).iterdir())				# all images
	num_images = len(all_images)								# num of all images
	num_train_images = int(num_images * rate[0])				# num of train images
	num_val_images = int(num_images * rate[1])					# num of val images
	num_test_images = num_images - num_train_images - num_val_images  		# num of test images

	# info
	rich.print(f"[bold magenta]==>All element: {num_images} | Train number: {num_train_images} | Val number: {num_val_images} | Test number: {num_test_images}")

	# random select
	random.seed(seed)
	train_samples_id = random.sample(range(num_images), num_train_images)
	val_samples_id = random.sample(set(range(num_images)) - set(train_samples_id), num_val_images)
	test_samples_id = list(set(range(num_images)) - set(train_samples_id) - set(val_samples_id))

	
	# train dir
	for train_id in train_samples_id:
		
		image = all_images[train_id]	
		if cp_mv == "cp":
			shutil.copy(image, train_images_dir)
			if ann_folder:
				ann_path = annotations_dir / Path(str(image.stem) + ann_suffix)
				shutil.copy(ann_path, train_ann_dir)
		elif cp_mv == "mv":
			shutil.move(str(image), train_images_dir)
			if ann_folder:
				ann_path = annotations_dir / Path(str(image.stem) + ann_suffix)
				shutil.move(str(ann_path), train_ann_dir)

	# val dir
	for val_id in val_samples_id:

		image = all_images[val_id]	
		if cp_mv == "cp":
			shutil.copy(image, val_images_dir)
			if ann_folder:
				ann_path = annotations_dir / Path(str(image.stem) + ann_suffix)	
				shutil.copy(ann_path, val_ann_dir)
		elif cp_mv == "mv":
			shutil.move(str(image), val_images_dir)
			if ann_folder:			
				ann_path = annotations_dir / Path(str(image.stem) + ann_suffix)
				shutil.move(str(ann_path), val_ann_dir)

	# test dir
	for test_id in test_samples_id:

		image = all_images[test_id]	
		if cp_mv == "cp":
			shutil.copy(image, test_images_dir)
			if ann_folder:
				ann_path = annotations_dir / Path(str(image.stem) + ann_suffix)	
				shutil.copy(ann_path, test_ann_dir)
		elif cp_mv == "mv":
			shutil.move(str(image), test_images_dir)
			if ann_folder:			
				ann_path = annotations_dir / Path(str(image.stem) + ann_suffix)
				shutil.move(str(ann_path), test_ann_dir)

	

# train_val split
def train_val_split(img_folder, ann_folder=None, 
					rate=0.8, 
					seed=777, 
					cp_mv = "cp", 
					ann_suffix=".txt",
					train_images_dir = "train_val/train/images",
					val_images_dir = "train_val/val/images",
					train_ann_dir = "train_val/train/labels",	
					val_ann_dir = "train_val/val/labels",
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
	if Path("train_val").resolve().exists():
		shutil.rmtree(Path("train_val").resolve())

	# make save dirs for train_val_images
	Path(train_images_dir).resolve().mkdir(parents=True, exist_ok=True)
	Path(val_images_dir).resolve().mkdir(parents=True, exist_ok=True)	

	# make save dirs for train_val_labels
	if ann_folder:
		Path(train_ann_dir).resolve().mkdir(parents=True, exist_ok=True)
		Path(val_ann_dir).resolve().mkdir(parents=True, exist_ok=True)	
	
	# 
	all_images = list(Path(images_dir).iterdir())	# all images
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
	for train_id in train_samples_id:
		
		image = all_images[train_id]	
		if cp_mv == "cp":
			shutil.copy(image, train_images_dir)
			if ann_folder:
				ann_path = annotations_dir / Path(str(image.stem) + ann_suffix)
				shutil.copy(ann_path, train_ann_dir)
		elif cp_mv == "mv":
			shutil.move(str(image), train_images_dir)
			if ann_folder:
				ann_path = annotations_dir / Path(str(image.stem) + ann_suffix)
				shutil.move(str(ann_path), train_ann_dir)

	# val dir
	for val_id in val_samples_id:

		image = all_images[val_id]	
		if cp_mv == "cp":
			shutil.copy(image, val_images_dir)
			if ann_folder:
				ann_path = annotations_dir / Path(str(image.stem) + ann_suffix)	
				shutil.copy(ann_path, val_ann_dir)
		elif cp_mv == "mv":
			shutil.move(str(image), val_images_dir)
			if ann_folder:			
				ann_path = annotations_dir / Path(str(image.stem) + ann_suffix)
				shutil.move(str(ann_path), val_ann_dir)

	


if __name__ == "__main__":
	# train_val_split("/home/user/Desktop/cyberslacking_project/ver004/slacking_box/images", rate=.8, ann_suffix=".xml", cp_mv="cp")
	tvt_split("/home/user/Desktop/cyberslacking_project/ver004/slacking_box/images", "annotations",ann_suffix=".xml", cp_mv="mv")








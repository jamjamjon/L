import os
from slacking_box import out
from tqdm import tqdm
from pathlib import Path
import shutil
import cv2



input_img_dir = "/home/user/zhangjian/Models/fall_detect_proj/pedestrian_datasets/coco/images/train2017"
input_label_dir = "/home/user/zhangjian/Models/fall_detect_proj/pedestrian_datasets/coco/labels/train2017"


# output dir
output_img_dir = "coco_filter_person/images"
output_label_dir = "coco_filter_person/labels"

if not Path(output_img_dir).exists():
	Path(output_img_dir).mkdir(parents=True, exist_ok=True)
else:
	shutil.rmtree(output_img_dir)
	Path(output_img_dir).mkdir(parents=True, exist_ok=True)

if not Path(output_label_dir).exists():
	Path(output_label_dir).mkdir(parents=True, exist_ok=True)
else:
	shutil.rmtree(output_label_dir)
	Path(output_label_dir).mkdir(parents=True, exist_ok=True)


# input info
images_list = [x for x in Path(input_img_dir).iterdir() if not x.is_dir()]
out(f"[bold green]==>Images counts: {len(images_list)}")
labels_list = list(Path(input_label_dir).glob("*.txt"))
out(f"[bold green]==>Labels counts: {len(labels_list)}")


# read images(opencv)
idx = 1
for img in tqdm(images_list):
	img0 = cv2.imread(str(img))
	
	cv2.destroyAllWindows()
	cv2.imshow(str(img.stem), img0)
	key = cv2.waitKey(0) & 0xff
	if key == ord("q"):
		cv2.destroyAllWindows()
		break
	elif key == ord("s"):

		label_path = Path(input_label_dir) / Path(str(img.stem) + ".txt")
		if label_path in labels_list:
			shutil.copy(img, output_img_dir)
			shutil.copy(label_path, output_label_dir)
			out(f"[bold magenta]==>Image & labels has saved: {idx}")
			idx += 1
						
		else:
			out(f"[bold red]==>Can't find label: {label_path}")
			out(img)
			




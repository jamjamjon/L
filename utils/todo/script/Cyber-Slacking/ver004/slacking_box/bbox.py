import rich
import os
import cv2
import numpy as np
from tqdm import tqdm
from pathlib import Path
import shutil
from . import rich_print

def gt_bbox_check(images_dir, 
				labels_dir,
				classes=None,
				start=0,
				end=-1,
				label_type="ccwh", # yolo type. addttional type support => [x1,y1,x2,y2] and  [x1,y1,w,h]
				suffix=".txt",
				save_out="save_out",
				mv_dataset="temp_dir",
				verbose=False,
				save_log="",
				):

	rich.print(f"[bold italic green]This function can: \n[bold magenta]==>1. Check if label.txt is correct. \n==>2. Save images with bboxes. \n==>3. Move images and corresponding label(.txt) out for filtering dataset.")
	rich.print(f"[bold green]Press s/S to save image with bboxes to save_out(default)\nPress m/M to move image and corresponding label(.txt) to temp_dir(default)\nPress q/Q to quit.\nPress other keys to move on.")
	rich.print(f"[bold red]!!! Images in Dir will be log at paramter save_log(if named)")

	images_list = [x for x in Path(images_dir).resolve().iterdir() if (str(x).endswith("jpg") or str(x).endswith("jpeg") or str(x).endswith("png"))]

	# 保存log，文件顺序
	if save_log:
		rich_print.out(images_list, to_file=save_log, to_console=False)

	# main
	for img in tqdm(images_list[start: end]):
		if verbose:
			rich.print(img)

		
		image = cv2.imread(str(img))

		if image.shape[1] is None:
			continue

		width = image.shape[1]
		height = image.shape[0]
		
		label_path = Path(labels_dir) / Path(str(img.stem) + suffix)
		bboxs = []
	

		with open(label_path, "r") as f:
			for line in f:
				
				content = line.strip().split(" ")	
				if label_type == "ccwh":
					cx = round(float(content[1]) * width)
					cy = round(float(content[2]) * height)
					w = round(float(content[3]) * width)
					h = round(float(content[4]) * height)

					x1 = cx - w // 2
					y1 = cy - h // 2
					x2 = cx + w // 2
					y2 = cy + h // 2

					bboxs.append([x1, y1, x2, y2, content[0]])
				elif label_type == "xyxy":
					x1 = round(float(content[1]) * width)
					y1 = round(float(content[2]) * height)
					x2 = round(float(content[3]) * width)
					y2 = round(float(content[4]) * height)
					bboxs.append([x1, y1, x2, y2, content[0]])
				
				elif label_type == "xywh":
					x1 = round(float(content[1]) * width)
					y1 = round(float(content[2]) * height)
					w = round(float(content[3]) * width)
					h = round(float(content[4]) * height)
					
					x2 = x1 + w
					y2 = y1 + h
					bboxs.append([x1, y1, x2, y2, content[0]])


		for box in bboxs:
			
			if not classes:
				cv2.rectangle(image, (box[0], box[1]), (box[2], box[3]), (0, 255, 255), 2)
				cv2.putText(image, box[-1], (box[0] + 5, box[1] + 20), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(0, 255, 0), thickness=2)
			else:
				cv2.rectangle(image, (box[0], box[1]), (box[2], box[3]), (0, 255, 255), 2)
				cv2.putText(image, classes[int(box[-1] + 5)], (box[0], box[1] + 20), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(0, 255, 0), thickness=2)
	
		cv2.destroyAllWindows()
		cv2.imshow("{}".format(str(img)), image)

		key = cv2.waitKey(0)
		if key == ord("q") or key == ord("Q"):
			cv2.destroyAllWindows()
			break
		elif key == ord("s") or key == ord("S"):	# save
			if not Path(save_out).resolve().exists():
				Path(save_out).resolve().mkdir()
			save = Path(save_out).resolve() / img.name
			cv2.imwrite(str(save), image)
		elif key == ord("m") or key == ord("M"):	# move to another dir
			if not Path(mv_dataset).resolve().exists():
				Path(mv_dataset).resolve().mkdir()

			des = Path(mv_dataset).resolve()
			#rich.print(des)
			#rich.print(str(img))
			shutil.move(str(img), str(des))		
			shutil.move(str(label_path), str(des))
			rich.print(f"[bold italic red]==>File moved!![italic magenta]\n  @Source: {str(img)}\n  @Destination: {str(des)}")
	
		
			





if __name__ == "__main__":
	CLASSES = ("person", "bicycle", "car", "motorbike ", "aeroplane ", "bus ", "train", "truck ", "boat", "traffic light",
           "fire hydrant", "stop sign ", "parking meter", "bench", "bird", "cat", "dog ", "horse ", "sheep", "cow",
           "elephant",
           "bear", "zebra ", "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis",
           "snowboard", "sports ball", "kite",
           "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
           "fork", "knife ",
           "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza ", "donut",
           "cake", "chair", "sofa",
           "pottedplant", "bed", "diningtable", "toilet ", "tvmonitor", "laptop ", "mouse   ", "remote ",
           "keyboard ", "cell phone", "microwave ",
           "oven ", "toaster", "sink", "refrigerator ", "book", "clock", "vase", "scissors ", "teddy bear ",
           "hair drier", "toothbrush ")

	gt_bbox_check(images_dir="/home/user/wuzhe/darknet/darknet/train_coco/train_images", 
				labels_dir="/home/user/wuzhe/darknet/darknet/train_coco/train_labels",
				start=0,
				end=-1,
				classes=CLASSES,
				label_type="ccwh", # yolo type. addttional type support => [x1,y1,x2,y2] and [x1,y1,w,h]
				suffix=".txt",
				mv_dataset="temp_dir",
				)


















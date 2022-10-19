import os
#from slacking_box import out
from tqdm import tqdm
from pathlib import Path, PurePath
import shutil
import cv2
#import slacking_box as sb
import rich
import argparse
import sys




def gt_bbox_check(
				# images_dir,
				image_list,
				# labels_dir,
				label_list,

				classes_name=[],
				start=0,
				end=-1,
				label_type="ccwh", # yolo type.
				save_out="save_out",
				mv_dataset="wrong_data_dir",
				verbose=False,
				# save_log="",
				exclude_cls=None,
				cls=None,
				hide_label=True,
				line_thickness=2,
				):

	rich.print(f"[bold gold1]-"*100)
	rich.print(f"[gold1]# Press m/M to move image and corresponding label(.txt) to temp_dir(default)")
	rich.print(f"[gold1]# Press s/S to save image with bboxes to save_out(default)")
	rich.print(f"[gold1]# Press q/Q to quit.")
	rich.print(f"[gold1]# Press other keys to move on.")
	rich.print(f"[blue]# Images order list in Dir will be logged. --save_log(if named)")
	rich.print(f"[bold gold1]-"*100)



	# save some imgs can not be cv2.imread
	wrong_image_list = []


	# main
	for img_path in tqdm(image_list[start: end]):

		# show image abs path
		if verbose:
			rich.print(f"[italic magenta]Current: {img_path}")

		# read image
		image = cv2.imread(str(img_path))

		if image.shape[1] is None:
			rich.print(f"[bold red]Wrong image: {img_path.name}")
			wrong_image_list.append(img_path.name)
			continue

		width = image.shape[1]
		height = image.shape[0]

		# lable path		
		label_path = label_list[0].parent.joinpath(img_path.stem + '.txt')  
		# print("img ", img_path)
		# print("label ", label_path)
		# exit()

		bboxs = []
		with open(label_path, "r") as f:
			for line in f:
				
				content = line.strip().split(" ")	

				# 不查看某个标签
				if exclude_cls is not None:
					if content[0] == str(exclude_cls):
						continue

				# 单独查看某个标签
				if cls is not None:
					if content[0] != str(cls):
						continue	


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

		# 如果有bbox
		if len(bboxs) != 0:
			for box in bboxs:
				cv2.rectangle(image, (box[0], box[1]), (box[2], box[3]), (0, 255, 255), line_thickness)

				if not hide_label:
					if not classes_name:
						cv2.putText(image, box[-1], (box[0] + 5, box[1] + 20), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(0, 255, 0), thickness=2)
					else:
						cv2.putText(image, classes_name[int(box[-1])], (box[0]+5, box[1] + 20), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(0, 255, 0), thickness=2)
	
			cv2.destroyAllWindows()
			cv2.imshow("{}".format(str(img_path.name)), image)


			#--------------------------------------
			#    key listen
			#--------------------------------------
			key = cv2.waitKey(0)
			if key == ord("q") or key == ord("Q"):
				cv2.destroyAllWindows()
				break

			elif key == ord("s") or key == ord("S"):	# save
				if not Path(save_out).resolve().exists():
					Path(save_out).resolve().mkdir()
				save = Path(save_out).resolve() / img_path.name
				cv2.imwrite(str(save), image)
				rich.print(f"[bold italic blue]==>File saved > {save}")

			elif key == ord("m") or key == ord("M"):	# move to another dir
				if not Path(mv_dataset).resolve().exists():
					Path(mv_dataset).resolve().mkdir()

				des = Path(mv_dataset).resolve()
				# rich.print(des)
				# rich.print(str(img_path))
				shutil.move(str(img_path), str(des))		
				shutil.move(str(label_path), str(des))
				rich.print(f"[bold italic red]==>File moved!![italic magenta]\n  @Source: {str(img_path)}\n  @Destination: {str(des)}")
	
	# 无法被opencv读取的图
	if len(wrong_image_list) > 0:
		rich.print(f"[bold red]==>These images can not be imread:")
		rich.print(wrong_image_list)
	

	





def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_img', type=str, default="", help='img dir path(s)')
    parser.add_argument('--input_label', type=str, default="", help='label dir path(s)')

    parser.add_argument('--start', type=int, default=0, help='start')
    parser.add_argument('--end', type=int, default=-1, help='end')

    parser.add_argument('--line-thickness', type=int, default=2, help='end')
    parser.add_argument('--label_type', type=str, default="ccwh", help='# yolo type. addttional type support => [x1,y1,x2,y2] and  [x1,y1,w,h]')

    parser.add_argument('--save-out', type=str, default="save_out", help='press S/s to save image') 
    parser.add_argument('--mv-dir', type=str, default="./moved_data", help='press m/M to move image/label')

    parser.add_argument('--verbose', action='store_true', default=True, help='verbose')
    parser.add_argument('--hide-label', action='store_true', help='verbose')

    parser.add_argument('--save_log', type=str, default="", help='save_log') 
    parser.add_argument('--exclude-cls', type=int, default=None, help='filter by class: --classes 0, or --classes 0 2 3')    
    parser.add_argument('--cls', type=int, default=None, help='filter by class: --classes 0, or --classes 0 2 3')    



    opt = parser.parse_args()
    rich.print(opt, end="\n\n")
    return opt



# --------------------------------------------------------------

VIDRO_FORMAT = ['.jpg', '.jpeg', '.png']
CLASSES_NAME = ('person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light',
		        'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
		        'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
		        'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard',
		        'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
		        'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
		        'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
		        'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear',
		        'hair drier', 'toothbrush')


# --------------------------------------------------------------
def main(opt):
	input_img_dir = Path(opt.input_img).resolve()
	input_label_dir = Path(opt.input_label).resolve()

	# input info
	image_list = [x for x in input_img_dir.iterdir() if x.suffix in VIDRO_FORMAT]
	rich.print(f"[bold green]==>Images counts: {len(image_list)}")

	label_list = list(input_label_dir.glob("*.txt"))
	rich.print(f"[bold green]==>Labels counts: {len(label_list)}")


	# 检查是否所有的label都有对应的image
	rich.print(f"[magenta]==>Check if all labels has corresponding images...")
	for label_path in tqdm(label_list):



		if input_img_dir / (label_path.stem + '.png') in image_list:
			continue
		elif input_img_dir / (label_path.stem + '.jpg') in image_list:
			continue
		elif input_img_dir / (label_path.stem + '.jpeg') in image_list:
			continue
		else:
			rich.print(f"[bold red]Wrong: {label_path}")
		
	# 检查是否所有的image都有对应的label
	rich.print(f"[magenta]==>Check if all labels has corresponding images...")
	for image_path in tqdm(image_list):

		if input_label_dir / (image_path.stem + '.txt') in label_list:
			continue
		else:
			rich.print(f"[bold red]Wrong: {label_path}")
		
			
	# GT_bbox plot & checking
	gt_bbox_check(image_list, 
				  label_list, 
				  start=opt.start, 
				  end=opt.end, 
				  verbose=opt.verbose, 
				  mv_dataset=opt.mv_dir,
				  # save_log=opt.save_log,
				  classes_name=CLASSES_NAME,
				  cls=opt.cls,
				  exclude_cls=opt.exclude_cls,
				  hide_label=opt.hide_label,
				  line_thickness=opt.line_thickness,
				  ) 	






if __name__ == "__main__":
    opt = parse_opt()
    main(opt)










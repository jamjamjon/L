import slacking_box as sb
from slacking_box import out
import os
import cv2
import numpy as np

out(f"[bold green]To test label's accuracy!")

labels_dir = "/home/user/wuzhe/darknet/darknet/train_smoke_fire/new_train_labels"
img_path = "/home/user/wuzhe/darknet/darknet/train_smoke_fire/new_train_images"

images = os.listdir(img_path)
# out(images[:10])

for idx, img in enumerate(images[4000:4500]):
	#out(img)
	image = cv2.imread(os.path.join(img_path, img))

	width = image.shape[1]
	height = image.shape[0]

	label_path = os.path.join(labels_dir, img.split(".")[0] + ".txt")
	bboxs = []
	with open(label_path, "r") as f:
		for line in f:

			content = line.strip().split(" ")	
			cx = round(float(content[1]) * width)
			cy = round(float(content[2]) * height)
			w = round(float(content[3]) * width)
			h = round(float(content[4]) * height)

			x1 = cx - w // 2
			y1 = cy - h // 2
			x2 = cx + w // 2
			y2 = cy + h // 2

			bboxs.append([x1, y1, x2, y2, content[0]])

	for box in bboxs:
		# out(box)
		if box[-1] == "0":
			cv2.rectangle(image, (box[0], box[1]), (box[2], box[3]), (0, 255, 255), 3)
		else:
			cv2.rectangle(image, (box[0], box[1]), (box[2], box[3]), (0, 0, 255), 3)

	cv2.imshow("{}".format(idx), image)
	key = cv2.waitKey(0)
	if key == ord("q"):
		cv2.destroyAllWindows()
		break
	elif key == ord("s"):

		cv2.imwrite("res/{}.jpg".format(img), image)

import os 
import sys


thresh = 0.2
meta = os.path.abspath("head_detect.data")
cfg = os.path.abspath("yolov3-tiny_head_detect.cfg")
weights_path = os.path.abspath("backup/yolov3-tiny_head_detect_160000.weights")
save_out = os.path.abspath("rknn_test_imgs_res")

image_dir = os.path.abspath("rknn_test_imgs") # modify!  input data dir
test_command = "./darknet detector test"

base_dir = "/home/user/wuzhe/darknet/darknet"

image_lists = [os.path.join(image_dir, x) for x in os.listdir(image_dir)]
print(image_lists[0])


idx = 1
for image in image_lists:
	image_name = image.split("/")[-1].split(".")[0]

	command = " ".join([test_command, meta, cfg, weights_path, 
						image, "-out",
					 	os.path.join(save_out, image_name),
					 	"-thresh", str(thresh),

					])
	

	os.chdir(base_dir)
	os.system(command)
	idx += 1





print(f"# {idx-1} images detetcting done")

'''
./darknet detector test 
train_head/head_detect.data 
train_head/yolov3-tiny_head_detect.cfg 
train_head/backup_20210608_15_33/yolov3-tiny_head_detect_160000.weights 
train_head/validate_images/20210604_0940_001_408.jpg 
-out head_detect_res/1
'''

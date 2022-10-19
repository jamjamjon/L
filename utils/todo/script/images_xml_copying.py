import os 
import shutil
from slacking_box import out
import slacking_box as sb


img_dir = "train_images"
xml_dir = "train_imageXML"


img_saveout_dir = "smoke_train_img"
xml_saveout_dir = "smoke_train_xml"


image_all = os.listdir(img_dir)
out(f"images num: {len(img_saveout_dir)}")

pwd = os.getcwd()


start_idx = len(os.listdir(img_dir))
out(f"[bold green]Start from {start_idx}")


for image in image_all:
	out(f"[italic bold green]num: {start_idx}")

	img_name = image.split(".")[0]
	
	img_path_old = os.path.join(pwd, img_dir, image)
	xml_path_old = os.path.join(pwd, xml_dir, img_name + ".xml")

	img_path_new = os.path.join(pwd, img_saveout_dir, str(start_idx) + ".jpg")
	xml_path_new = os.path.join(pwd, xml_saveout_dir, str(start_idx) + ".xml")

	shutil.copy(img_path_old, img_path_new)
	shutil.copy(xml_path_old, xml_path_new)

	start_idx += 1


out(f"[bold green]==>{start_idx} file copy done!")


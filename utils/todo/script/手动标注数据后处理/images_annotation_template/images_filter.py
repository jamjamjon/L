# encoding: UTF-8


###########################################################
# 目录结构
# -root
#  - images: 标注图像
#  - all_images: 所有未标注图片文件夹
#  - xmls: 标注图像的xml存放文件夹
#  - imagess_filter.py
#　
#　本代码用于将all_images中已经标注了图像转移到images，同时输出一些信息。
#　By zhangjian, 07/07/2021.
###########################################################

import os
import shutil
import glob

all_images_path = "all_images"
xmls_path = "xmls"
images_marked_path = "images"


if not os.path.exists(images_marked_path):
	os.mkdir(images_marked_path)
	print("--> images dir created!")
else:
	print("--> images dir already exist!")


# global variable
file_modified_lenghth = 0
num_empty_xml_file = 0


# read all_images names
all_xmls = glob.glob(xmls_path + "/*.xml")
print("--> len of all_xmls:", len(all_xmls))

# read all_images
all_images = glob.glob(all_images_path + "/*.jpg")
print(f"--> len of all_images: {len(all_images)}")


# main
for xml_file in all_xmls:

	image_name = os.path.splitext(os.path.basename(xml_file))[0] + ".jpg"
	image_addr = os.path.join(all_images_path, image_name)
	# print(image_addr)

	# move to "images/"
	if image_addr in all_images:
		shutil.move(image_addr, images_marked_path)
		file_modified_lenghth += 1

	# check size of xml file
	xml_size = os.path.getsize(xml_file)
	if xml_size < 430:
		num_empty_xml_file += 1


# info of Dirs
length_of_xmls = len(glob.glob(xmls_path + "/*.xml"))
length_of_unmarked_images = len(glob.glob(all_images_path + "/*.jpg"))
length_of_marked_images = len(glob.glob(images_marked_path + "/*.jpg"))

print(f"--> {file_modified_lenghth} images & xmls check are done!")
print(f"  --> marked images has been moved to [{images_marked_path}/]: {length_of_marked_images}")
print(f"  --> xmls file saved to [{xmls_path}/]: {length_of_xmls}")
print(f"  --> un-marked images are still in [{all_images_path}]: {length_of_unmarked_images}")
print(f"--> num of empty xml file: {num_empty_xml_file}")

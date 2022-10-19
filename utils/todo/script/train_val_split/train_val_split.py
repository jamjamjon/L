# encoding: utf-8



# 运行前先把当前目录的train 和 val目录删掉
# 本文件用于拆分images和xml文件，拆分为"train/images", "train/xmls" 和 "val/images", "val/xmls"


import os
import shutil
import sys
import random

pwd = os.getcwd()


images_dir = os.path.join(pwd, "images")
annotations_dir = os.path.join(pwd, "annotations")

train_images_dir = "train/images"
train_xml_dir = "train/xmls"
val_images_dir = "val/images"
val_xml_dir = "val/xmls"

#
train_split_rate = 0.82

all_images = os.listdir(images_dir)
num_images = len(all_images)
num_train_images = int(num_images * train_split_rate)
num_val_images = num_images - num_train_images

print(f"all images number:{num_images}")
print(f"train number: {num_train_images}")
print(f"val number: {num_val_images}")

train_samples_id = random.sample(range(num_images), num_train_images)
val_samples_id = list(set(range(num_images-1)) - set(train_samples_id))
# print("train samples:", train_samples_id)
# print("val samples:", val_samples_id)

# make dirs
os.makedirs(train_images_dir)
os.makedirs(train_xml_dir)
os.makedirs(val_images_dir)
os.makedirs(val_xml_dir)


# train images & xmls copy
for train_id in train_samples_id:
    
    image_name = all_images[train_id]
    xml_name = image_name.strip().split(".")[0] + ".xml"
    
    image_path = os.path.join(images_dir, image_name)
    xml_path = os.path.join(annotations_dir, xml_name)  

    shutil.copy(image_path, train_images_dir)
    shutil.copy(xml_path, train_xml_dir)


# val images & xmls copy
for val_id in val_samples_id:
    
    image_name = all_images[val_id]
    xml_name = image_name.strip().split(".")[0] + ".xml"
    
    image_path = os.path.join(images_dir, image_name)
    xml_path = os.path.join(annotations_dir, xml_name)  

    shutil.copy(image_path, val_images_dir)
    shutil.copy(xml_path, val_xml_dir)

print("copy done")


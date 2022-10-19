# encoding: UTF-8

import xml.etree.ElementTree as ET
import pickle
import string
import os
import shutil
from os import listdir, getcwd
from os.path import join
   
 
# classes
# classes = ["person","safety_belt"]
classes = ["person_head"]

# 先手动创建各个文件夹，名字如下：
# - xml文件夹名
xmls_file_name = {
    "train": "train_imageXML",
    "val": "validate_imageXML",
    "add_more": "xml"
}


# - labels文件夹名
labels_file_name = {
    "train": "train_labels",
    "val": "validate_labels",
    "add_more": "labels"
}

# - image图像文件夹名
image_files = {
    "train": "train_images",
    "val": "validate_images",
    "add_more": "images"      
}

# 导出图片路径 output file path
output_paths = {
    "train": "trainImagePath.txt",
    "val": "validateImagePath.txt",
    "add_more": "image_path.txt"
}




def convert(size, box):
    dw = 1./size[0]
    dh = 1./size[1]
    x = (box[0] + box[1])/2.0
    y = (box[2] + box[3])/2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)
 
def convert_annotation(xml_path, txt_path):

    in_file = open(xml_path)
    # out_file = open(txt_path, 'w')
    out_file = open(txt_path, 'a')

    tree = ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find("width").text)
    h = int(size.find("height").text)

    
    for obj in root.iter('object'):
        difficult = obj.find('difficult').text
        cls = obj.find('name').text
        if cls not in classes or int(difficult) == 1:
            continue

        cls_id = classes.index(cls)
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
        bb = convert((w,h), b)
        out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')
    out_file.close()

# generate lebels/xxx.txt
def labels_generate(xmls_file_name, labels_file_name):
    pwd = getcwd()
    xmls_dir = os.path.join(pwd, xmls_file_name)
    if not os.path.exists(os.path.join(pwd, labels_file_name)):
        temp_labels_dir = xmls_file_name + "_labels"
        os.mkdir(temp_labels_dir)
        labels_dir = os.path.join(pwd, temp_labels_dir)
    else:
        labels_dir = os.path.join(pwd, labels_file_name)


    for item in os.listdir(xmls_dir):
        xml_path = os.path.join(xmls_dir, item)

        txt_path = os.path.join(labels_dir, item[:-4]+'.txt')
        
        convert_annotation(xml_path, txt_path)

# generate images_path.txt(train & val)
def images_path_generate(image_file, save_out, re_write=False):
    pwd = getcwd()

    if re_write:
        f = open(save_out, "w+")
    else:
        f = open(save_out, "a+")


    directory = os.path.join(pwd, image_file)
    for path in os.listdir(directory):
        image_path = os.path.join(directory, path)
        f.write(image_path + "\n")
    f.close()


## for train file
# labels_generate(xmls_file_name["train"], labels_file_name["train"])
# images_path_generate(image_file=image_files["train"], save_out=output_paths["train"], re_write=True)

## for validation file
#labels_generate(xmls_file_name["val"], labels_file_name["val"])
#images_path_generate(image_file=image_files["val"], save_out=output_paths["val"], re_write=True)

# for adding more data
labels_generate(xmls_file_name["add_more"], labels_file_name["add_more"])
images_path_generate(image_file=image_files["add_more"], save_out=output_paths["add_more"], re_write=True)




# def generate_all(kind, re_write=True):

#     labels_generate(xmls_file_name[kind], labels_file_name[kind])
#     images_path_generate(image_file=image_files[kind], save_out=output_paths[kind], re_write=re_write)

# def adding_more_data(From, to, re_write=False):
#     images_path_generate(image_file=image_files[From], save_out=output_paths[to], re_write=re_write)


# generate_all(kind="train", re_write=True)
# generate_all(kind="val", re_write=True)
# generate_all(kind="add_more", re_write=True)
# adding_more_data(From="add_more", to="train")


print("done")



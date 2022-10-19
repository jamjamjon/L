import xml.etree.ElementTree as ET
import os
import shutil


#　默认属性包括[person, head, helmet]
# 此文件用来筛选其中包含某个属性的xml和images，
# 结果复制到filtered_images 和 filtered_annotations

xml_dir = "annotations"
image_dir = "images"

filtered_image_dir = "filtered_images"
filtered_xml_dir = "filtered_annotations"


# 过滤出来包含此属性的xmls和images
target = "head" 


# 1、找是否有head
# 2、按照image name 复制 image和xml


# get list
xml_list = os.listdir(xml_dir)
print(f"num_xml_list: {len(xml_list)}")

# make dir for save out
if not os.path.exists(filtered_image_dir):
    os.mkdir(filtered_image_dir)
if not os.path.exists(filtered_xml_dir):
    os.mkdir(filtered_xml_dir)



num_filtered_item = 0

# main()
for idx, xml_file in enumerate(xml_list):

    target_exist_flag = False

    # input path
    xml_path = os.path.join(xml_dir, xml_file)
    
    # xml tree
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # image path
    file_name = xml_file.strip().split(".")[0]
    image_path = os.path.join(image_dir, file_name) + ".png"

    # tag modified 
    for obj in root.iter('object'):

        name_tag = obj.find('name')

        if name_tag.text == target:
            target_exist_flag = True



    if target_exist_flag:

        # cp images & xml
        shutil.copy(image_path, filtered_image_dir)
        shutil.copy(xml_path, filtered_xml_dir)
        num_filtered_item += 1

        # print(f"{image_path}  -->  filtered_image_dir")
    

    # if idx >= 5:
    #     break


print(f"num_filtered: {num_filtered_item}")
print("done")
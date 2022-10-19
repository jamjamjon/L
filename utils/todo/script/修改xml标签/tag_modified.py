import xml.etree.ElementTree as ET
import os
import shutil


xml_dir = "xmls"
output_dir = "xml_modified"


# get list
xml_list = os.listdir(xml_dir)
print(f"num_xml_list: {len(xml_list)}")

# make dir for save out
if not os.path.exists(output_dir):
    os.mkdir(output_dir)


# main()
for xml_file in xml_list:

    # input path
    input_path = os.path.join(xml_dir, xml_file)
    
    # xml tree
    tree = ET.parse(input_path)
    root = tree.getroot()

    # output path
    file_name = xml_file.strip().split(".")[0]
    save_out_path = os.path.join(output_dir, file_name)

    # tag modified 
    for obj in root.iter('object'):

        name_tag = obj.find('name')
        if name_tag.text == "person":
            name_tag.text = "head"
        if name_tag.text == "hat":
            name_tag.text = "head-hat"


        # print(obj.find('name').text)

    tree.write(save_out_path + ".xml", "utf-8")


print("done")

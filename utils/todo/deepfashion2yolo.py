import numpy as np
from PIL import Image
import os
import json 
import glob
import argparse
from tqdm import tqdm



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, help="Folder containing image files")
    args = parser.parse_args()
    directory = args.input + '/labels/'
    if not os.path.exists(directory):
        os.makedirs(directory)
    annos_list = glob.glob(args.input + '/annos/*.json')

    for anno in tqdm(annos_list):
        len_split = len(anno.split('/'))
        file_name_jpg = anno.split('/')[len_split-1].split('.')[0]
        file_nanme_jpg_full = anno.split('annos')[0] + 'image/' + file_name_jpg + '.jpg'
        file_name_label_txt = directory + file_name_jpg + '.txt'
        img = Image.open(file_nanme_jpg_full)
        img_width = img.size[0]
        img_height = img.size[1]
        # print (len_split, img.size, file_nanme_jpg_full, file_name_label_txt)
        file = open(file_name_label_txt, "a")
        with open(anno) as json_file:
            data = json.load(json_file)
            for i in range(10):
                key = 'item{}'.format(i + 1)
                if key in data:
                    item_dic = data[key]
                    cat_id = item_dic['category_id']
                    bbox = item_dic['bounding_box']
		
                    # (xmin, ymin, xmax, ymax) => bbox[0], bbox[1], bbox[2], bbox[3]
                    # string1 = str(cat_id-1)
                    # string2 = str(bbox[0]/img_width)
                    # string3 = str(bbox[1]/img_height)
                    # string4 = str((bbox[2]-bbox[0])/img_width)
                    # string5 = str((bbox[3]-bbox[1])/img_height)


                    # obj: <object-class> <x_center> <y_center> <width> <height>
                    string1 = str(cat_id - 1)
                    w = bbox[2] - bbox[0]
                    h = bbox[3] - bbox[1]
                    string2 = str((bbox[0] + w // 2) / img_width)                  # str(bbox[0] / img_width)  # cx
                    string3 = str((bbox[1] + h // 2) / img_height)                  # str(bbox[1] / img_height)   # cy
                    string4 = str(w / img_width)                  # str((bbox[2]-bbox[0])/img_width)  # w
                    string5 = str(h / img_height)                  # str((bbox[3]-bbox[1])/img_height) # h


                    


                    file.write(string1 + ' ' + string2 + ' ' + string3 + ' ' + string4 + ' ' + string5 + '\n')
                    # print(cat_id, bbox)

        file.close()

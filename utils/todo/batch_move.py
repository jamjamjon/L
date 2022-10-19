# # general Py module
# from general import (get_corresponding_label_path, Colors, load_img_label_list, set_logging, 
#                     IMG_FORMAT, is_point_in_rect, LOGGER, img_label_dir_cleanup
#                     )
import rich
from pathlib import Path
import os
import sys
import re
import shutil



def cmp(s, r=re.compile('([0-9]+)')):
    return [int(x) if x.isdigit() else x.lower() for x in r.split(s)]




# step 1 
INPUT_IMG_DIR = "/home/user/zhangjian/MLOps/Datasets/rider_vehicle_hemlet_head/workspace/head-helmet/patch01_17"
IMAGE_PATH_LIST = []

rich.print(f"[bold green]loading data...")
for f in sorted(os.listdir(INPUT_IMG_DIR), key=cmp):    
    f_path = os.path.join(INPUT_IMG_DIR, f)
    # 如果是文件夹，不读，continue
    if os.path.isdir(f_path):   
        continue

    # check if it is an image (opencv imread)  => IMAGE_PATH_LIST
    # to do: 太费时间，直接后缀判断 + 错误记录
    if Path(f).suffix in ['.jpg', '.png', '.jpeg']:
        IMAGE_PATH_LIST.append(f_path)

# rich.print(IMAGE_PATH_LIST[:220])

# step 2
if not Path('move_dir').exists():
    Path('move_dir').mkdir()
else:
    exit('dir already exits')

# step 3
for idx in range(220):
    img_p = IMAGE_PATH_LIST[idx]
    label_p = IMAGE_PATH_LIST[idx].replace('.jpg', '.txt')
    shutil.copy(img_p, 'move_dir')
    if Path(label_p).exists():
        shutil.copy(label_p, 'move_dir')
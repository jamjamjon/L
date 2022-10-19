
import argparse
import glob
import json
import os
import re
import cv2
import numpy as np
from tqdm import tqdm
from lxml import etree
import xml.etree.cElementTree as ET
import rich
from pathlib import Path
import sys
import shutil
import random
import time
import logging


#----------------------------
#  new v1.2
#----------------------------

# video record (待完善)



#----------------------------
#  to do  v1.1
#----------------------------
# (done)img & label dir clean up
# dir imcrement

# into project

# simplify
# key combination

#----------------
# maybe todo
#----------------
# --get_path   
# --video2img
# --img2video
# --dir_combine
# --rename_dir_item_name(random_name & dir name)
#----------------------------


#--------------------------------------------
#       ADD TO PYTHON_PATH
#--------------------------------------------
FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]   # FILE.parent 
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
# ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # abs path => relative
#--------------------------------------------


# ----------------options ------------------------
def parse_opt():
    parser = argparse.ArgumentParser(description='Open-source image labeling tool')
    parser.add_argument('--img-dir', default='img-dir', type=str, help='Path to input directory')
    parser.add_argument('--label-dir', default='', type=str, help='Path to output directory')
    parser.add_argument('--mv-dir', default="moved_dir", type=str, help='mv-dir to save moved data[img, label]')
    parser.add_argument('--mark-mode', default=False, type=bool, help='mark or insepect(default)')

    parser.add_argument('--classes-txt', default='class_list.txt', type=str, help='classes list text')
    parser.add_argument('--hide-label', default=False, type=bool, help='hide label or not')
    parser.add_argument('--hide-num-bboxes', default=False, type=bool, help='show num of bboxes in the img')
    parser.add_argument('--blink-bboxes', default=False, type=bool, help='blink bboxes')
    parser.add_argument('--cls', type=int, default=None, help='filter by class: --classes 0, or --classes 0 2 3')    
    parser.add_argument('--mode', default='INSPECT_MARK', type=str, help='info(img and label count), cleanup(img_label_pair), inspect_mark(gt_bbox_check), copy_valid(post-solve mode)')

    # for record video
    # parser.add_argument('--video-rec', action='store_true', help='record video')
    parser.add_argument('--video-rec', default='', type=str, help='record video')
    parser.add_argument('--video-rec-saveout', type=str, default= "video_rec_1.mp4", help='record video')

    

    opt = parser.parse_args()
    rich.print(f"{opt}\n")

    return opt

# options
opt = parse_opt()


# ---------Global Variables---------

# windows 
WINDOW_NAME = 'MLOps-Dataset-Jamjon'
WINDOW_INIT_WIDTH = 1000    # initial window width
WINDOW_INIT_HEIGHT = 700    # initial window height

# tracker bars
TRACKBAR_IMG = 'Images'
TRACKBAR_CLASS = 'Classes'

# dirs
INPUT_IMG_DIR  = opt.img_dir
INPUT_LABEL_DIR = opt.label_dir if opt.label_dir else INPUT_IMG_DIR
MV_DIR = opt.mv_dir

WRONG_IMG_DIR = "wrong_img_dir"

# hide label
HIDE_LABEL = opt.hide_label

# num_bboxes
HIDE_NUM_BBOXES = opt.hide_num_bboxes

# mode 
MARK_MODE = opt.mark_mode

# only show one specific class
SINGLE_CLS = opt.cls

# bboxes blink
BLINK_BBOXES = opt.blink_bboxes
BLINK_OR_NOT = False

# line thickness
LINE_THICKNESS_ADJUST = False   # line thickness adjust flag
LINE_THICKNESS = 1

# images
IMAGE_PATH_LIST = []
IMG_IDX_CURRENT = 0         # 当前的img index
IMG_IDX_LAST = 0            # last 的img index
IMG_CURRENT = None          # 当前页面显示的img
IMG_OBJECTS = []            # 当前页面总所有bbox
WRONG_IMG_SET = set()             # 无法正常读取的image

IMG_WIDTH_CURRENT = 0
IMG_HEIGHT_CURRENT = 0

# classes
CLASSES_TXT = opt.classes_txt          # classes txt
CLASS_LIST = []                         # all class ID
CLS_IDX_CURRENT = 0         # 当前的class index

# bbox status
PRVE_WAS_DOUBLE_CLICK = False   # 之前是否双击了
IS_BBOX_SELECTED = False        # 是否选中了当前bbox
SELECTED_BBOX = -1              # 选中后，IMG_OBJECTS中的第 idx 个

# point_xy & mouse_xy
MOUSE_X = 0
MOUSE_Y = 0
POINT_1 = (-1, -1)
POINT_2 = (-1, -1)

# imag format
IMG_FORMAT = ('.jpg', '.jpeg', '.png', '.bmp')

# color shuffle 
COLOR_PALETTE = None


#--------------------------------------------
#          Functions
#--------------------------------------------


# √ Check if a point belongs to a rectangle
def is_point_in_rect(x, y, l, t, r, b):
    return l <= x <= r and t <= y <= b


# √ display text in the [overlap, terminal, status_bar]
def print_info(text="for example", ms=1000, where=None):
    global WINDOW_NAME

    if where == 'Overlay':
        cv2.displayOverlay(WINDOW_NAME, text, ms)
    elif where == 'Statusbar':
        cv2.displayStatusBar(WINDOW_NAME, text, ms)
    else:
        # rich.print(f"==>{text}")
        LOGGER.info(f"{text}")


# set current img index & imshow image
def set_img_index(x):

    # current_image_index, current_image, window_name, image_path_list, wrong_image_set(image which opencv can't read)
    global IMG_IDX_CURRENT, IMG_CURRENT, WINDOW_NAME, IMAGE_PATH_LIST, WRONG_IMG_SET

    IMG_IDX_CURRENT = x
    img_path = IMAGE_PATH_LIST[IMG_IDX_CURRENT]
    
    # opencv read img
    IMG_CURRENT = cv2.imread(img_path)
    if IMG_CURRENT is None:
        
        # create a empty img
        IMG_CURRENT = np.ones((1000, 1000, 3))

        # show notification
        cv2.putText(IMG_CURRENT, "Wrong image format! Tt will delete after pressing ESC.", 
                    (10, IMG_CURRENT.shape[0]//2), cv2.FONT_HERSHEY_SIMPLEX, 
                    1, (0,0,0), thickness=2, lineType=cv2.LINE_AA)

        # save wrong images path, delete all these image at the end of the program
        WRONG_IMG_SET.add(img_path)

    text = f"Image: {str(IMG_IDX_CURRENT)}/{str(IMG_COUNT)}"
    print_info(text, ms=1000, where="Overlay")


# set current class index 
def set_class_index(x):

    # current_class_index, class_list, window_name
    global CLS_IDX_CURRENT, CLASS_LIST, WINDOW_NAME

    CLS_IDX_CURRENT = x
    text = f"Selected class: {CLASS_LIST[CLS_IDX_CURRENT]} ({str(CLS_IDX_CURRENT)}/{str(CLS_COUNT)})" 
    print_info(text, ms=1000, where="Overlay")


# index -1
def decrease_index(current_idx, max_idx):
    current_idx -= 1
    if current_idx < 0:
        current_idx = max_idx
    return current_idx

# index +1
def increase_index(current_idx, max_idx):
    current_idx += 1
    if current_idx > max_idx:
        current_idx = 0
    return current_idx


# cursor line for drawing
def draw_cursor_line(img, x, y, height, width, color, line_thickness):
    cv2.line(img, (x, 0), (x, height), color, line_thickness)
    cv2.line(img, (0, y), (width, y), color, line_thickness)


# YOLO format => (cx, cy, w, h)
def yolo_format(cls_idx, point_1, point_2, img_w, img_h):

    cx = float((point_1[0] + point_2[0]) / (2.0 * img_w) )
    cy = float((point_1[1] + point_2[1]) / (2.0 * img_h))
    w = float(abs(point_2[0] - point_1[0])) / img_w
    h = float(abs(point_2[1] - point_1[1])) / img_h
    items = map(str, [cls_idx, cx, cy, w, h])
    return ' '.join(items)


# read label.txt and draw all bboxes
# todo : rename
def draw_bboxes_from_file(img, label_path, width, height, colors, line_thickness, single_cls=None, hide_label=False):

    # current_img_all_bboxes, is_current_bbox_selected, index_of_select_bbox, class_list
    global IMG_OBJECTS, IS_BBOX_SELECTED, SELECTED_BBOX, CLASS_LIST

    # initial objexts
    IMG_OBJECTS = []

    # Drawing bounding boxes from the YOLO files
    # if os.path.isfile(label_path):
    if Path(label_path).is_file():
        
        # read label file
        with open(label_path) as f:
            for idx, line in enumerate(f):
    
                # (id, cx, cy, w, h) => (id, name, xmin, ymin, xmax, ymax)
                classId, centerX, centerY, bbox_width, bbox_height = line.split()
                bbox_width = float(bbox_width)
                bbox_height  = float(bbox_height)
                centerX = float(centerX)
                centerY = float(centerY)

                class_index = int(classId)
                class_name = CLASS_LIST[class_index]
                xmin = int(width * centerX - width * bbox_width/2.0)
                xmax = int(width * centerX + width * bbox_width/2.0)
                ymin = int(height * centerY - height * bbox_height/2.0)
                ymax = int(height * centerY + height * bbox_height/2.0)

                # show single class
                if single_cls is not None:
                    # rich.print(f"single_cls is not none! {single_cls}")
                    if str(class_index) != str(single_cls):
                        continue    

                # all object 
                IMG_OBJECTS.append([class_index, xmin, ymin, xmax, ymax])

                # draw bbox
                color = colors(int(class_index), bgr=False)
                cv2.rectangle(img, (xmin, ymin), (xmax, ymax), color, line_thickness, cv2.LINE_AA)

                # hide label or not
                if not hide_label:
                    font=cv2.FONT_HERSHEY_SIMPLEX
                    font_thickness = max(line_thickness - 1, 1)  # font thickness
                    fontScale = line_thickness / 3
                    text_w, text_h = cv2.getTextSize(class_name, 0, fontScale=fontScale, thickness=font_thickness)[0]  # text width, height
 
                    # check if outside of img
                    outside = ymin - text_h - 3 >= 0  # label fits outside box
                    # cv2.rectangle(img, (xmin, ymin), (xmax, ymax), color, -1, cv2.LINE_AA)  # filled
                    cv2.putText(img, class_name, (xmin, ymin - 2 if outside else ymin + text_h + 3), font, fontScale, color, thickness=line_thickness, lineType=cv2.LINE_AA)
    return img



# left double click in bbox => select the smallest bbox, and set that bbox
# todo: line_thickness
def set_selected_bbox(set_cls_trackbar=True):
    global IS_BBOX_SELECTED, SELECTED_BBOX, IMG_OBJECTS, LINE_THICKNESS

    # smallest bbox flag
    smallest_area = -1

    # if clicked inside multiple bboxes selects the smallest one
    for idx, obj in enumerate(IMG_OBJECTS):
        ind, x1, y1, x2, y2 = obj

        # line width (consider) 
        margin = 2 * LINE_THICKNESS
        x1 = x1 - margin  
        y1 = y1 - margin
        x2 = x2 + margin
        y2 = y2 + margin

        # is mouse_xy in bbox
        if is_point_in_rect(MOUSE_X, MOUSE_Y, x1, y1, x2, y2):

            IS_BBOX_SELECTED = True     # set bbox selected
            tmp_area = abs(x2 - x1) * abs(y2 - y1)  # area of bbox

            if tmp_area < smallest_area or smallest_area == -1:
                smallest_area = tmp_area
                SELECTED_BBOX = idx
                if set_cls_trackbar: 
                    cv2.setTrackbarPos(TRACKBAR_CLASS, WINDOW_NAME, ind)    # 将track Bar的类别移动到所属class



# todo: 找出删除了的或者修改了类别的那一行idx
def findIndex(bbox_with_id):
    global IMG_OBJECTS
 
    ind = -1
    ind_ = 0

    for listElem in IMG_OBJECTS:
        if listElem == bbox_with_id:
            ind = ind_
            return ind
        ind_ = ind_+1

    return ind


# edit bbox
# todo : rename, width, height
def edit_bbox(bbox_with_id, action):
    global IMAGE_PATH_LIST, IMG_IDX_CURRENT, INPUT_LABEL_DIR, IMG_WIDTH_CURRENT, IMG_HEIGHT_CURRENT

    ''' 
    print(f"action : {action}")
    action = [`delete`] [`change_class:new_class_index`]
    '''
    
    if 'change_class' in action:
        new_class_index = int(action.split(':')[1])


    # initialize bboxes_to_edit_dict
    bboxes_to_edit_dict = {}                                # {path: [id, x,y,x,y]}
    current_img_path = IMAGE_PATH_LIST[IMG_IDX_CURRENT]
    bboxes_to_edit_dict[current_img_path] = bbox_with_id     # {'4/2.jpg': [0, 144, 970, 386, 1468]}


    # add elements to bboxes_to_edit_dict
    # loop through bboxes_to_edit_dict and edit the corresponding annotation files
    for path in bboxes_to_edit_dict:
        bbox_with_id = bboxes_to_edit_dict[path]        # [0, 144, 970, 386, 1468]
        cls_idx, xmin, ymin, xmax, ymax = map(int, bbox_with_id)

        ann_path = get_corresponding_label_path(path, INPUT_LABEL_DIR)
        with open(ann_path, 'r') as old_file:
            lines = old_file.readlines()

        yolo_line = yolo_format(cls_idx, (xmin, ymin), (xmax, ymax), IMG_WIDTH_CURRENT, IMG_HEIGHT_CURRENT) # TODO: height and width ought to be stored
        
        # 找出删除了的或者修改了类别的那一行idx
        ind = findIndex(bbox_with_id)

        # re-write label(.txt)
        with open(ann_path, 'w') as new_file:
            for idx, line in enumerate(lines):
                if idx != ind:              # 如果未修改的行，直接写入
                    new_file.write(line)
                
                elif 'change_class' in action:  # 如果是修改的行，并且修的是类别，将更换后新的类别写入
                    new_yolo_line = yolo_format(new_class_index, (xmin, ymin), (xmax, ymax), IMG_WIDTH_CURRENT, IMG_HEIGHT_CURRENT)
                    new_file.write(new_yolo_line + '\n')
                
                # 如果不属于以上情况，那么就是删除，则不写入该行
                


# mouse callback function
def mouse_listener(event, x, y, flags, param):
    global IS_BBOX_SELECTED, PRVE_WAS_DOUBLE_CLICK, MOUSE_X, MOUSE_Y, POINT_1, POINT_2, IMG_OBJECTS, MARK_MODE

    # mark mode
    if MARK_MODE:
        # move:  MOUSE_X mouse_y
        if event == cv2.EVENT_MOUSEMOVE:
            MOUSE_X = x
            MOUSE_Y = y

        # left button double click -> select object
        elif event == cv2.EVENT_LBUTTONDBLCLK:
            PRVE_WAS_DOUBLE_CLICK = True    
            POINT_1 = (-1, -1)  # reset top_left point => ponit_1

            # if clicked inside a bounding box we set that bbox
            set_selected_bbox(set_cls_trackbar=True)

        # right button pressed down
        elif event == cv2.EVENT_RBUTTONDOWN:  #     EVENT_RBUTTONUP 
            set_selected_bbox(set_cls_trackbar=False)   # cancel set class
            
            # 如果选中了bbox，右键删除该选中的框
            if IS_BBOX_SELECTED:
                bbox_with_id = IMG_OBJECTS[SELECTED_BBOX]
                edit_bbox(bbox_with_id, 'delete')        # to do
                IS_BBOX_SELECTED = False

        # 左键按下
        elif event == cv2.EVENT_LBUTTONDOWN:

            # 前一次是双击，单击取消
            if PRVE_WAS_DOUBLE_CLICK:
                PRVE_WAS_DOUBLE_CLICK = False

            else:   # Normal left click
                # 如果鼠标在选中的框内
                if POINT_1[0] == -1:
                    # selected? 
                    if IS_BBOX_SELECTED:
                        IS_BBOX_SELECTED = False
                    else:
                        # first click (start drawing a bounding box or delete an item)
                        POINT_1 = (x, y)
                else:
                    # minimal size for bounding box to avoid errors
                    threshold = 5
                    if abs(x - POINT_1[0]) > threshold or abs(y - POINT_1[1]) > threshold:
                        # second click
                        POINT_2 = (x, y)



# when select(double click)  => hight light bboxes
def highlight_selected_bbox(img, alpha=1, beta=0.5, gamma=0):
    global IMG_OBJECTS, SELECTED_BBOX, LINE_THICKNESS

    # line width
    lw = LINE_THICKNESS // 2


    for idx, obj in enumerate(IMG_OBJECTS):
        ind, x1, y1, x2, y2 = obj
        if idx == SELECTED_BBOX:
            # copy original image
            mask = np.zeros((img.shape), dtype=np.uint8)
            cv2.rectangle(mask, (x1-lw, y1-lw), (x2+lw, y2+lw), (255, 255, 255, 0), -1, cv2.LINE_AA)
            img_weighted = cv2.addWeighted(img, alpha, mask, beta, gamma)
            

    return img_weighted


# key for sort
# to do
def cmp(s, r=re.compile('([0-9]+)')):
    return [int(x) if x.isdigit() else x.lower() for x in r.split(s)]


# img_path => label_path(txt)
def get_corresponding_label_path(img_path, output_dir):
    label_name = Path(img_path).stem + '.txt'
    saveout = Path(output_dir) / label_name 
    return str(saveout)

	

# colors palette
class Colors:
    '''
        # hex 颜色对照表    https://www.cnblogs.com/summary-2017/p/7504126.html
        # RGB的数值 = 16 * HEX的第一位 + HEX的第二位
        # RGB: 92, 184, 232 
        # 92 / 16 = 5余12 -> 5C
        # 184 / 16 = 11余8 -> B8
        # 232 / 16 = 14余8 -> E8
        # HEX = 5CB8E8
    '''

    # def __init__(self, random=0, shuffle=False):
    def __init__(self, shuffle=False):
        # hex = matplotlib.colors.TABLEAU_COLORS.values()
        hex = ('33FF00', '9933FF', 'CC0000', 'FFCC00', '99FFFF', '3300FF', 'FF3333', # new add
               'FF3838', 'FF9D97', 'FF701F', 'FFB21D', 'CFD231', '48F90A', '92CC17', '3DDB86', 
               '1A9334', '00D4BB', '2C99A8', '00C2FF', '344593', '6473FF', '0018EC', '8438FF', 
               '520085', 'CB38FF', 'FF95C8', 'FF37C7')
        
        # shuffle color 
        if shuffle:
            hex_list = list(hex)
            random.shuffle(hex_list)
            hex = tuple(hex_list)

        self.palette = [self.hex2rgb('#' + c) for c in hex]
        self.n = len(self.palette)
        # self.b = random   # also for shuffle color 


    def __call__(self, i, bgr=False):        
        c = self.palette[int(i) % self.n]
        return (c[2], c[1], c[0]) if bgr else c

    @staticmethod  
    def hex2rgb(h):  # int('CC', base=16) 将16进制的CC转成10进制 
        return tuple(int(h[1 + i:1 + i + 2], 16) for i in (0, 2, 4))
        
        


# img_list & label_list, relative path
def load_img_label_list(img_dir, label_dir, img_format, info=True):
    image_list = [x for x in Path(img_dir).iterdir() if x.suffix in img_format]
    label_list = list(Path(INPUT_LABEL_DIR).glob("*.txt"))
    
    if info:
        # LOGGER.info(f"Original Images count: {len(image_list)}")
        # LOGGER.info(f"original Labels count: {len(label_list)}")
        rich.print(f"[green]==>Valid Labels count: {len(label_list)}")
        rich.print(f"[green]==>Valid Images count: {len(image_list)}")

    return image_list, label_list


# logging -> LOGGER
def set_logging(name=None, verbose=True):
    # Sets level and returns logger

    # time + file + line + level + msg
    # fmt = f"[%(asctime)s | %(filename)s | line:%(lineno)d | %(levelname)s] => %(message)s"
    fmt = f"[%(asctime)s | %(levelname)s] => %(message)s"

    logging.basicConfig(format=fmt, level=logging.INFO if verbose else logging.WARNING)
    return logging.getLogger(name)


# video record
def video_record(video_path, saveout):
    videoCapture = cv2.VideoCapture(video_path)
    fps = int(videoCapture.get(cv2.CAP_PROP_FPS))
    w = int(videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print("video size:", (w, h))
    video_size = (w, h)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')


    # SAVE-DIR increment
    sp = Path(saveout)
    if sp.exists():
        # idx = sp.stem.split('_')[-1] + 1   # video_rec_10,   +1 
        # new_stem = sp.stem[:-2] + 
        saveout = Path(saveout).with_name(f"{sp.stem}_1{sp.suffix}")


    video_writer = cv2.VideoWriter(str(saveout), fourcc, fps, video_size)


    while True:
        ret, frame = videoCapture.read()
        if ret:
            cv2.imshow('frame', frame)
            key = cv2.waitKey(1)
            if key == ord('Q'):
                break
            video_writer.write(frame)


        else:
            print('can not read frame!')
            break

    videoCapture.release()


# ---------------------------------------------------
#   main
#--------------------------------------------------
if __name__ == '__main__':


    # instantiate LOGGER
    LOGGER = set_logging(__name__) 
    
    # -------------------------------------
    # record video 
    # -------------------------------------
    if opt.video_rec:
        video_record(opt.video_rec, opt.video_rec_saveout)




    # -------------------------------------
    # mode: info 
    # -------------------------------------
    if opt.mode in ("info", "INFO"):

        rich.print(f"[bold green]-------[INFO MODE]-------\n")
        _, _ = load_img_label_list(INPUT_IMG_DIR, INPUT_LABEL_DIR, IMG_FORMAT, True)


    # -------------------------------------
    # mode: check img_label_pair 
    # 1. 检查是否所有的img都有对应lable；  done
    # 2. 是否所有的label都有对应img; 
    # 3. 并且检查是否所有的label都是有内容的
    # 将不满足的img和label移除到 mv_dir
    # 4. img dir 仅仅可以存在支持的IMG_FORMAT文件
    # 5. label dir 仅仅可以存在.txt文件
    # -------------------------------------
    if opt.mode in ("clean", "cleanup"):

        rich.print(f"[bold green]-------[CHECK MODE]-------\n")

        image_list, label_list = load_img_label_list(INPUT_IMG_DIR, INPUT_LABEL_DIR, IMG_FORMAT, True)

        # create mv-dir if not exist
        if not Path(MV_DIR).exists():
            Path(MV_DIR).mkdir()


        # 1. 检查是否所有的image都有对应的label
        # has img, no label => remove img
        rich.print(f"[bold gold1 italic]==>1. Check if all images has corresponding label...")
        for image_path in tqdm(image_list):

            # has corresponding label, continue
            if Path(INPUT_LABEL_DIR) / (image_path.stem + '.txt') in label_list:
                continue

            # else remove img
            # rich.print(f"[bold red]No corresponding label: {image_path}, moved.")
            LOGGER.warning(f"No corresponding label: {image_path}, moved.")
            shutil.move(str(image_path), MV_DIR)  


        # 2. 剩余的所有image都有对应的label，size(img) <= size(label)
        # 检查是否所有的label都有对应的image
        # has label, no img  => remove label 
        rich.print(f"[bold gold1 italic]==>2. Check if all labels has corresponding image...")
        
        image_list, label_list = load_img_label_list(INPUT_IMG_DIR, INPUT_LABEL_DIR, IMG_FORMAT, False)
        for label_path in tqdm(label_list):      

            # remove label file without corresponding img
            if Path(INPUT_IMG_DIR) / (label_path.stem + '.png') in image_list:
                continue
            elif Path(INPUT_IMG_DIR) / (label_path.stem + '.jpg') in image_list:
                continue
            elif Path(INPUT_IMG_DIR) / (label_path.stem + '.jpeg') in image_list:
                continue
            else:
                # rich.print(f"[bold red]No corresponding img: {label_path}, moved.")
                LOGGER.warning(f"No corresponding img: {label_path}, moved.")
                shutil.move(str(label_path), MV_DIR)

        # 3. 检查所有label都有内容，不是空的; 此刻，size(img) = size(label)
        # empty label => remove img & label
        rich.print(f"[bold gold1 italic]==>3. Check if all labels are not empty...")
        image_list, label_list = load_img_label_list(INPUT_IMG_DIR, INPUT_LABEL_DIR, IMG_FORMAT, False)
        for label_path in tqdm(label_list):   

            # size < 10 => empty
            if os.path.getsize(str(label_path)) < 10:

                # revome label & img
                # rich.print(f"[bold red]Empty label file: {label_path}, moved.")
                LOGGER.warning(f"Empty label file: {label_path}, moved.")
                shutil.move(str(label_path), MV_DIR)
                label_list.remove(label_path)

                # remove corresponding img
                img_path_png = Path(INPUT_IMG_DIR) / (label_path.stem + '.png')
                img_path_jpg = Path(INPUT_IMG_DIR) / (label_path.stem + '.jpg')
                img_path_jpeg = Path(INPUT_IMG_DIR) / (label_path.stem + '.jpeg')

                # PNG
                if img_path_png in image_list:
                    # rich.print(f"[bold red]=>corresponding img file: {label_path}, moved.")
                    LOGGER.warning(f"-> corresponding img file: {img_path_png}, moved.")
                    shutil.move(str(img_path_png), MV_DIR)
                    
                # JPG
                elif img_path_jpg in image_list:
                    # rich.print(f"[bold red]=>corresponding img file: {label_path}, moved.")
                    LOGGER.warning(f"-> corresponding img file: {img_path_jpg}, moved.")
                    shutil.move(str(img_path_jpg), MV_DIR)
                    
                # JPEG
                elif img_path_jpeg in image_list:
                    # rich.print(f"[bold red]=>corresponding img file: {label_path}, moved.")
                    LOGGER.warning(f"-> corresponding img file: {img_path_jpeg}, moved.")
                    shutil.move(str(img_path_jpeg), MV_DIR)
                    

        # 4. clean up IMG-dir, Label-dir
        rich.print(f"[bold gold1 italic]==>4. Clean up img-dir * label-dir...")
        item_list = list(Path(INPUT_IMG_DIR).iterdir())
        for p in tqdm(item_list):
            if p.suffix in list(IMG_FORMAT) + ['.txt']:
                continue
            LOGGER.warning(f"Not support format: {p.suffix} --> {p}, moved.")
            shutil.move(str(p.resolve()), MV_DIR)

        # show after check result info
        image_list, label_list = load_img_label_list(INPUT_IMG_DIR, INPUT_LABEL_DIR, IMG_FORMAT, False)
        rich.print(f"[green]==>Valid Labels count: {len(label_list)}")
        rich.print(f"[green]==>Valid Images count: {len(image_list)}")
        # LOGGER.info(f"Valid Labels count: {len(label_list)}")
        # LOGGER.info(f"Valid Images count: {len(image_list)}")


    # -------------------------------------
    # mode: inspect & mark
    # -------------------------------------
    if opt.mode == "INSPECT_MARK":

        rich.print(f"[bold green]-------[INSPECT_MARK MODE]-------\n")

        # init window with overlap
        try:
            cv2.namedWindow('Test')   
            cv2.displayOverlay('Test', 'Test overlap', 10)  
            cv2.displayStatusBar('Test', 'Test status bar', 10)
        except cv2.error:
            print('-> Please ignore this error message\n')
        cv2.destroyAllWindows()

        # read all input images
        rich.print(f"[bold green]loading data...")
        for f in sorted(os.listdir(INPUT_IMG_DIR), key=cmp):    
            f_path = os.path.join(INPUT_IMG_DIR, f)
            # 如果是文件夹，不读，continue
            if os.path.isdir(f_path):   
                continue

            # check if it is an image (opencv imread)  => IMAGE_PATH_LIST
            # to do: 太费时间，直接后缀判断 + 错误记录
            if Path(f).suffix in IMG_FORMAT:
                IMAGE_PATH_LIST.append(f_path)


        # img count
        IMG_COUNT = len(IMAGE_PATH_LIST) - 1  

        # load all class name
        with open(CLASSES_TXT) as f:
            for line in f:
                CLASS_LIST.append(line.strip())
        print_info(f"CLASS_LIST: {CLASS_LIST}")

        # class count
        CLS_COUNT = len(CLASS_LIST) - 1
        if CLS_COUNT < 0:
            rich.print(f"[red bold]Error: No class in class_list.txt!")
            raise StopIteration


        # create output dir if not exist
        if not Path(INPUT_LABEL_DIR).exists():
            Path(INPUT_LABEL_DIR).mkdir()

        # create window 
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_KEEPRATIO)  # cv2.WINDOW_FREERATIO   cv2.WINDOW_KEEPRATIO
        cv2.resizeWindow(WINDOW_NAME, WINDOW_INIT_WIDTH, WINDOW_INIT_HEIGHT)

        # mouse listen callback
        cv2.setMouseCallback(WINDOW_NAME, mouse_listener)

        # trackBar of images
        cv2.createTrackbar(TRACKBAR_IMG, WINDOW_NAME, 0, IMG_COUNT, set_img_index) 
     
        # class tracker bar
        if CLS_COUNT != 0:
            cv2.createTrackbar(TRACKBAR_CLASS, WINDOW_NAME, 0, CLS_COUNT, set_class_index)

        # initialize the img index
        set_img_index(0)

        # overlay to show: help
        print_info('Press [h] for help.', ms=0, where="Overlay")

        # colors palette
        COLOR_PALETTE = Colors(shuffle=False)  


        # loop
        while True:

            # color for every class
            color = COLOR_PALETTE(int(CLS_IDX_CURRENT), bgr=False)

            # clone the img   
            tmp_img = IMG_CURRENT.copy()
            # height, width = tmp_img.shape[:2]
            IMG_HEIGHT_CURRENT, IMG_WIDTH_CURRENT = tmp_img.shape[:2]


            # bbox line-thickness
            LINE_THICKNESS = max(round(sum(tmp_img.shape) / 2 * 0.003), 2) if not LINE_THICKNESS_ADJUST else LINE_THICKNESS      # line width

            # mode: mark, inspect
            if MARK_MODE:
                # cursor line for drawing
                draw_cursor_line(tmp_img, MOUSE_X, MOUSE_Y, IMG_HEIGHT_CURRENT, IMG_WIDTH_CURRENT, color, LINE_THICKNESS)

                # show label or not when drawing
                if not HIDE_LABEL:
                    text_w, text_h = cv2.getTextSize(class_name, 
                                                     0,
                                                     fontScale=LINE_THICKNESS / 3, 
                                                     thickness=max(LINE_THICKNESS - 1, 1)
                                                     )[0]  # text width, height
                    # check if outside of img
                    outside = MOUSE_Y - text_h - 3 >= 0  # label fits outside box
                    cv2.putText(tmp_img, 
                                class_name, 
                                (MOUSE_X, MOUSE_Y - 2 if outside else MOUSE_Y + text_h + 3), 
                                cv2.FONT_HERSHEY_SIMPLEX, 
                                LINE_THICKNESS / 3, 
                                color, 
                                thickness=LINE_THICKNESS, lineType=cv2.LINE_AA)



            # current class index and it's class name
            class_name = CLASS_LIST[CLS_IDX_CURRENT]
            
            # current image path, relative path: img/img_1.jpg
            img_path = IMAGE_PATH_LIST[IMG_IDX_CURRENT]   
            
            # get get_corresponding_label_path
            label_path = get_corresponding_label_path(img_path, INPUT_LABEL_DIR)

            # status bar show [img_path] & [label_path]
            path_info = (f"[Image path]: {Path(img_path).resolve()}"
                         + "\t" * 20
                         + f"[Label path]: {Path(label_path).resolve()}"
                        )
            # cv2.displayStatusBar(WINDOW_NAME, path_info, 0)
            print_info(path_info, ms=0, where="Statusbar")

            
            # Blink bboxes
            if BLINK_BBOXES:
                if BLINK_OR_NOT == False:
                    tmp_img = draw_bboxes_from_file(tmp_img, label_path, IMG_WIDTH_CURRENT, IMG_HEIGHT_CURRENT, COLOR_PALETTE, 0, SINGLE_CLS, HIDE_LABEL)
                    BLINK_OR_NOT = True
                else:
                    tmp_img = draw_bboxes_from_file(tmp_img, label_path, IMG_WIDTH_CURRENT, IMG_HEIGHT_CURRENT, COLOR_PALETTE, LINE_THICKNESS, SINGLE_CLS, HIDE_LABEL)
                    BLINK_OR_NOT = False
            else:
                # draw already done bounding boxes
                tmp_img = draw_bboxes_from_file(tmp_img, label_path, IMG_WIDTH_CURRENT, IMG_HEIGHT_CURRENT, COLOR_PALETTE, LINE_THICKNESS, SINGLE_CLS, HIDE_LABEL)

            # Mode: mark, read
            if MARK_MODE:
                # left button double click  =>  hightlight selected bbox
                if IS_BBOX_SELECTED:
                    tmp_img = highlight_selected_bbox(tmp_img, alpha=1, beta=0.5, gamma=0)


            # key listen
            pressed_key = cv2.waitKey(5)


            if MARK_MODE:
                # draw with twice left_click
                # first click: top_left point
                if POINT_1[0] != -1:    
                    # draw partial bbox 
                    cv2.rectangle(tmp_img, POINT_1, (MOUSE_X, MOUSE_Y), color, LINE_THICKNESS)

                    # if second click: bottom_right point
                    if POINT_2[0] != -1:

                        # save bbox right after get point_2  =>  label.txt
                        line = yolo_format(CLS_IDX_CURRENT, POINT_1, POINT_2, IMG_WIDTH_CURRENT, IMG_HEIGHT_CURRENT) # (x,y,x,y) => (x,y,w,h)
                        with open(label_path, 'a') as f:
                            f.write(line + '\n') # append line
                        
                        # reset the points
                        POINT_1 = (-1, -1)
                        POINT_2 = (-1, -1)

            # show bboxes num
            if not HIDE_NUM_BBOXES:
                cv2.putText(tmp_img, 
                            "bbox_num: " + str(len(IMG_OBJECTS)), 
                            (IMG_WIDTH_CURRENT // 50, IMG_HEIGHT_CURRENT // 5), 
                            cv2.FONT_HERSHEY_SIMPLEX,
                            LINE_THICKNESS / 3, 
                            color,
                            thickness=LINE_THICKNESS * 2,
                            lineType=cv2.LINE_AA
                            )

            # current show
            cv2.imshow(WINDOW_NAME, tmp_img)
            
            
            # -----------------------------------------
            # opencv key listening
            # -----------------------------------------

            # h/H => help 
            if pressed_key in (ord('h'), ord('H')):
                text = ('[ESC] to quit;\n'
                        '[r]switch mode: mark? read?;\n'
                        '[a/d] to switch Image;\n'
                        '[w/s] to switch Class;\n'
                        '[double click to select] + w/s can change class;\n'
                        '[-/+] to adjust line-thickness;\n'
                        '[n] to hide labels;\n'
                        '[b] to blink the bboxes in the img;\n'
                        '[l] to shuffle bbox colors;\n'
                        '[i] to display info: [path & bboxes];\n'
                        '[c] to to remove all bboxes;\n'
                        '[backspace]to remove bbox one by one from the last;\n'
                        '[0-8] to show single class bboxes;\n'
                        '[9] to show all classes bboxes;\n'
                        'inspect & mark mode => info => check(copy valid & check img_label_pair)'
                        )

                print_info(text, ms=5000, where="Overlay")

            # ---------------------------------------
            # a,d -> images [previous, next]
            # ---------------------------------------
            elif pressed_key in (ord('a'), ord('A'), ord('d'), ord('D')):
                
                # last image index
                IMG_IDX_LAST = IMG_IDX_CURRENT

                # show previous image
                if pressed_key in (ord('a'), ord('A')):     
                    IMG_IDX_CURRENT = decrease_index(IMG_IDX_CURRENT, IMG_COUNT)

                # show next image index
                elif pressed_key in (ord('d'), ord('D')):
                    IMG_IDX_CURRENT = increase_index(IMG_IDX_CURRENT, IMG_COUNT)

                # set current img index
                set_img_index(IMG_IDX_CURRENT)

                # update img trackbar 
                cv2.setTrackbarPos(TRACKBAR_IMG, WINDOW_NAME, IMG_IDX_CURRENT)

                # when reach the end
                if IMG_IDX_CURRENT == IMG_IDX_LAST:
                    print_info(f"Reach to the end!\n", ms=5000, where="Overlay")

                # set the adjust flag False
                LINE_THICKNESS_ADJUST = False

            

            # ---------------------------------------
            # w,s -> class  [previous, next]
            # ---------------------------------------
            elif pressed_key in (ord('s'), ord('S'), ord('w'), ord('W')):
                # next class
                if pressed_key in (ord('s'), ord('S')):
                    CLS_IDX_CURRENT = decrease_index(CLS_IDX_CURRENT, CLS_COUNT)

                # last class
                elif pressed_key in (ord('w'), ord('W')):
                    CLS_IDX_CURRENT = increase_index(CLS_IDX_CURRENT, CLS_COUNT)

                # set current class index
                set_class_index(CLS_IDX_CURRENT)

                # update class trackbar                
                cv2.setTrackbarPos(TRACKBAR_CLASS, WINDOW_NAME, CLS_IDX_CURRENT)

                # when select, use W/S to edit bbox's class
                if IS_BBOX_SELECTED:
                    bbox_with_id = IMG_OBJECTS[SELECTED_BBOX]
                    edit_bbox(bbox_with_id, 'change_class:{}'.format(CLS_IDX_CURRENT))

            # ---------------------------------------
            # n/N => hide label
            # ---------------------------------------
            elif pressed_key in (ord('n'), ord('N')):
                HIDE_LABEL = not HIDE_LABEL
                print_info('Press n to hide Label or show Label.', ms=1000, where="Overlay")

            # ---------------------------------------
            # '=+' => bold line thickness
            # '-_' => thin line thickness
            # ---------------------------------------
            elif pressed_key in (ord('='), ord('+')):

                # set the adjust flag TRUE
                LINE_THICKNESS_ADJUST = True
                
                # get the max line width
                max_t = max(round(sum(tmp_img.shape) / 2 * 0.003), 2) + 5

                # increate the line width
                if LINE_THICKNESS <= max_t:
                    LINE_THICKNESS += 1
                    print_info(f'Line Thickness +1, now = {LINE_THICKNESS}', ms=1000, where="Overlay")
                else:
                    print_info('Line Thickness has reach the max value!', ms=1000, where="Overlay")

            elif pressed_key in (ord('-'), ord('_')):
                LINE_THICKNESS_ADJUST = True
                min_t = 1
                if LINE_THICKNESS > min_t:
                    LINE_THICKNESS -= 1
                    print_info(f'Line Thickness -1, now = {LINE_THICKNESS}', ms=1000, where="Overlay")
                else: 
                    print_info('Line Thickness has reach the min value!', ms=1000, where="Overlay")

            # ---------------------------------------
            # i/I => display the info in this img(size, path, num_bboxes)
            # ---------------------------------------
            elif pressed_key in (ord('i'), ord('I')):
                msg = (f"Current image: {Path(img_path).name}\n," 
                      f"Currnet BBoxes: {len(IMG_OBJECTS)}\n"
                      f"Img size: ({tmp_img.shape[0]}, {tmp_img.shape[1]})")
                print_info(msg, ms=3000, where="Overlay")

                # display the num_bboxes in the img
                HIDE_NUM_BBOXES = not HIDE_NUM_BBOXES


            # ---------------------------------------
            # b/b => blink bboxes in current img
            # ---------------------------------------
            elif pressed_key in (ord('b'), ord('B')):
                BLINK_BBOXES = not BLINK_BBOXES


            # ---------------------------------------
            # BACKSPACE => emove all bboxes in current image
            # ---------------------------------------
            elif pressed_key == 8:
                print_info(f"Remove all bbox", ms=2000, where="Overlay")
                

                if IMG_OBJECTS:
                    # print(f"num: {len(IMG_OBJECTS)}")
                    bbox_with_id = IMG_OBJECTS[-1]
                    edit_bbox(bbox_with_id, 'delete')

            # ---------------------------------------
            # c/C  =>  Remove all bboxes in this img, specifically, delete the annotation file(.txt)
            # ---------------------------------------
            elif pressed_key in (ord('c'), ord('C')):
                print_info(f"Clean bbox one by one! rest num = {len(IMG_OBJECTS)}", ms=1000, where="Overlay")
                if Path(label_path).exists():
                    Path(label_path).unlink()
                else:
                    print_info(f"No bboxes in this img!", ms=1000, where="Overlay")

            # ---------------------------------------
            # r/R  =>  switch mode
            # ---------------------------------------
            elif pressed_key in (ord('r'), ord('R')):
                print_info(f"Switch mode between READ and MARK", ms=1000, where="Overlay")
                MARK_MODE = not MARK_MODE

            # ---------------------------------------
            # l/L  =>  shuffle bbox color
            # ---------------------------------------
            elif pressed_key in (ord('l'), ord('L')):
                COLOR_PALETTE = Colors(shuffle=True)
                print_info(f"Colors palette shuffled!", ms=1000, where="Overlay")

            # ---------------------------------------
            # 0-8 -> select to show single class
            # 9 -> show all
            # ---------------------------------------
            elif pressed_key in range(48, 57):  # 0-8 => 48-56
                value = int(chr(pressed_key))
                if value <= CLS_COUNT:
                    SINGLE_CLS = value
                    print_info(f"Only show class: {SINGLE_CLS} => {CLASS_LIST[SINGLE_CLS]}", ms=1000, where="Overlay")
                else:
                    SINGLE_CLS = None
                    print_info(f"No class: {value}, Max class is {CLS_COUNT} => {CLASS_LIST[CLS_COUNT]}. Show All bboxes", ms=1000, where="Overlay")

            elif pressed_key == 57:  # 9
                SINGLE_CLS = None
            



            # ---------------------------------------
            # ESC -> quit key listener
            # ---------------------------------------
            elif pressed_key == 27:
                break

            # ---------------- Key Listeners END ------------------------

            # if window gets closed then quit
            if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
                break

        cv2.destroyAllWindows()


        # 删除所有无法被opencv读取的图像

        if len(WRONG_IMG_SET) > 0:
            # rich.print(f"[gold1 bold]==>has {len(WRONG_IMG_SET)} images can not be read by OpenCV, moving to {WRONG_IMG_DIR}")
            LOGGER.warning(f"has {len(WRONG_IMG_SET)} images can not be read by OpenCV, moving to {WRONG_IMG_DIR}")
            
            # create dir if not exist
            if not Path(WRONG_IMG_DIR).exists():
                Path(WRONG_IMG_DIR).mkdir()

            # remove
            for img in WRONG_IMG_SET:
                # remove 
                shutil.move(img, WRONG_IMG_DIR)
                rich.print(f"[bold red]{Path(img).resolve()}")

        else:
            # rich.print(f"[gold1 bold]==>Every image can be read by OpenCV.")
            LOGGER.info(f"Every image can be read by OpenCV.")

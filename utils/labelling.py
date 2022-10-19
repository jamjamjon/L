
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
from loguru import logger as LOGGER

#--------------------------------------------
#       ADD TO PYTHON_PATH
#--------------------------------------------
FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]   # FILE.parent 
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
# ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # abs path => relative
#--------------------------------------------

# general Py module
from general import (get_corresponding_label_path, Colors, load_img_label_list, 
                    IMG_FORMAT, is_point_in_rect, img_label_dir_cleanup
                    )


#--------------------------------------------
#          Global Variables
#--------------------------------------------

# windows 
WINDOW_NAME = 'MLOps-Dataset-Jamjon'

# tracker bars
TRACKBAR_IMG = 'Images'
TRACKBAR_CLASS = 'Classes'


# input dir
INPUT_IMG_DIR  = ""
INPUT_LABEL_DIR = ""

# mode 
MARK_MODE = False


# images
IMAGE_PATH_LIST = [] 
IMG_IDX_CURRENT = 0         # 当前的img index
IMG_IDX_LAST = 0            # last 的img index
IMG_CURRENT = None          # 当前页面显示的img
IMG_OBJECTS = []            # 当前页面总所有bbox
WRONG_IMG_SET = set()       # 无法正常读取的image
IMG_COUNT = 0


# classes
CLASS_LIST = []                         # all class ID
CLS_IDX_CURRENT = 0         # 当前的class index
CLS_COUNT = 0

# bbox status
PRVE_WAS_DOUBLE_CLICK = False   # 之前是否双击了
IS_BBOX_SELECTED = False        # 是否选中了当前bbox
SELECTED_BBOX = -1              # 选中后，IMG_OBJECTS中的第 idx 个

# point_xy & mouse_xy
MOUSE_X = 0
MOUSE_Y = 0
POINT_1 = (-1, -1)
POINT_2 = (-1, -1)




#--------------------------------------------
#          Functions
#--------------------------------------------

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
    print_info(text, ms=500, where="Overlay")


# set current class index 
def set_class_index(x):

    # current_class_index, class_list, window_name
    global CLS_IDX_CURRENT, CLASS_LIST, WINDOW_NAME

    CLS_IDX_CURRENT = x
    text = f"Selected class: {CLASS_LIST[CLS_IDX_CURRENT]} ({str(CLS_IDX_CURRENT)}/{str(CLS_COUNT)})" 
    print_info(text, ms=500, where="Overlay")


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
def to_yolo_format(cls_idx, point_1, point_2, img_w, img_h):
    eps = 1e-4

    # boundary check
    if point_1[0] < 0:
        point_1 = (eps, point_1[1])
    if point_2[0] > img_w:
        point_2 = (img_w - eps, point_2[1])
    if point_1[1] < 0:
        point_1 = (point_1[0], eps)
    if point_2[1] > img_h:
        point_2 = (point_2[0], img_w - eps)

    # convert
    cx = float((point_1[0] + point_2[0]) / (2.0 * img_w) )
    cy = float((point_1[1] + point_2[1]) / (2.0 * img_h))
    w = float(abs(point_2[0] - point_1[0])) / img_w
    h = float(abs(point_2[1] - point_1[1])) / img_h
    
    # double check of boundary
    if not all([0 <= x <= 1 for x in [cx, cy, w, h]]):
        LOGGER.error(f"Wrong coordination of cx, cy, w, h!")
        
        # todo



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

        # print(Path(label_path).resolve())
        
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
# todo: line_thickness remove
def set_selected_bbox(set_cls_trackbar=True):
    global IS_BBOX_SELECTED, SELECTED_BBOX, IMG_OBJECTS  # , LINE_THICKNESS

    # smallest bbox flag
    smallest_area = -1

    # if clicked inside multiple bboxes selects the smallest one
    for idx, obj in enumerate(IMG_OBJECTS):
        ind, x1, y1, x2, y2 = obj

        # # line width (consider) 
        # margin = 2 * LINE_THICKNESS
        # x1 = x1 - margin  
        # y1 = y1 - margin
        # x2 = x2 + margin
        # y2 = y2 + margin

        # is mouse_xy in bbox
        if is_point_in_rect(MOUSE_X, MOUSE_Y, x1, y1, x2, y2):

            IS_BBOX_SELECTED = True     # set bbox selected
            tmp_area = abs(x2 - x1) * abs(y2 - y1)  # area of bbox

            if tmp_area < smallest_area or smallest_area == -1:
                smallest_area = tmp_area
                SELECTED_BBOX = idx
                if set_cls_trackbar: 
                    cv2.setTrackbarPos(TRACKBAR_CLASS, WINDOW_NAME, ind)    # 将track Bar的类别移动到所属class
        # else:
        #     IS_BBOX_SELECTED = False
        #     SELECTED_BBOX = -1


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
    global IMAGE_PATH_LIST, IMG_IDX_CURRENT, INPUT_LABEL_DIR, IMG_CURRENT


    img_height, img_width= IMG_CURRENT.shape[:2]

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

        yolo_line = to_yolo_format(cls_idx, (xmin, ymin), (xmax, ymax), img_width, img_height) # TODO: height and width ought to be stored
        
        # 找出删除了的或者修改了类别的那一行idx
        ind = findIndex(bbox_with_id)

        # re-write label(.txt)
        with open(ann_path, 'w') as new_file:
            for idx, line in enumerate(lines):
                if idx != ind:              # 如果未修改的行，直接写入
                    new_file.write(line)
                
                elif 'change_class' in action:  # 如果是修改的行，并且修的是类别，将更换后新的类别写入
                    new_yolo_line = to_yolo_format(new_class_index, (xmin, ymin), (xmax, ymax), img_width, img_height)
                    new_file.write(new_yolo_line + '\n')
                
                # 如果不属于以上情况，那么就是删除，则不写入该行
                


# mouse callback function
def mouse_listener(event, x, y, flags, param):
    global IS_BBOX_SELECTED, SELECTED_BBOX, PRVE_WAS_DOUBLE_CLICK, MOUSE_X, MOUSE_Y, POINT_1, POINT_2, IMG_OBJECTS, MARK_MODE

    # mark mode
    if MARK_MODE:
        # move:  MOUSE_X mouse_y
        if event == cv2.EVENT_MOUSEMOVE:
            MOUSE_X = x
            MOUSE_Y = y

            # # mouse hover 
            # for idx, obj in enumerate(IMG_OBJECTS):
            #     ind, x1, y1, x2, y2 = obj
              
            #     # is mouse_xy in bbox
            #     if is_point_in_rect(MOUSE_X, MOUSE_Y, x1, y1, x2, y2):
            #         IS_BBOX_SELECTED = True     # set bbox selected
            #         SELECTED_BBOX = idx
                    
           

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
# todo: remove line thickness
def highlight_selected_bbox(img, line_thickness, alpha=1, beta=0.5, gamma=0):
    global IMG_OBJECTS, SELECTED_BBOX  # , LINE_THICKNESS

    # line width
    lw = line_thickness // 2


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


# opencv window init
def opencv_window_init():
    # init window with overlap
    try:
        cv2.namedWindow('Test')   
        cv2.displayOverlay('Test', 'Test overlap', 10)  
        cv2.displayStatusBar('Test', 'Test status bar', 10)
    except cv2.error:
        print('-> Please ignore this error message\n')
    cv2.destroyAllWindows()   







# ---------------------------------------------------
#   inspect : main for calling
#--------------------------------------------------
def inspect( img_dir, 
             label_dir,
             mv_dir,
             wrong_img_dir,
             classes,
             window_width=800,
             window_height=600,
             ):
    
    # global vars
    global WINDOW_NAME,\
           INPUT_LABEL_DIR, \
           MARK_MODE,\
           IMAGE_PATH_LIST, IMG_IDX_CURRENT, IMG_IDX_LAST, IMG_CURRENT, IMG_OBJECTS, WRONG_IMG_SET,\
           CLASS_LIST, CLS_IDX_CURRENT, \
           TRACKBAR_IMG, TRACKBAR_CLASS,\
           PRVE_WAS_DOUBLE_CLICK, IS_BBOX_SELECTED, SELECTED_BBOX, MOUSE_X, MOUSE_Y, POINT_1, POINT_2,\
           IMG_COUNT, CLS_COUNT
    


    # input img dir & label dir
    INPUT_IMG_DIR  = img_dir
    INPUT_LABEL_DIR = label_dir if label_dir else INPUT_IMG_DIR
    print_info(f"IMG   DIR:\t{Path(INPUT_IMG_DIR).resolve()}")
    print_info(f"LABEL DIR:\t{Path(INPUT_LABEL_DIR).resolve()}")


    #-----------------------------------------   
    WINDOW_INIT_WIDTH = window_width    # initial window width
    WINDOW_INIT_HEIGHT = window_height    # initial window height

    # mark mode 
    MARK_MODE = False

    # wrong dir & move dir
    WRONG_IMG_DIR = wrong_img_dir
    MV_DIR = mv_dir

    # hide label
    HIDE_LABEL = False

    # num_bboxes
    HIDE_NUM_BBOXES = False

    # only show one specific class
    SINGLE_CLS = None

    # bboxes blink
    DO_BLINK_BBOXES = False
    BLINK_OR_NOT = False

    # line thickness  &  line thickes adjust
    LINE_THICKNESS = 1            
    LINE_THICKNESS_ADJUST = False   # line thickness adjust flag

    # CLASS_LIST
    if len(classes) == 0:   # no classes
        LOGGER.error(f"No classes input!!!")
        exit(-3)
    elif len(classes) == 1 and classes[0].endswith('.txt'):    # txt input
        # load all class name
        with open(classes[0]) as f:
            for line in f:
                CLASS_LIST.append(line.strip())
        print_info(f"CLASS_LIST:\t{CLASS_LIST}")
    else: # args classes 
        CLASS_LIST = classes
        print_info(f"CLASS_LIST:\t{CLASS_LIST}")    


    # repeat class check 
    if not (len(CLASS_LIST) == len(set(CLASS_LIST))):
        LOGGER.error("Repeat class name!!!")
        exit(-3)


    # init
    opencv_window_init()

    # read all input images
    rich.print(f"[bold green]loading data...")
    for f in sorted(os.listdir(INPUT_IMG_DIR), key=cmp):    
        f_path = os.path.join(INPUT_IMG_DIR, f)
        # 如果是文件夹，不读，continue
        if os.path.isdir(f_path):   
            continue

        # image verify. images path  => IMAGE_PATH_LIST
        # 太费时间，直接后缀判断 + 错误记录
        if Path(f).suffix in IMG_FORMAT:
            IMAGE_PATH_LIST.append(f_path)


    # img count
    IMG_COUNT = len(IMAGE_PATH_LIST) - 1  

    # class count
    CLS_COUNT = len(CLASS_LIST) - 1
    if CLS_COUNT < 0:
        rich.print(f"[red bold]Error: No class in class_list.txt!")
        raise StopIteration


    # create output dir if not exist
    if not Path(INPUT_LABEL_DIR).exists():
        Path(INPUT_LABEL_DIR).mkdir()

    # create window 
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_KEEPRATIO)  # cv2.WINDOW_FREERATIO   cv2.WINDOW_KEEPRATIO, WINDOW_GUI_NORMAL, WINDOW_GUI_EXPANDED
    cv2.resizeWindow(WINDOW_NAME, WINDOW_INIT_WIDTH, WINDOW_INIT_HEIGHT)

    # mouse listen callback
    cv2.setMouseCallback(WINDOW_NAME, mouse_listener)

    # trackBar of images
    if IMG_COUNT != 0:
        cv2.createTrackbar(TRACKBAR_IMG, WINDOW_NAME, 0, IMG_COUNT, set_img_index) 
 
    # class tracker bar
    if CLS_COUNT != 0:
        cv2.createTrackbar(TRACKBAR_CLASS, WINDOW_NAME, 0, CLS_COUNT, set_class_index)

    # initialize the img index
    set_img_index(0)

    # overlay to show: help
    # print_info('Press [h] for help.', ms=0, where="Overlay")
    print_info('Press [h] for help.', ms=0, where="Statusbar")


    # colors palette
    COLOR_PALETTE = Colors(shuffle=False)  

    rich.print(f"[bold green]running...")
    # loop
    while True:


        # color for every class
        color = COLOR_PALETTE(int(CLS_IDX_CURRENT), bgr=False)

        # clone the img   
        tmp_img = IMG_CURRENT.copy()
        img_height_current, img_width_current = tmp_img.shape[:2]

        # bbox line-thickness
        LINE_THICKNESS = max(round(sum(tmp_img.shape) / 2 * 0.003), 1) if not LINE_THICKNESS_ADJUST else LINE_THICKNESS      # line width

        # mode: mark, inspect
        if MARK_MODE:
            # cursor line for drawing
            draw_cursor_line(tmp_img, MOUSE_X, MOUSE_Y, img_height_current, img_width_current, color, LINE_THICKNESS)

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
        if DO_BLINK_BBOXES:
            if BLINK_OR_NOT == False:
                tmp_img = draw_bboxes_from_file(tmp_img, label_path, img_width_current, img_height_current, COLOR_PALETTE, 0, SINGLE_CLS, HIDE_LABEL)
                BLINK_OR_NOT = True
            else:
                tmp_img = draw_bboxes_from_file(tmp_img, label_path, img_width_current, img_height_current, COLOR_PALETTE, LINE_THICKNESS, SINGLE_CLS, HIDE_LABEL)
                BLINK_OR_NOT = False
        else:
            # draw already done bounding boxes
            tmp_img = draw_bboxes_from_file(tmp_img, label_path, img_width_current, img_height_current, COLOR_PALETTE, LINE_THICKNESS, SINGLE_CLS, HIDE_LABEL)

        # Mode: mark, read
        if MARK_MODE:
            # left button double click  =>  hightlight selected bbox
            if IS_BBOX_SELECTED:
                tmp_img = highlight_selected_bbox(tmp_img, LINE_THICKNESS, alpha=1, beta=0.5, gamma=0)


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
                    line = to_yolo_format(CLS_IDX_CURRENT, POINT_1, POINT_2, img_width_current, img_height_current) # (x,y,x,y) => (x,y,w,h)

                    # save label
                    with open(label_path, 'a') as f:
                        f.write(line + '\n') # append line
                    
                    # reset the points
                    POINT_1 = (-1, -1)
                    POINT_2 = (-1, -1)

        # show bboxes num
        if not HIDE_NUM_BBOXES:
            cv2.putText(tmp_img, 
                        "bbox_num: " + str(len(IMG_OBJECTS)), 
                        (img_width_current // 50, img_height_current // 5), 
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

            print_info(text, ms=1000, where="Overlay")

        # ---------------------------------------
        # a,d -> images [previous, next]
        # ---------------------------------------
        elif pressed_key in (ord('a'), ord('A'), ord('d'), ord('D')):

            if not IS_BBOX_SELECTED:

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
                    print_info(f"Reach to the end!\n", ms=2000, where="Overlay")

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
            print_info(msg, ms=1000, where="Overlay")

            # display the num_bboxes in the img
            HIDE_NUM_BBOXES = not HIDE_NUM_BBOXES


        # ---------------------------------------
        # b/b => blink bboxes in current img
        # ---------------------------------------
        elif pressed_key in (ord('b'), ord('B')):
            DO_BLINK_BBOXES = not DO_BLINK_BBOXES


        # ---------------------------------------
        # BACKSPACE => remove last bboxes in current image
        # ---------------------------------------
        elif pressed_key == 8:
            
            
            if not IS_BBOX_SELECTED:
                print_info(f"Remove all bbox", ms=1000, where="Overlay")
                if IMG_OBJECTS:
                    # print(f"num: {len(IMG_OBJECTS)}")
                    bbox_with_id = IMG_OBJECTS[-1]
                    edit_bbox(bbox_with_id, 'delete')

        # ---------------------------------------
        # c/C  =>  Remove all bboxes in this img, specifically, delete the annotation file(.txt)
        # ---------------------------------------
        elif pressed_key in (ord('c'), ord('C')):
            if not IS_BBOX_SELECTED:
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


    # last step: 删除所有无法被opencv读取的图像
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






# ----------------options ------------------------
def parse_opt():
    parser = argparse.ArgumentParser(description='Open-source image labeling tool')
    parser.add_argument('--img-dir', default='img-dir', type=str, help='Path to input directory')
    parser.add_argument('--label-dir', default='', type=str, help='Path to output directory')
    parser.add_argument('--mv-dir', default="moved_dir", type=str, help='mv-dir to save moved data[img, label]')
    parser.add_argument('--wrong-img-dir', default="wrong_img_dir", type=str, help='wrong format img to save imgs opencv cant read')
    parser.add_argument('--classes', default='', nargs="+", type=str, help='classes list text')
    parser.add_argument('--window_width', default=800, type=int, help='classes list text')
    parser.add_argument('--window_height', default=600, type=int, help='classes list text')


    # parser.add_argument('--mark-mode', default=False, type=bool, help='mark or insepect(default)')
    # parser.add_argument('--hide-label', default=False, type=bool, help='hide label or not')
    # parser.add_argument('--hide-num-bboxes', default=False, type=bool, help='show num of bboxes in the img')
    # parser.add_argument('--blink', default=False, type=bool, help='blink bboxes')
    # parser.add_argument('--cls', type=int, default=None, help='filter by class: --classes 0, or --classes 0 2 3')

    opt = parser.parse_args()
    rich.print(f"{opt}\n")

    return opt





# ---------------------------------------------------
#   main
#--------------------------------------------------
if __name__ == '__main__':


    rich.print(f"[bold green]-------[INSPECT_MARK MODE]-------\n")

    # options
    opt = parse_opt()
    inspect( opt.img_dir, 
             opt.label_dir,
             opt.mv_dir,
             opt.wrong_img_dir,
             opt.classes,
             opt.window_width,
             opt.window_height,
             )

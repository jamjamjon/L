from ctypes import *
import math
import random
import cv2
import numpy as np
import time

def nparray_to_image(img):
    data = img.ctypes.data_as(POINTER(c_ubyte))
    image = ndarray_image(data, img.ctypes.shape, img.ctypes.strides)
    return image



class BOX(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float),
                ("w", c_float),
                ("h", c_float)]


class DETECTION(Structure):
    _fields_ = [("bbox", BOX),
                ("classes", c_int),
                ("prob", POINTER(c_float)),
                ("mask", POINTER(c_float)),
                ("objectness", c_float),
                ("sort_class", c_int)]


class IMAGE(Structure):
    _fields_ = [("w", c_int),
                ("h", c_int),
                ("c", c_int),
                ("data", POINTER(c_float))]


class METADATA(Structure):
    _fields_ = [("classes", c_int),
                ("names", POINTER(c_char_p))]


lib = CDLL("/home/user/wuzhe/darknet/darknet/libdarknet.so", RTLD_GLOBAL)
# lib = CDLL("libdarknet.so", RTLD_GLOBAL)
lib.network_width.argtypes = [c_void_p]
lib.network_width.restype = c_int
lib.network_height.argtypes = [c_void_p]
lib.network_height.restype = c_int

predict = lib.network_predict
predict.argtypes = [c_void_p, POINTER(c_float)]
predict.restype = POINTER(c_float)

set_gpu = lib.cuda_set_device
set_gpu.argtypes = [c_int]

make_image = lib.make_image
make_image.argtypes = [c_int, c_int, c_int]
make_image.restype = IMAGE

get_network_boxes = lib.get_network_boxes
get_network_boxes.argtypes = [c_void_p, c_int, c_int, c_float, c_float, POINTER(c_int), c_int, POINTER(c_int)]
get_network_boxes.restype = POINTER(DETECTION)

make_network_boxes = lib.make_network_boxes
make_network_boxes.argtypes = [c_void_p]
make_network_boxes.restype = POINTER(DETECTION)

free_detections = lib.free_detections
free_detections.argtypes = [POINTER(DETECTION), c_int]

free_ptrs = lib.free_ptrs
free_ptrs.argtypes = [POINTER(c_void_p), c_int]

network_predict = lib.network_predict
network_predict.argtypes = [c_void_p, POINTER(c_float)]

reset_rnn = lib.reset_rnn
reset_rnn.argtypes = [c_void_p]

load_net = lib.load_network
load_net.argtypes = [c_char_p, c_char_p, c_int]
load_net.restype = c_void_p

do_nms_obj = lib.do_nms_obj
do_nms_obj.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

do_nms_sort = lib.do_nms_sort
do_nms_sort.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

free_image = lib.free_image
free_image.argtypes = [IMAGE]

letterbox_image = lib.letterbox_image
letterbox_image.argtypes = [IMAGE, c_int, c_int]
letterbox_image.restype = IMAGE

load_meta = lib.get_metadata
lib.get_metadata.argtypes = [c_char_p]
lib.get_metadata.restype = METADATA

load_image = lib.load_image_color
load_image.argtypes = [c_char_p, c_int, c_int]
load_image.restype = IMAGE

rgbgr_image = lib.rgbgr_image
rgbgr_image.argtypes = [IMAGE]

predict_image = lib.network_predict_image
predict_image.argtypes = [c_void_p, IMAGE]
predict_image.restype = POINTER(c_float)

ndarray_image = lib.ndarray_to_image
ndarray_image.argtypes = [POINTER(c_ubyte), POINTER(c_long), POINTER(c_long)]
ndarray_image.restype = IMAGE

def detect(net, meta, im, thresh=.3, hier_thresh=.5, nms=.45):
    num = c_int(0)
    pnum = pointer(num)

    predict_image(net, im)
    dets = get_network_boxes(net, im.w, im.h, thresh, hier_thresh, None, 0, pnum)
    num = pnum[0]
    if (nms): do_nms_obj(dets, num, meta.classes, nms);

    res = []
    for j in range(num):
        for i in range(meta.classes):
            if dets[j].prob[i] > 0:
                b = dets[j].bbox
                res.append((meta.names[i], dets[j].prob[i], (b.x, b.y, b.w, b.h)))
    res = sorted(res, key=lambda x: -x[1])
    free_image(im)
    free_detections(dets, num)
    return res

def ReadEveryNthFrame(cap, N):
    for i in range(N):
        ret, frame = cap.read()
    return ret, frame

def boxInArea(box, targetArea):
    x = box[0]
    y = box[1]
    if x >= targetArea[0] and x <= targetArea[2] and y >= targetArea[1] and y <= targetArea[3]:
        return True
    else:
        return False



def detector(img_folder, net, meta, flip, transpose, saveout_folder):

    import os
    from slacking_box import out
    import slacking_box as sb

    images_all = os.listdir(img_folder)
    out(f"[bold green]{len(images_all)}  images to be detect!")

    for idx, image in enumerate(images_all):
        out(f"=> img {idx}")

        img_path = os.path.join(img_folder, image)

        img = cv2.imread(img_path)

        img_c = img.copy()
        im = nparray_to_image(img_c)
        start = time.time()
        objects = detect(net, meta, im)
        # print(time.time() - start)

        for object in objects:
            label = object[0]
            confidence = object[1]
            box = object[2]
            p1 = (int(box[0] - box[2]/2), int(box[1] - box[3]/2))
            p2 = (int(box[0] + box[2]/2), int(box[1] + box[3]/2))
            # print(confidence)

            if label.decode() == "fire":
                cv2.rectangle(img_c, p1, p2, (0, 0, 255), 2)
                cv2.putText(img_c, str(label.decode()) + " " + str("{:.2}".format(confidence)), (p1[0], p1[1]-5), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(0, 255, 0), thickness=2)
            elif label.decode() == "smoke":
                cv2.rectangle(img_c, p1, p2, (0, 255, 255), 2)
                cv2.putText(img_c, str(label.decode()) + " " +  str("{:.2}".format(confidence)), (p1[0], p1[1]-5), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(0, 255, 0), thickness=2)
        

        saveout = os.path.join(saveout_folder, image)
        cv2.imwrite(saveout, img_c)
    
    out(f"[bold green]done.")



if __name__ == "__main__":
    net = load_net("/home/user/wuzhe/darknet/darknet/train_smoke_fire/yolov3_416x416.cfg".encode("utf-8"),
		   "/home/user/wuzhe/darknet/darknet/train_smoke_fire/backup_3/yolov3_416x416_22000.weights".encode("utf-8"), 0)
    meta = load_meta("./smokefire.data".encode("utf-8"))

    img_folder = "validate_images"
    saveout_folder = "test_imgs_res"
    flip = False
    transpose = False
    detector(img_folder, net, meta, flip, transpose, saveout_folder)

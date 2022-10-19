#!/usr/bin/env python
# -*- coding:utf-8 -*- 



import cv2
import os
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("--video_path", type=str, default="people_vehicle.mp4")

parser.add_argument("--video_to_image", action='store_true')
parser.add_argument("--img_save_dir", type=str, default="img_output")

parser.add_argument("--save_video", action='store_true')
parser.add_argument("--video_save_out", type=str, default="video_output.mp4")

args = parser.parse_args()


# split video into frames
if args.video_to_image:
    idx = 0 # frame count

    # make dir for saving
    if not os.path.exists(args.img_save_dir):
        os.mkdir(args.img_save_dir)


# load video
cap = cv2.VideoCapture(args.video_path)


# save video
if args.save_video:
    # fourcc = cv2.VideoWriter_fourcc('I', '4', '2', '0') # avi
    fourcc = cv2.VideoWriter_fourcc(*'MP4V')

    video_fps =int(cap.get(cv2.CAP_PROP_FPS))
    video_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    video_size = (video_w, video_h)
    # video_save_ = args.video_save_out    # output.mp4
    video_writer = cv2.VideoWriter(args.video_save_out, fourcc, video_fps, video_size)



while 1:
    ret, frame = cap.read()
    if ret == True:
        # frame = cv2.flip(frame, 0)


        # save frame inorder to save video
        if args.save_video:
            video_writer.write(frame)
        
        # show video        
        cv2.imshow('frame', frame)

        # video to img
        if args.video_to_image:
            save_out = os.path.join(args.img_save_dir, str(idx)) + ".jpg"
            cv2.imwrite(save_out, frame)
            idx += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break



cap.release()
if args.save_video:
    video_writer.release()
cv2.destroyAllWindows()
print("done")
#!/usr/bin/env python
# -*- coding:utf-8 -*- 

import cv2
import os
import rich

def video2imgs(source,                             # 0: cam
                img_save_out="video_2_images",      # save dir
                img_format=".jpg",
                show_frame=False,
                flip=False,
                every_N_frame=1,
                ):
    


    idx = 0 # frame count

    # make dir for saving
    if not os.path.exists(img_save_out):
        os.mkdir(img_save_out)
    else:
        img_dir = os.path.abspath(img_save_out)
        imgs_list = [os.path.join(img_save_out, x) for x in os.listdir(img_dir)]
        for elem in imgs_list:
            os.remove(elem)


    # load video
    cap = cv2.VideoCapture(source)


    while 1:
        ret, frame = cap.read()
        if ret == True:

            # flip frame
            if flip:
                frame = cv2.flip(frame, 0)
            
            # show video 
            if show_frame:       
                cv2.imshow('video', frame)


            # video to img
            if idx % every_N_frame == 0:                
                save_out = os.path.join(img_save_out, str(idx)) + img_format
                cv2.imwrite(save_out, frame)
            
            idx += 1

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break

    cap.release()
    cv2.destroyAllWindows()

    rich.print(f"[bold green]=> Successfully split video into images.")



def play(source, flip=False, wait=1):

    # 0 -> web cam
    cap = cv2.VideoCapture(source)

    idx = 1
    while True:
        ret, frame = cap.read()
        cv2.imshow("video", frame)
        

        # get the key
        key = cv2.waitKey(wait)
        if key == 27 or key == ord("q"):
            #通过esc键退出摄像
            cv2.destroyAllWindows()
            break

        if key == ord("s"):
            # 通过s键保存图片
            cv2.imwrite("image" + str(idx) + ".jpg",frame)
            idx += 1

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


    rich.print(f"[bold green]Successfully played video.")


if __name__ == '__main__':
    pass

    # convert2img(source="1.mp4",
    #             img_save_out="video_2_images",      # save dir
    #             img_format=".jpg",
    #             show_frame=False,
    #             flip=False,
    #             every_N_frame=3,
    #             )
    
    # play("1.mp4")



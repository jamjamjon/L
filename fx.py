import cv2
from pathlib import Path
import numpy as np
import rich
import shutil
import argparse
import os
from tqdm import tqdm
import sys
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
from utils.general import (get_corresponding_label_path, Colors, load_img_label_list, 
                    IMG_FORMAT, is_point_in_rect, img_label_dir_cleanup, get_img_path,
                    # LOGGER,  set_logging,
                    )

from utils.labelling import inspect
from utils.video_tools import play_and_record, video_to_images, videos_to_images, images_to_video
from utils.spider import spider_img_baidu
from utils.dir_combine import dir_combine

# ----------------options ------------------------
def parse_opt():
    parser = argparse.ArgumentParser(description='Open-source image labeling tool')

    # basic directory
    parser.add_argument('--img-dir', default='', type=str, help='Path to input directory')
    parser.add_argument('--label-dir', default='', type=str, help='Path to output directory')
    parser.add_argument('--mv-dir', default="moved_dir", type=str, help='mv-dir to save moved data[img, label]')


    # inspect mode
    parser.add_argument('--inspect', action='store_true', help='labelling, inspect, GTBboxes check')
    parser.add_argument('--wrong-img-dir', default="wrong_img_dir", type=str, help='wrong format img to save imgs opencv cant read')
    parser.add_argument('--classes', default='', nargs="+", type=str, help='classes list text')
    parser.add_argument('--window_width', default=800, type=int, help='classes list text')
    parser.add_argument('--window_height', default=600, type=int, help='classes list text')

    # info mode  
    parser.add_argument('--info', action='store_true', help='info(img and label count)')

    # clean up mode
    parser.add_argument('--cleanup', '--clean', action='store_true', help='cleanup(img_label_pair)')
    parser.add_argument('--dont-clean-empty-txt', action='store_true', help='cleanup empty txt file')
    
    # video rec
    # rtsp://admin:admin12345@192.168.0.195/h264/ch1/sub/av_stream
    # parser.add_argument('--video-rec', default='', type=str, help='record video')
    # parser.add_argument('--video-rec-saveout', type=str, default= "video_rec_1.mp4", help='record video')


    # get_path mode
    parser.add_argument('--get-path', action='store_true', help='get img path')
    parser.add_argument('--d', type=str, required=False)
    parser.add_argument('--append', action='store_true',help='append to exist file or rewrite')
    parser.add_argument('--save-txt', default="images_path.txt",type=str, required=False)



    # video_tools
    parser.add_argument('--source', default='', type=str, help='dir, img, video, rtsp')

    # video -> images
    parser.add_argument('--v2is', action='store_true', help='video to images')
    parser.add_argument('--v2is-output', type=str, default='v2is', help='output dir')
    parser.add_argument('--frame', type=float, default=30, help='N frame')  # to do : change a name
    parser.add_argument('--view', action='store_true',help='imshow')
    parser.add_argument('--flip', action='store_true',help='Flip frame')
    parser.add_argument('--fmt-img', type=str, default='.jpg', help='img suffix')

    # videos -> images
    parser.add_argument('--vs2is', action='store_true', help='videos(dir) to images')
    parser.add_argument('--vs2is-output', type=str, default='vs2is', help='output dir')

    # play and record
    parser.add_argument('--play-rec', action='store_true', help='video play and record')
    parser.add_argument('--delay', type=int, default=1, help='cv2.keyWait')


    # images -> video
    parser.add_argument('--is2v', action='store_true', help='images to video')  
    parser.add_argument('--fps', default=30, help='FPS')
    parser.add_argument('--last4', default=60, help='imags as frame last for')
    parser.add_argument('--video-size', default=(416, 416), help='imags as frame last for')



    # spider -> image & video
    parser.add_argument('--spider-img-baidu', action='store_true', help='spider img from baidu') 
    parser.add_argument('--words', default='', type=str, nargs="+", help='multi word use space to sep.')
    # youtube-dl


    # check every image, [m] to remove
    parser.add_argument('--check-every-img', action='store_true', help='check every image, [m] to remove') 

    # dir_combined
    parser.add_argument('--dir-combine', action='store_true', help='combine dir')    
    parser.add_argument('--input', type=str, default='./', help='img dir path(s)')
    parser.add_argument('--output', type=str, default='raw_video/img_combined', help='output dir')
    parser.add_argument('--move', action='store_true', help='copy or move')
    parser.add_argument('--suffix', nargs='+', type=str, default=[], help=".py', '.jpg', '.txt")



    opt = parser.parse_args()
    rich.print(f"[bold white]=>({FILE.name})[/bold white] : [bold]{opt}\n")
    return opt


# introduction
def intro():
    rich.print("[gold1]-" * 40)
    rich.print(f"[gold1]Welcome to MLOps-Data-kits (v1.3)")
    rich.print("[gold1]-" * 40)
    rich.print(f"[green]--info:[/green]\t\t\tcheck img & label info. (required) --img (optional) --label ")
    rich.print(f"[green]--inspect:[/green]\t\tLabelling, GTBboxes check, Dataset washing. (required) --img --label --classes (optional) --mv-dir --window-height --window-width")
    rich.print(f"[green]--clean --cleanup:[/green]\tclean up IMG & LABEL dir. (required) --img (optional) --label") 
    rich.print(f"[green]--get-path:[/green]\t\tget images path. (required) --d --save-txt (optional) --append")
    rich.print(f"[green]--v2is:[/green]\t\t\tvideo to images. (required) --source --frame (optional) --v2is-output --view --flip --fmt-img")
    rich.print(f"[green]--vs2is:[/green]\t\tvideos to images. (required) --source --frame (optional) --vs2is-output --view --flip -- fmt-img")
    rich.print(f"[green]--is2v:[/green]\t\t\timages to video. (required) --source --last4  --video-size (optional) --fps")
    rich.print(f"[green]--play-rec:[/green]\t\tvideo paly and rec, Press r/R to record. (required) --source (optional) --delay --flip")
    rich.print(f"[green]--spider-img-baidu:[/green]\tSpider image from baidu. (required) --words")
    rich.print(f"[green]--check-every-img:[/green]\t\tUse openCV to check every image, [m] to remove image into MV_DIR. (required) --source (optional) --mv-dir")



    rich.print("[gold1]-" * 40)
    rich.print("\n\n")


def main(opt):

    # introduction
    intro()


    # ------------
    #   vars
    # ------------
    IMG_DIR = opt.img_dir               # IMG & LABEL Dir
    LABEL_DIR = IMG_DIR if not opt.label_dir else opt.label_dir
    MV_DIR = opt.mv_dir                 # MV Dir
    WRONG_IMG_DIR = opt.wrong_img_dir   # Wrong IMG Dir


    # # -------------------------------------
    # # 1. record video 
    # # -------------------------------------
    # if opt.video_rec:
    #     video_record(opt.video_rec, opt.video_rec_saveout)

    # -------------------------------------
    # 2. img & label dir info 
    # -------------------------------------
    if opt.info:
        # no IMG dir input
        if not IMG_DIR:
            LOGGER.error(f"No IMG Directory input!!! You need to input [--img], [--label](optional)")
            exit(-1)

        rich.print(f"[bold green]-------[INFO MODE]-------\n")
        _, _ = load_img_label_list(IMG_DIR, LABEL_DIR, IMG_FORMAT, True)


    # -------------------------------------
    # 3. img & label dir clean up 
    # -------------------------------------
    if opt.cleanup:
        # no IMG Dir input
        if not IMG_DIR:
            LOGGER.error(f"No IMG Directory input!!! You need to input [--img], [--label](optional)")
            exit(-1)

        
        rich.print(f"[bold green]-------[CLEAN_UP MODE]-------\n")

        # check if IMG dir == LABEL dir
        # interactive mode
        rich.print(f"[bold gold1]Please make sure IMG & LABEL directory is right!")
        rich.print("=> IMG Directory:", Path(IMG_DIR).resolve())
        rich.print("=> LABEL Directory:", Path(LABEL_DIR).resolve())

        # in case of other keys input
        while True: 
            user_answer = input('[y/n]: ')
            if user_answer in ('n', 'N', 'no', 'NO'):
                LOGGER.warning(f"please check --img & --label.")
                exit(-2)

            elif user_answer in ('y', 'Y', 'yes', 'YES'):
                img_label_dir_cleanup(IMG_DIR, LABEL_DIR, MV_DIR, IMG_FORMAT, info=True, dont_clean_empty_txt=opt.dont_clean_empty_txt)
                break


    # -------------------------------------
    # 4. inspect 
    # -------------------------------------
    if opt.inspect:
        # no IMG Dir input
        if not IMG_DIR:
            LOGGER.error(f"No IMG Directory input!!! You need to input [--img], [--label](optional)")
            exit(-1)

        # inspect
        inspect( IMG_DIR, 
                 LABEL_DIR,
                 MV_DIR,
                 WRONG_IMG_DIR,
                 opt.classes,
                 opt.window_width,
                 opt.window_height,
                 )

    # -------------------------------------
    # 5. get_path 
    # -------------------------------------
    if opt.get_path:
        get_img_path(opt.d, opt.save_txt, IMG_FORMAT, append=opt.append)


    # -------------------------------------
    # 6. video_tools => video to images 
    # -------------------------------------
    if opt.v2is:
        video_to_images(source=opt.source,      
                        output=opt.v2is_output,      
                        x=opt.frame,
                        view=opt.view,
                        flip=opt.flip,
                        img_fmt=opt.fmt_img
                        )

    # -------------------------------------
    # 6. video_tools => video to images 
    # -------------------------------------
    if opt.vs2is:
        videos_to_images(input_dir=opt.source,
                        output_dir=opt.vs2is_output,
                        x=opt.frame,
                        view=opt.view,
                        flip=opt.flip,
                        img_fmt=opt.fmt_img
                        )

    # -------------------------------------
    # 7. video_tools => play and rec 
    # -------------------------------------
    if opt.play_rec:
        play_and_record(source=opt.source, delay=opt.delay, flip=opt.flip)

    # -------------------------------------
    # 8. video_tools => images to video
    # -------------------------------------
    if opt.is2v:
        images_to_video(source=opt.source, 
                        last4=int(opt.last4), 
                        fps=opt.fps, 
                        size=opt.video_size,
                        )


    # -------------------------------------
    # 9. spider image from baidu
    # -------------------------------------
    if opt.spider_img_baidu:
        spider_img_baidu(opt.words)


    # -------------------------------------
    # 10. check_every_img
    # -------------------------------------
    if opt.check_every_img:
        image_list, _ = load_img_label_list(opt.source, opt.source, IMG_FORMAT, True)

        for img in tqdm(image_list):
            p = str(img.resolve())
            im0 = cv2.imread(p)
            print(img)
            cv2.destroyAllWindows()
            cv2.imshow(f"{img}", im0)

            key = cv2.waitKey(0)
            if key == ord('q'):
                break
            elif key == ord('m'):
                # create mv-dir if not exist
                if not Path(MV_DIR).exists():
                    Path(MV_DIR).mkdir()
                
                shutil.move(p, MV_DIR)
                LOGGER.info(f"Moving {p} into {MV_DIR}")



        cv2.destroyAllWindows()



    # -------------------------------------
    # 11. 
    # -------------------------------------
    if opt.dir_combine:
        dir_combine(input=opt.input,
                    output=opt.output,
                    suffix=opt.suffix,
                    move=opt.move)





# ---------------------------------------------------
#   main
#--------------------------------------------------
if __name__ == '__main__':
	# options
	opt = parse_opt()
	main(opt)




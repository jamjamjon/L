#!/usr/bin/env python
# -*- coding:utf-8 -*- 


# from slacking_box import video_tools
# from slacking_box import out
import os
from tqdm import tqdm 
from pathlib import Path
import argparse
import sys
import rich



from tools.video_tools import video2imgs, play



def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, default='', help='img dir path(s)')
    # parser.add_argument('--output', type=str, default='', help='output dir')
    parser.add_argument('--format', type=str, default='.jpg', help='img suffix')
    parser.add_argument('--frame', type=float, default=30, help='N frame')
    parser.add_argument('--view', action='store_true',help='imshow')
    parser.add_argument('--flip', action='store_true',help='Flip frame')

    opt = parser.parse_args()
    rich.print(opt, end="\n\n")
    return opt



VIDRO_FORMAT = ['.mp4', '.flv', '.avi']

def main(opt):


	VIDEO_LIST = [x for x in Path(opt.input).iterdir() if x.suffix in VIDRO_FORMAT]
	rich.print(f"[italic blue]==>Videos to be split:[/italic blue]\n{VIDEO_LIST}\n\n")

	idx = 1
	for video in tqdm(VIDEO_LIST):
		path = video.resolve()
		video2imgs(str(path), 
				   img_save_out=str(path.parents[0]) + "/" + str(path.stem), 
				   img_format=opt.format, 
				   show_frame=opt.view,
				   flip=opt.flip,
				   every_N_frame=opt.frame)
		idx += 1



if __name__ == "__main__":
    opt = parse_opt()
    main(opt)

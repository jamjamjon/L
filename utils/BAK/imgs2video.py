import cv2
from tqdm import tqdm
from pathlib import Path
import os
import sys
import rich
import argparse


def imgs2video(source, output_name="imgs2video", fmt=".mp4",last4=40):
    
	# load images
	IMG_FORMAT = [".jpg", ".png", ".jpeg", ".bmp"]	
	images_list = [x.resolve() for x in Path(source).iterdir() if x.suffix in IMG_FORMAT]
	rich.print(f"[gold1 bold]==>{len(images_list)} found.")

	

	# video writer
	'''
	CV_FOURCC('P', 'I', 'M', '1') = MPEG-1 codec
	CV_FOURCC('M', 'J', 'P', 'G') = motion-jpeg codec
	CV_FOURCC('M', 'P', '4', '2') = MPEG-4.2 codec
	CV_FOURCC('D', 'I', 'V', '3') = MPEG-4.3 codec
	CV_FOURCC('D', 'I', 'V', 'X') = MPEG-4 codec
	CV_FOURCC('U', '2', '6', '3') = H263 codec
	CV_FOURCC('I', '2', '6', '3') = H263I codec

	CV_FOURCC('F', 'L', 'V', '1') = FLV1 codec
	'''


	# fourcc = cv2.VideoWriter_fourcc('I', '4', '2', '0')  # avi
	fourcc = cv2.VideoWriter_fourcc('P', 'I', 'M', '1')  # mp4

	
	fps = 30
	wh_ratio = 1
	w, h = wh_ratio * 416, wh_ratio * 416
	video_size = (w, h)
	video_writer = cv2.VideoWriter(output_name + fmt,  fourcc, fps, video_size)

	key = cv2.waitKey(1)
	for img in tqdm(images_list):
		frame = cv2.imread(str(img))		
		for idx in range(last4):
			video_writer.write(frame)


		if key == ord('q'):
			break

	rich.print("[green]==>done.")  

	video_writer.release()


def parse_opt():
	parser = argparse.ArgumentParser()
	parser.add_argument('--imgs-dir', type=str, default='./', help='img dir path(s)')
	parser.add_argument('--output-name', type=str, default='imgs2video', help='output dir')
	# parser.add_argument('--fmt', type=str, default='.mp4', help='output dir')
	parser.add_argument('--last4', type=int, default=30, help='output dir')
	opt = parser.parse_args()
	rich.print(opt, end="\n\n")
	return opt


def main(opt):
	imgs2video(opt.imgs_dir, last4=opt.last4, output_name=opt.output_name)



#----------------------------------------------------
if __name__ == "__main__":
	opt = parse_opt()
	main(opt)






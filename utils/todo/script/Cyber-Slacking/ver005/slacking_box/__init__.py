#!/usr/bin/env python
# -*- coding:utf-8 -*-
import datetime
import sys

from . import z_time
from . import sprint
from . import greet

from . import rich_print
from typing import IO, TYPE_CHECKING, Any, Optional

# from slacking_box import cron

from . import folder_split
from . import bbox
from . import crawling



emoji_url = "https://apps.timwhitlock.info/emoji/tables/unicode"


#---------------------------------------------------------
#	Module: stop() 
#   => To stop right here for debugging
#----------------------------------------------------------
def stop(note="Manually stoped for debugging...", cmd=0):
	out(note, show_time=True, time_format="datetime")
	sys.exit(cmd)


#---------------------------------------------------------
#	Module: time() 
#   => Common time module, calling datetime
#----------------------------------------------------------
def time(time_format="time", time_symlink = ":"):
    return z_time.time(time_format=time_format, time_symlink=time_symlink)



#---------------------------------------------------------
#	Module: hello() 
#   => greet
#----------------------------------------------------------
def hello():
    return greet.greet()



#---------------------------------------------------------
#	Module: pout() 
#   => using print()
#----------------------------------------------------------
def p_out(*message, 
		to_console=True,			# 输出到console(default)

	    to_file=None, 				# 输出到file，两种类型，str和io_text.　１.str类型是传入地址，自动创建并且打开文件，需要指定文件的mode，即to_file_mode；2.IO_text类型，提前创建文件，直接传入open后的文件名
	    to_file_mode="a+",			#　to_file为地址时设定，默认为"w+"，如果是IO_text类型，不需要使用此参数。
	    
	    show_time=False,				# 是否显示时间
	    time_format="time",			#　可选　"time", "date", "datetime"
	    time_symlink = ":",			# 时间之间的连接符　hour:minute:second
	    
	    identifier = "[🍉 slacking_box]",	# 标识符, (out) 12:12:31 => message
	    msg_symlink=" ==> ",			# message之前的连接符号
	    pp_stream=None, pp_indent=1, pp_width=80, pp_depth=None, pp_compact=False, 		# pretty print config 

	    end="\n",					# 默认打印完换行
	    ):

    return sprint.pout(*message, 
    					to_console=to_console,
    					to_file=to_file,to_file_mode=to_file_mode,
    					show_time=show_time,time_format=time_format,
    					time_symlink = time_symlink,
    					identifier = identifier,
    					msg_symlink=msg_symlink,
		    			pp_stream=pp_stream, pp_indent=pp_indent, pp_width=pp_width, pp_depth=pp_depth, pp_compact=pp_compact,
		    			end=end,				
		    			)


#---------------------------------------------------------
#	Module: out() 
#   => using rich.print() to output to console and to file.
#----------------------------------------------------------
def out(*message: Any, 				# *objects: Any,
		to_console=True,			# 输出到console(default)
	    to_file=None, 				# 输出到file，两种类型，str和io_text.　１.str类型是传入地址，自动创建并且打开文件，需要指定文件的mode，即to_file_mode；2.IO_text类型，提前创建文件，直接传入open后的文件名
	    to_file_mode="a+",			#　to_file为地址时设定，默认为"w+"，如果是IO_text类型，不需要使用此参数。
	    
	    show_time=False,				# 是否显示时间
	    time_format="time",			#　可选　"time", "date", "datetime"
	    time_symlink = ":",			# 时间之间的连接符　hour:minute:second

	    end="\n",					# 默认打印完换行 	end: str = "\n",
	    sep= " ",
	    flush: bool = False):
	
	return rich_print.out(*message, 
						to_console=to_console,
						to_file=to_file, 
						to_file_mode=to_file_mode,
						
						show_time=show_time,
						time_format=time_format,
						time_symlink=time_symlink,
						
						sep=sep, 
						end=end,
						flush=flush)

#---------------------------------------------------------
#	Module: tvt_split() 
#  	train test val split
#----------------------------------------------------------
def tvt_split(	img_folder, ann_folder=None, 
				rate=[0.6, 0.3, 0.1], 
				seed=777, 
				cp_mv = "cp", 
				suffix=".txt",
				train_images_dir = "train_val_test/train/images",
				val_images_dir = "train_val_test/val/images",
				test_images_dir = "train_val_test/test/images",				
				train_ann_dir = "train_val_test/train/labels",	
				val_ann_dir = "train_val_test/val/labels",
				test_ann_dir = "train_val_test/test/labels",
			  ):

	return folder_split.tvt_split(	img_folder=img_folder, 
				ann_folder=ann_folder, 
				rate=rate, 
				seed=seed, 
				cp_mv = cp_mv, 
				ann_suffix=suffix,
				train_images_dir = train_images_dir,
				val_images_dir = val_images_dir,
				test_images_dir = test_images_dir,				
				train_ann_dir = train_ann_dir,	
				val_ann_dir = val_ann_dir,
				test_ann_dir = test_ann_dir,
			  )

#---------------------------------------------------------
#	Module: tv_split() 
#  	train val split
#----------------------------------------------------------
def tv_split(img_folder, ann_folder=None, 
					rate=0.8, 
					seed=777, 
					cp_mv = "cp", 
					suffix=".txt",
					train_images_dir = "train_val/train/images",
					val_images_dir = "train_val/val/images",
					train_ann_dir = "train_val/train/labels",	
					val_ann_dir = "train_val/val/labels",
					):

	return folder_split.train_val_split(img_folder=img_folder, 
			ann_folder=ann_folder, 
			rate=rate, 
			seed=seed, 
			cp_mv = cp_mv, 
			ann_suffix=suffix,
			train_images_dir = train_images_dir,
			val_images_dir = val_images_dir,
			train_ann_dir = train_ann_dir,	
			val_ann_dir = val_ann_dir,
			)

#---------------------------------------------------------
#	Module: gt_bbox_check() 
#  	train val split
#----------------------------------------------------------
def gt_bbox_check(images_dir, 
		labels_dir,
		classes=None,
		start=0,
		end=-1,
		label_type="ccwh", # yolo type. addttional type support => [x1,y1,x2,y2] and  [x1,y1,w,h]
		suffix=".txt",
		save_out="save_out",
		verbose=False,
		):
	return bbox.gt_bbox_check(images_dir=images_dir, 
				labels_dir=labels_dir,
				classes=classes,
				start=start,
				end=end,
				label_type=label_type, # yolo type. addttional type support => [x1,y1,x2,y2] and  [x1,y1,w,h]
				suffix=suffix,
				save_out=save_out,
				verbose=verbose,
				)




#---------------------------------------------------------
#	Module: crawl_images_baidu_chinese() 
#  	crawl images from Baidu.com
# 	only support chinese just now
#----------------------------------------------------------
def crawl_images_baidu_chinese(word, total_page=2, start_page=1, per_page=30, t_interval=0.05):
	crawler = crawling.Crawler(t_interval) 
	crawler.start(word, total_page, start_page, per_page)
       





















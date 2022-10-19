# encoding: utf-8

import datetime
import sys

from . import z_time
from . import sprint
from . import greet

from . import rich_print
from typing import IO, TYPE_CHECKING, Any, Optional

# from slacking_box import cron


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


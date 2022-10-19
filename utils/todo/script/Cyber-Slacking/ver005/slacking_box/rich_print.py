# encoding: utf-8
from __future__ import print_function

import rich
from typing import IO, TYPE_CHECKING, Any, Optional
from pprint import pprint
from . import z_time



doc = """
up next...
"""


#--------------------
# global variables
#--------------------
blank_space = " "
colon_mark = ":"


# --------------------------------------------------------
# Module => Use rich print() to print to console and to file.
# --------------------------------------------------------
def out(*message: Any, 				# *objects: Any,
		to_console=True,			# 输出到console(default)
	    to_file=None, 				# 输出到file，两种类型，str和io_text.　１.str类型是传入地址，自动创建并且打开文件，需要指定文件的mode，即to_file_mode；2.IO_text类型，提前创建文件，直接传入open后的文件名
	    to_file_mode="a+",			#　to_file为地址时设定，默认为"w+"，如果是IO_text类型，不需要使用此参数。
	    
	    show_time=False,				# 是否显示时间
	    time_format="time",			#　可选　"time", "date", "datetime"
	    time_symlink = ":",			# 时间之间的连接符　hour:minute:second
	    
	    end="\n",					# 默认打印完换行 	end: str = "\n",
	    sep= " ",
	    flush: bool = False
    
	    ):

	# at least one output
	assert to_console or to_file, "Error: you have to choose to output ot [file] or [console]"

	#------------------------
	# ===> Part 1. output to file
	#------------------------
	if to_file:
		if isinstance(to_file, str):	# str -> open then print
			f = open(to_file, to_file_mode)
			if show_time:	# show time or not  (optional)
				rich.print(f"[{z_time.time(time_format, time_symlink)}]",file=f, flush=flush, end="\t")
			rich.print(*message, end=end, file=f, flush=flush, sep=sep)
			f.close()
		else:	# IO_Text -> print directly
			if show_time: 
				rich.print(f"[{z_time.time(time_format, time_symlink)}]",file=to_file, flush=flush, end="\t")
			rich.print(*message, end=end, file=to_file, flush=flush, sep=sep)
			

		
	#---------------------------------------------------------------------
	# ===> Part 2. output to Console
	#---------------------------------------------------------------------
	if to_console:
		# show time or not (optional)
		if show_time:
			rich.print(f"[{z_time.time(time_format, time_symlink)}]", end="\t", sep=sep)
		rich.print(*message,
				    sep=sep,
				    end=end,
				    )

# --------------------------------------------------------
# (abandoned)Module => Use rich print() to print to console and to file.
# --------------------------------------------------------
def rich_print(*message: Any, 			# *objects: Any,
			to_console=True,			# 输出到console(default)

		    to_file=None, 				# 输出到file，两种类型，str和io_text.　１.str类型是传入地址，自动创建并且打开文件，需要指定文件的mode，即to_file_mode；2.IO_text类型，提前创建文件，直接传入open后的文件名
		    to_file_mode="a+",			#　to_file为地址时设定，默认为"w+"，如果是IO_text类型，不需要使用此参数。
		    
		    show_time=False,				# 是否显示时间
		    time_format="time",			#　可选　"time", "date", "datetime"
		    time_symlink = ":",			# 时间之间的连接符　hour:minute:second
		    
		    identifier = "(🍉 z_box)",	# 标识符, (out) 12:12:31 => message
		    msg_symlink=" ==> ",			# message之前的连接符号
		    pretty_print = True,
		    pp_stream=None, pp_indent=1, pp_width=80, pp_depth=None, pp_compact=False, 		# pretty print config 

		    end="\n",					# 默认打印完换行 	end: str = "\n",
		    sep: str = " ",

		    file: Optional[IO[str]] = None,
		    flush: bool = False
	    


		    ):

	#------------------------
	# 	global variables
	#------------------------
	global blank_space
	global colon_mark


	# at least one output
	assert to_console or to_file, "Error: you have to choose to output ot [file] or [console]"

	#------------------------
	# ===> Part 1. output to file
	#------------------------
	if to_file:

		# 1. string to be write into file
		content_2_file = ""

		# 2. show time or not  (optional)
		if show_time:	
			content_2_file	+= f"{z_time.time(time_format, time_symlink)}{msg_symlink}"
		
		# 3. concat message
		content_2_file += f"{message[0]}" 	# unwrap tuple, or pick the first item

		# 4. check the file input is "str" or "IO_Text" 
		if isinstance(to_file, str):	# str -> open then print
			f = open(to_file, to_file_mode)
			rich.print(f"{content_2_file}", end=end, file=f)
			f.close()
		else:	# IO_Text -> print directly 
			rich.print(f"{content_2_file}", end=end, file=to_file)

		
	#---------------------------------------------------------------------
	# ===> Part 2. output to Console
	# case one : sigle item	 e.g. out(f"xxx")
	# case two : multi itemS	 e.g. out(f"xxx", x_1, x_2, "xxxx")
	# solution => [1. str -> print()  2.not str -> pprint()]
	#---------------------------------------------------------------------
	if to_console:

		# 1.prefix (fixed but can modified)
		content_2_console = f"{identifier}"

		# 2.show time or not (optional)
		if show_time:
			content_2_console += f"{blank_space}{z_time.time(time_format, time_symlink)}"

		# 3.msg symlink (fixed)
		content_2_console += f"{msg_symlink}"

		# 4.print first
		rich.print(content_2_console, end="") 	# To here, it should be like this: (🍉 out) 21:44:56 ==> 
		
		# print("##########", len(message))

		# 0.nothing input
		if len(message) == 0:
			rich.print("")
		elif len(message) > 1:	# 5.multi itemS in message
			pre_is_str = True
			for idx, item in enumerate(message):
				if isinstance(item, str):	# string item -> print()
					if idx == len(message) - 1:
						rich.print(item)
					else: 
						rich.print(item, end=blank_space*2)
					pre_is_str = True	
				else:	# not string, e.g. list or dict -> pprint()
					if pre_is_str:
						rich.print("")
						if pretty_print:
							rich.print(item)
						else:
							pprint(item, stream=pp_stream, indent=pp_indent, width=pp_width, depth=pp_depth, compact=pp_compact)    # \n 
					else:
						if pretty_print:
							rich.print(item)
						else:
							pprint(item, stream=pp_stream, indent=pp_indent, width=pp_width, depth=pp_depth, compact=pp_compact)  
					pre_is_str = False
		else:	# 6.only one item in message
			if message[0] == "": 	# print("")
				rich.print("[bold red][Nothing typed...]")
			elif isinstance(*message, str): 	# string item -> print()
				rich.print(*message)
			else: 	# [dict or list] item -> pprint() 	
				rich.print("")
				if pretty_print:
					rich.print(*message)
				else:
					pprint(*message, stream=pp_stream, indent=pp_indent, width=pp_width, depth=pp_depth, compact=pp_compact)
		




if __name__ == '__main__':

	pass

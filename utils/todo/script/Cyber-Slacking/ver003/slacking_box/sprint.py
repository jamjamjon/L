# encoding: utf-8

from __future__ import print_function
import datetime
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
# Module => Use out() to print to console and to file.
# --------------------------------------------------------
def pout(*message, 
			to_console=True,			# 输出到console(default)

		    to_file=None, 				# 输出到file，两种类型，str和io_text.　１.str类型是传入地址，自动创建并且打开文件，需要指定文件的mode，即to_file_mode；2.IO_text类型，提前创建文件，直接传入open后的文件名
		    to_file_mode="a+",			#　to_file为地址时设定，默认为"w+"，如果是IO_text类型，不需要使用此参数。
		    
		    show_time=False,				# 是否显示时间
		    time_format="time",			#　可选　"time", "date", "datetime"
		    time_symlink = ":",			# 时间之间的连接符　hour:minute:second
		    
		    identifier = "(🍉 z_box)",	# 标识符, (out) 12:12:31 => message
		    msg_symlink=" ==> ",			# message之前的连接符号
		    pp_stream=None, pp_indent=1, pp_width=80, pp_depth=None, pp_compact=False, 		# pretty print config 

		    end="\n",					# 默认打印完换行
		    ):
	
	'''
	#-----------------------------
	#  	1.Quick Use
	#-----------------------------

	epoch, acc, loss = 77, 0.96712, 0.123

	==> 1.输出到file 
	# 方式１
	save_out = "test.log" 	# <class '_io.TextIOWrapper'>
	f = open(save_out, "a+")
	out(f"epoch: {epoch}  | accuracy: {acc:.2f}% | loss: {loss:.2f}%", to_file=f, to_console=False)
	f.close()

	# 方式２(recommanded)
	out(f"epoch: {epoch}  | accuracy: {acc:.2f}% | loss: {loss:.2f}%", to_file="training_info.txt", to_file_mode="a+", to_console=False)

	==> 2.输出到console
	out("123", show_time=True, time_format="time")
	out("") 	# (🍉 z_box) ==> Nothing typed...
	out()		# (🍉 z_box) ==> 



	#---------------------------
	# 	2.Finished
	#---------------------------
	- 1.自定义前缀,带有标识，(out) 12:12:31  -->  
	- 2.两种方式写入file:# 输出到file，两种类型，str和io_text.　
		- str类型是传入地址，自动创建并且打开文件，需要指定文件的mode，即to_file_mode;
		- IO_text类型，提前创建文件，直接传入open后的文件名;

		->	out(f"epoch: {epoch} | accuracy: {acc:.2f}% | loss: {loss:.2f}%", to_file="training_info.txt", to_file_mode="a+", to_console=True)
		->	out(f"epoch: {epoch} | accuracy: {acc:.2f}% | loss: {loss:.2f}%", show_time=True ,to_file="training_info.txt", to_file_mode="a+", to_console=False)	
		->	save_out = "test.log" 	# <class '_io.TextIOWrapper'>
		->	f = open(save_out, "a+")
		->	# out(f"epoch: {epoch}  | accuracy: {acc:.2f}% | loss: {loss:.2f}%", to_file=f, to_console=True, show_time=True)
		->	out(f"{epoch}\t{acc}\t{loss}\tcat", to_file=f, show_time=False, to_console=False)
		->	f.close()


	- 3. out() => 纳入pretty print,自动根据输入数据的类型进行调整，支持类型如下：
		->	out("111123", "hhhelo", dict_case) 							#  support for type print(a,b,c) 
		->	out(f"dictionay is:", "123213", dict_case, "----------") 	#  support for type print(a,b,c) 
		->	out(dict_case, f"dictionay is:", "123213", "----------") 	#  support for type print(a,b,c) 
		->	out(f"dictionay is:", array_case, "----------") 			#  support for type print(a,b,c)
		->	out(dict_case, pp_indent=2, show_time=True) 				#  pretty print
		->	out("epoch:{}, acc:{:.2f}, loss:{:.2f}".format(66, 0.94823, 0.1234), show_time=True, time_format="date") 	# support for format-string
		->	out(f"epoch: {epoch}  | accuracy: {acc:.2f}% | loss: {loss:.2f}%", show_time=True) 	 						# support for f-string
	- 4.time() => 根据fomat返回时间字符串，目前支持 "年月日 时分秒"
	- 5.hello() => 问候函数


	#---------------------------
	# 	3.To do
	#---------------------------
	- time() 提供对 week 的支持。
	- 显示代码的文件名和函数
	- 配置函数config
	- 打印一些常用的图、表、分割符号

	'''


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
			print(f"{content_2_file}", end=end, file=f)
			f.close()
		else:	# IO_Text -> print directly 
			print(f"{content_2_file}", end=end, file=to_file)

		
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
		print(content_2_console, end="") 	# To here, it should be like this: (🍉 out) 21:44:56 ==> 
		
		# print("##########", len(message))

		# 0.nothing input
		if len(message) == 0:
			print("")
		elif len(message) > 1:	# 5.multi itemS in message
			pre_is_str = True
			for idx, item in enumerate(message):
				if isinstance(item, str):	# string item -> print()
					if idx == len(message) - 1:
						print(item)
					else: 
						print(item, end=blank_space*2)
					pre_is_str = True	
				else:	# not string, e.g. list or dict -> pprint()
					if pre_is_str:
						print("")
						pprint(item, stream=pp_stream, indent=pp_indent, width=pp_width, depth=pp_depth, compact=pp_compact)    # \n 
					else:
						pprint(item, stream=pp_stream, indent=pp_indent, width=pp_width, depth=pp_depth, compact=pp_compact)  
					pre_is_str = False
		else:	# 6.only one item in message
			if message[0] == "": 	# print("")
				print("Nothing typed...")
			elif isinstance(*message, str): 	# string item -> print()
				print(*message)
			else: 	# [dict or list] item -> pprint() 	
				print("")
				pprint(*message, stream=pp_stream, indent=pp_indent, width=pp_width, depth=pp_depth, compact=pp_compact)
		



if __name__ == '__main__':

	# hello()
	pass
	
	# epoch, acc, loss = 77, 0.96712, 0.123
	# import numpy as np
	# array_case = np.random.randn(4,4)
	# dict_case = {
	# 	"a": 123,
	# 	"b": {"123": 123, "456": 456},
	# 	"c": ["777", "Beijing", 1, 2, 3, 4, 5, 6, 7, 8, 9],
	# 	"d": 456,
	# 	"e": 999
	# }
	
	# ------------------------------------
	# 1. use case to test Console output
	# ------------------------------------
	# out(f"Good evening!\tout will auto print nicely!", show_time=True)
	# out(dict_case, pp_indent=2, show_time=True) # prety print
	# out("epoch:{}, acc:{:.2f}, loss:{:.2f}".format(66, 0.94823, 0.1234), show_time=True, time_format="date") 	# # support for format-string
	# out(f"epoch: {epoch}  | accuracy: {acc:.2f}% | loss: {loss:.2f}%", show_time=True) 	 	# support for f-string
	# out("111123", "hhhelo", dict_case) 	#  support for type print(a,b,c) 
	# out(f"dictionay is:", "123213", dict_case, "----------") 	#  support for type print(a,b,c) 
	# out(dict_case, f"dictionay is:", "123213", "----------") 	#  support for type print(a,b,c) 
	# out(f"dictionay is:", array_case, "----------") 	#  support for type print(a,b,c) 
	# out("epoch:{}, acc:{}, loss:{}".format(epoch, acc, loss))

	# ------------------------------------
	# 2. use case to test File output
	# ------------------------------------	
	# out(f"epoch: {epoch} | accuracy: {acc:.2f}% | loss: {loss:.2f}%", to_file="training_info.txt", to_file_mode="a+", to_console=True)
	# out(f"epoch: {epoch} | accuracy: {acc:.2f}% | loss: {loss:.2f}%", show_time=True ,to_file="training_info.txt", to_file_mode="a+", to_console=False)
	# save_out = "test.log" 	# <class '_io.TextIOWrapper'>
	# f = open(save_out, "a+")
	# # out(f"epoch: {epoch}  | accuracy: {acc:.2f}% | loss: {loss:.2f}%", to_file=f, to_console=True, show_time=True)
	# out(f"{epoch}\t{acc}\t{loss}\tcat", to_file=f, show_time=False, to_console=False)
	# f.close()

	
	# out("")
	# out()
	# out()
	# out(array_case, f"epoch: {epoch} | acc: {acc}", dict_case, "time to go!")

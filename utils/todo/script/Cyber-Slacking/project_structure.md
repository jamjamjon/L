---cyberslacking_project
	--- package_test.py 			# TO DO
	--- project_structure.md
	--- verxxx
		--- setup.py
		--- code_test.py
		--- slacking_box
			---  __init__.py
				- stop(note="Manually stoped for debugging...", cmd=0)			-> sys.exit()用于调试
				- hello()			-> greet.py 
				- time(time_format="time", time_symlink = ":")			-> z_time.py 
				- p_out()  			-> using print() to output to console and to file.
				- out()  			-> using rich.print() to output to console and to file.

			--- sprint.py   		-> 调用print的输出(file & console)  	Done.
			--- rich_print.py		-> 调用rich的输出(file & console)		Done.
			--- greet.py 			-> 自我调侃模块						Done.
			--- z_time.py			-> 常用时间模块						Done.
			--- cron.py   			-> 定时任务							Done.
				=> quick start: 
					# def work():
					#    sb.out("[bold green]this is my job!")
					#    sb.out("[bold green]Job done!")
					#    sb.out("[bold red]==> If not stop, please press ctrl + c => exit")

					# from slacking_box import cron
					# cron.execute_after(work, after="3s")
					# cron.execute_circularly(work, interval="1s", begin_at="2021-07-20", end_at="2021-8-29 16:11:30")

				- execute_at(job = None,	
							at = "2021-7-24-11-11-30", 		# 2-way: [today -"12-27-30"] or ["2021-7-24-11-11-30"]
							scheduler = "blocking", 			# blocking , background
							triger = "cron",
							):
				- execute_after(
							job = None,
							after = "10s", 		# 3-way: [1s] [1m] [1d]  -> 1分钟、1小时后 
							scheduler = "blocking", 			# blocking , background
							triger = "cron",
							):	
				- execute_circularly(
							job = None,
							interval = "5s",					# execute at every 5second 
							begin_at = None, 					# "2021-07-20". format： "2021-7-24 14:11:30"
							end_at = None,						# "2021-7-25" : 24号晚24点结束，25号这一天不包括
							scheduler = "blocking", 			# blocking , background
							triger = "cron",
							# day_of_week="0-6"
							):




			--- video_tools.py		-> 常用video操作
				- video2imgs(	source,                             # 0: cam
				                img_save_out="video_2_images",      # save dir
				                img_format=".jpg",
				                show_frame=False,
				                flip=False,
				                every_N_frame=1,)		-> 视频按固定frame分割成图
				- play(source, flip=False, key_wait=1)  -> using opencv to play video


# encoding: utf-8

import datetime
import time
from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from . import rich_print
import rich


#------------
# to do 
#-----------------
# 触发事件退出
# listener



doc = """
#---------------------------
#	Quick Start
#---------------------------

from z_box import cron
from z_box import z

#-------------------------
#  => define your work
#-------------------------
def work():
	print("test----------------")
	print("job done! If not stop, please press [ctrl + c] => exit")



#--------------------------------------------
#  => 3-func() to cope with common siatuation
#--------------------------------------------
# cron.execute_at(work, at = "2021-7-24-23-52-50")
# cron.execute_at(work, at = "23-53-50")
# cron.execute_after(work, after="2s") 	# , scheduler = "background"
# cron.execute_circularly(work, interval="1s", begin_at="2021-07-20", end_at="2021-7-25 16:11:30")
cron.execute_circularly(work, interval="1s")


#----------------------------
#  => 另一种方式（不完善）
#---------------------------- 
# while True:
# 	cron.execute_after(work, after="3s", scheduler="background")

# 	time.sleep(4)
# 	sys.exit()
"""




# 1. [固定时间(年月日时分秒)执行一次]
def execute_at(
			job = None,
			at = "2021-7-24-11-11-30", 		# 2-way: [today -"12-27-30"] or ["2021-7-24-11-11-30"]
			scheduler = "blocking", 			# blocking , background
			triger = "cron",
			):

	# time parse 
	#  "2021-7-24-11-11-30"  or  "11-11-30" 
	# time now


	# prompt
	rich.print(f"[bold green]==> Job wil be excuted at {at}, please wait...")

	time_str = at.strip().split("-")
	if len(time_str) == 3:
		hour = at.split("-")[0]
		minute = at.split("-")[1]
		second = at.split("-")[2]

		year = datetime.datetime.today().strftime("%Y")
		month = datetime.datetime.today().strftime("%m")
		day = datetime.datetime.today().strftime("%d")

	elif len(time_str) == 6:
		year = at.split("-")[0]
		month = at.split("-")[1]
		day = at.split("-")[2]
		hour = at.split("-")[3]
		minute = at.split("-")[4]
		second = at.split("-")[5]


	if scheduler == "blocking":
		sched = BlockingScheduler()
	elif scheduler == "background":
		sched = BackgroundScheduler()

	if job:
		sched.add_job(job, triger, year=year, month=month, day=day, hour=hour, minute=minute, second=second)
		try:
			sched.start()
		except (KeyboardInterrupt, SystemExit):
			sched.shutdown() 



# 2. [x分钟、x小时后 执行一次]
def execute_after(
			job = None,
			after = "10s", 		# 3-way: [1s] [1m] [1d]  -> 1分钟、1小时后 
			scheduler = "blocking", 			# blocking , background
			triger = "cron",
			):


	span_unit = after.strip()[-1]
	span_time = int(after.strip()[: -1])

	# prompt
	rich.print(f"[bold green]==> Job wil be excuted after {after}, please wait...")

	now = datetime.datetime.today()

	if span_unit == "s":
		timedelta = datetime.timedelta(seconds=span_time)
	elif span_unit == "m":
		timedelta = datetime.timedelta(minutes=span_time)
	elif span_unit == "d":
		timedelta = datetime.timedelta(days=span_time)


	execute_time = now + timedelta


	year = execute_time.strftime("%Y")
	month = execute_time.strftime("%m")
	day = execute_time.strftime("%d")
	hour = execute_time.strftime("%H")
	minute = execute_time.strftime("%M")
	second = execute_time.strftime("%S")

	if scheduler == "blocking":
		sched = BlockingScheduler()
	elif scheduler == "background":
		sched = BackgroundScheduler()

	if job:
		sched.add_job(job, triger, year=year, month=month, day=day, hour=hour, minute=minute, second=second)
		# sched.add_listener(job_exception_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
		# print(sched.get_jobs())


		try:
			sched.start()

		except (KeyboardInterrupt, SystemExit):
			sched.shutdown()

	print(sched.get_jobs())




# [间隔时间 区间 循环执行]
def execute_circularly(
			job = None,
			interval = "5s",					# execute at every 5second 
			begin_at = None, 					# "2021-07-20". format： "2021-7-24 14:11:30"
			end_at = None,						# "2021-7-25" : 24号晚24点结束，25号这一天不包括
			scheduler = "blocking", 			# blocking , background
			triger = "cron",
			# day_of_week="0-6"
			):

	
	second = None
	minute = None
	hour = None
	day = None
	month = None
	year = None



	# prompt
	if begin_at and end_at:
		rich.print(f"[bold green]==> Job wil be excuted during {begin_at} - {end_at}, at every {interval}, please wait...")
	else:
		rich.print(f"[bold green]==> Job wil be excuted at every {interval}, please wait...")

	span_unit = interval[-1]
	span_time = int(interval[: -1])

	if span_unit == "s":
		second = "*/{}".format(span_time)
	elif span_unit == "m":
		minute = "*/{}".format(span_time)
	elif span_unit == "d":
		day = "*/{}".format(span_time)
	elif span_unit == "M": 
		month = "*/{}".format(span_time)
	elif span_unit == "h": 
		hour = "*/{}".format(span_time)
	elif span_unit == "y": 
		year = "*/{}".format(span_time)

	
	if scheduler == "blocking":
		sched = BlockingScheduler()
	elif scheduler == "background":
		sched = BackgroundScheduler()

	if job:
		sched.add_job(job, triger, 
						  year=year, month=month, day=day, hour=hour, minute=minute, second=second, 
						  start_date=begin_at, end_date=end_at,
						  ) 
		try:
			sched.start()
		except (KeyboardInterrupt, SystemExit):
			sched.shutdown() 
  



def execute_weekly():
    # scheduler.add_job(job, 'cron', day_of_week="0-6", second="*/2")	 		

    pass






#----------------
# 	jobs
#---------------
def job_example():
	print("aps testing....")

def job_execute_py(py_file="test.py"):
	import os

	command = "python " + py_file
	os.system(command)

	print("done")




if __name__ == '__main__':
	# print(z.time())
	

	# execute_at(job_example, at = "2021-7-24-12-26-50")
	# execute_at(job_example, at = "12-27-30")
	# execute_after(job_example, after = "1m")
	execute_after(job_execute_py, after="2s") 	# , scheduler = "background"
	# execute_circularly(job_example, interval="1s", begin_at="2021-07-20", end_at="2021-7-24 16:11:30")
	# execute_circularly(job_example, interval="1s")

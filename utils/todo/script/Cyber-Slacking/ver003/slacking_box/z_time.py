# encoding: utf-8
import datetime


#---------------------
# Module => time_str print
#---------------------
def time(time_format="time", time_symlink = ":"):

	"""
	=> params：
		-> time_format = "time" 	#　"time": hour,minute,second，可选"date"(year,month,day), "datetime"
		-> time_symlink = ":"  	# 时间之间的连接符　hour:minute:second
	=> test code:
		print("time:", time("time", ":"))
		print("date:", time("date", "-"))
		print("datetime:", time("datetime", "-"))

	"""

	assert time_format in ["time", "date", "datetime", "hour"], "time_format invalid!"
	fmt = ""

	if time_format == "time":
		fmt = time_symlink.join(["%H", "%M", "%S"])
	elif time_format == "date":
		# fmt = time_symlink.join(["%Y", "%m", "%d"])
		fmt = "%Y-%m-%d"
	elif time_format == "datetime":
		fmt = "%Y-%m-%d " + time_symlink.join(["%H", "%M", "%S"])
	elif time_format == "hour":
		fmt = "%H"


	return datetime.datetime.now().strftime(fmt)



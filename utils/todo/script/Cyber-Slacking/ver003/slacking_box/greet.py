# encoding: utf-8
from __future__ import print_function

from . import z_time



#------------------------
# Module =>  say_hello()
#------------------------
def greet():
	# out(f"Good evening!\tout will auto print nicely!", show_time=True)
	
	t = int(z_time.time(time_format="hour"))

	if t in range(0, 6):
		print("🔥 OMG！现在是清晨！您起得太早了吧？燃起来了^_^")
	elif t in range(6, 12):
		print("🌅 早上好，🍵咖啡+牛奶，开启美好一天！")
	elif t in range(12, 14):
		print("😎 要记得午休！中午不睡，下午瞌睡！记得保护眼睛！")
	elif t in range(14, 18):
		print("🎶 上班ing...")
	elif t in range(18, 19):
		print("🍕 下班！吃饭！")
	elif t in range(19, 23):
		print("🌙 晚上好！据说这个时间点可以培养一生的爱好！")
	elif t in range(23, 24):
		print("🌆 该睡觉了！关机！上床！晚安！")


# from slacking_box import *

import slacking_box as sb
# from slacking_box import cron

#------------------------
# 测试time模块
#------------------------
# print(sb.time())   


#------------------------
# 测试spint pout模块
#------------------------
# from slacking_box import sprint
# sprint.pout("testing pout...", show_time=True)

# sb.stop()
# ------------------------------------
# 1. use case to test Console output
# ------------------------------------
epoch, acc, loss = 77, 0.96712, 0.123
import numpy as np
array_case = np.random.randn(4,4)
dict_case = {
 "a": 123,
 "b": {"123": 123, "456": 456},
 "c": ["777", "Beijing", 1, 2, 3, 4, 5, 6, 7, 8, 9],
 "d": 456,
 "e": 999
}
# sb.pout("testing pout...", show_time=True)
# sb.pout(dict_case, pp_indent=2, show_time=True) # prety print
# sb.pout("epoch:{}, acc:{:.2f}, loss:{:.2f}".format(66, 0.94823, 0.1234), show_time=True, time_format="date")  # # support for format-string
# sb.pout(f"epoch: {epoch}  | accuracy: {acc:.2f}% | loss: {loss:.2f}%", show_time=True)      # support for f-string
# sb.pout("111123", "hhhelo", dict_case)   #  support for type print(a,b,c) 
# sb.pout(f"dictionay is:", "123213", dict_case, "----------")  #  support for type print(a,b,c) 
# sb.pout(dict_case, f"dictionay is:", "123213", "----------")  #  support for type print(a,b,c) 
# sb.pout(f"dictionay is:", array_case, "----------")  #  support for type print(a,b,c) 
# sb.pout("epoch:{}, acc:{}, loss:{}".format(epoch, acc, loss))

# ------------------------------------
# 2. use case to test File output
# ------------------------------------ 
# sb.pout(f"epoch: {epoch} | accuracy: {acc:.2f}% | loss: {loss:.2f}%", to_file="test_log.txt", to_file_mode="a+", to_console=True)
# sb.pout(f"epoch: {epoch} | accuracy: {acc:.2f}% | loss: {loss:.2f}%", show_time=True ,to_file="test_log.txt", to_file_mode="a+", to_console=False, time_format="datetime")
# save_out = "test.log"    # <class '_io.TextIOWrapper'>
# f = open(save_out, "a+")
# sb.pout(f"epoch: {epoch}  | accuracy: {acc:.2f}% | loss: {loss:.2f}%", to_file=f, to_console=True, show_time=True)
# sb.pout(f"{epoch}\t{acc}\t{loss}\tcat", to_file=f, show_time=False, to_console=False)
# f.close()


#------------------------
# 测试rich_print()模块
#------------------------
# sb.out("111123", "hhhelo", dict_case)   #  support for type print(a,b,c) 
# sb.out(f"dictionay is:", "123213", dict_case, "----------")  #  support for type print(a,b,c) 
# sb.out(dict_case, f"dictionay is:", "123213", "----------")  #  support for type print(a,b,c) 
# sb.out(f"dictionay is:", "\n", f"[bold magenta]{array_case}", "----------")  #  support for type print(a,b,c) , pretty_print=False
# sb.out("epoch:{}, accracy:{:.2f}, loss:{:.2f}".format(epoch, acc, loss))
# sb.out("a", "b", 3333, sep=" ---- " ,show_time=True, to_file="training_info.txt", time_format="time", to_console=False)

# sb.out("[italic bold green]Hello[italic yellow] World!", show_time=True, time_format="datetime")
# sb.out("[bold yellow]this is called by rich, [italic red]rich print", show_time=True, time_format="datetime")
# sb.out(f"[bold yellow]epoch: [italic red]{epoch}", "|", f"[bold yellow]accuracy: [italic red]{acc:.2f}%", "|", f"[bold yellow]loss: [italic red]{loss:.2f}%", to_console=True, show_time=True)
# sb.out(f"epoch: {epoch} | accuracy: {acc:.2f}% | loss: {loss:.2f}%", to_file="training_info.txt", to_file_mode="a+", to_console=True, show_time=True, time_format="datetime")
# sb.out(f"epoch: {epoch}", f"accuracy: {acc:.2f}% | loss: {loss:.2f}%", to_file="training_info.txt", to_file_mode="a+", to_console=True)

# save_out = "111.log"    # <class '_io.TextIOWrapper'>
# f = open(save_out, "a+")
# sb.out(f"epoch: {epoch}  | accuracy: {acc:.2f}% | loss: {loss:.2f}%", to_file=f, to_console=False, show_time=True, time_format="datetime")
# sb.out(f"{epoch}\t{acc}\t{loss}\tcat", to_file=f, show_time=False, to_console=False)
# f.close()


#------------------------
# 测试cron模块
#------------------------
def work():
   print("test----------------")
   print("job done! If not stop, please press [ctrl + c] => exit")

# sb.pout(cron.doc)

#--------------------------------------------
#  => 3-func() to cope with common siatuation
#--------------------------------------------
# cron.execute_at(work, at = "2021-7-26-11-17-00")
# cron.execute_at(work, at = "23-53-50")
# cron.execute_after(work, after="2s")    # , scheduler = "background"
# cron.execute_circularly(work, interval="1s", begin_at="2021-07-20", end_at="2021-7-29 16:11:30")
# cron.execute_circularly(work, interval="1s")

#----------------------------
#  => 另一种方式（不完善）
#---------------------------- 
# while True:
#  cron.execute_after(work, after="3s", scheduler="background")

#  time.sleep(4)
#  sys.exit()


#------------------------
# 测试hello()模块
#------------------------
# sb.hello()




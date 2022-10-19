import time, os, sched

schedule = sched.scheduler(time.time, time.sleep)

def perform_command(cmd, inc):
  os.system(cmd)
  print("task")


def timming_exe(cmd,inc=10):
  schedule.enter(inc, 0, perform_command,(cmd,inc))
  schedule.run()


print("10s--->")
timming_exe("python3 /home/user/Desktop/cv_test.py", 43200)

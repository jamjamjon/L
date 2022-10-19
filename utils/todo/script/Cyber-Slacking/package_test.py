import slacking_box as sb
# import rich

sb.out("🌉[italic bold red]晚上好，测试完代码赶紧买票！！！")
# sb.out("[italic bold blue]Message_1: rich print test", show_time=True, time_format="date")
# sb.out("[bold yellow]this is called by rich, [italic red]message...", show_time=True, time_format="datetime")

# epoch = 12
# acc = 0.981236
# loss = 1.213
# sb.out(f"[bold yellow]epoch: [italic red]{epoch}", "|", f"[bold yellow]accuracy: [italic red]{acc:.2f}%", "|", f"[bold yellow]loss: [italic red]{loss:.2f}%", to_console=True)
# sb.out(f"epoch: {epoch} | accuracy: {acc:.2f}% | loss: {loss:.2f}%", to_file="test_log.txt", to_file_mode="a+", to_console=True, show_time=True, time_format="datetime")



def work():
   sb.out("[bold green]this is my job!")
   sb.out("[bold green]Job done!")
   sb.out("[bold red]==> If not stop, please press ctrl + c => exit")


from slacking_box import cron
# cron.execute_after(work, after="3s")
# cron.execute_circularly(work, interval="1s", begin_at="2021-07-20", end_at="2021-8-29 16:11:30")

# sb.stop()
from slacking_box import video_tools
video_tools.video2imgs(source="1.mp4",
          img_save_out="video_2_images",      # save dir
          img_format=".jpg",
          show_frame=False,
          flip=False,
          every_N_frame=4,
          )
video_tools.play("1.mp4", wait=1000)

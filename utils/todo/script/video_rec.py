import cv2


#video_path = "rtsp://admin:admin12345@192.168.0.132/media/video2"
video_path = 'rtsp://admin:admin12345@192.168.0.195/h264/ch1/sub/av_stream'

videoCapture = cv2.VideoCapture(video_path)


fps = int(videoCapture.get(cv2.CAP_PROP_FPS))
w = int(videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT))
print("original size:", (w, h))
video_size = (w, h)

fourcc = cv2.VideoWriter_fourcc(*'mp4v')

video_writer = cv2.VideoWriter("./out.mp4",  fourcc, fps, video_size)

frame_num = 0

while True:
    ret, frame = videoCapture.read()
    if ret:
        cv2.imshow('frame', frame)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        video_writer.write(frame)


    else:
        print('end')
        break


videoCapture.release()

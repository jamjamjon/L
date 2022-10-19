import cv2

videoCapture = cv2.VideoCapture('/home/user/zhangjian/Models/yolov5/rknn_160/python/data/images/people_walking.mp4')

fps = int(videoCapture.get(cv2.CAP_PROP_FPS))

w = int(videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT))
print("original size:", (w, h))


# 
ratio = 0.45
video_size = (int(w*ratio), int(h*ratio))
print("after resized:", video_size)


# fourcc = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')
fourcc = cv2.VideoWriter_fourcc('I', '4', '2', '0') 

video_writer = cv2.VideoWriter("./out.avi",  fourcc, fps, video_size)


while True:
    ret, frame = videoCapture.read()
    if ret:
        frame = cv2.resize(frame, video_size)
        video_writer.write(frame)

    else:
        print('end')
        break


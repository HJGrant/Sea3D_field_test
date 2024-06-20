import cv2
import os
from gstreamer.gstreamer_pipeline import __gstreamer_pipeline
import datetime

def initialize_video_writer(data_dir):
    global cam1
    global cam2
    global out1
    global out2

    #initialise video capture object   
    cam1 = cv2.VideoCapture(__gstreamer_pipeline(camera_id=0, flip_method=0), cv2.CAP_GSTREAMER)
    #cam2 = cv2.VideoCapture(__gstreamer_pipeline(camera_id=1, flip_method=0), cv2.CAP_GSTREAMER)

    #check if video capture object was properly initialised and able to open
    if not cam1.isOpened():
        print("Cannot open camera 1")
        exit()

    #if not cam2.isOpened():
    #    print("Cannot open camera 1")
    #    exit()

    #fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out1 = cv2.VideoWriter()
    out1.open("appsrc ! video/x-raw, format=(string)BGR ! "
        "videoconvert ! video/x-raw, format=(string)I420 ! nvvidconv ! "
        "video/x-raw(memory:NVMM), format=(string)NV12 ! nvv4l2h264enc ! "
        "h264parse ! qtmux ! filesink location=test_1.mp4", cv2.CAP_GSTREAMER, 0, 60, (1920, 1080))
    
    #out2 = cv2.VideoWriter()
    #out2.open("appsrc ! video/x-raw, format=(string)BGR ! "
    #    "videoconvert ! video/x-raw, format=(string)I420 ! nvvidconv ! "
    #   "video/x-raw(memory:NVMM), format=(string)NV12 ! nvv4l2h264enc ! "
    #   "h264parse ! qtmux ! filesink location=test_2.mp4", cv2.CAP_GSTREAMER, 0, 60, (1920, 1080))

def save_video(data_dir):

    ret, frame1 = cam1.read()
    #ret, frame2 = cam2.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")

    out1.write(frame1)
    #out2.write(frame2)

    key = cv2.waitKey(1)

    if key == ord('f'):
        cv2.imshow('image',frame1)
        cv2.waitKey(0)

        frames_dir = os.path.join(data_dir, "frames")
        frame_path = os.path.join(frames_dir, datetime.datetime.time())
        
        cv2.imwrite(frame_path, frame1)

    return 0


if __name__ == "__main__":

    initialize_video_writer("../data")

    while True:
        save_video("../data")

cam1.release()
out1.release()
out2.release()
import cv2
import os
from .gstreamer.gstreamer_pipeline import __gstreamer_pipeline


def save_video(data_dir):

    ret, frame = cam1.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")

    out.write(frame)

    return 0

def initialize_video_writer(data_dir):
    global cam1
    global out

    #initialise video capture object   
    cam1 = cv2.VideoCapture(__gstreamer_pipeline(camera_id=1, flip_method=0), cv2.CAP_GSTREAMER)

    #check if video capture object was properly initialised and able to open
    if not cam1.isOpened():
        print("Cannot open camera 1")
        exit()

    video_file = os.path.join(data_dir, "cam1_left.avi")
    print(video_file)

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(video_file, fourcc, 60.0, (1920, 1080))

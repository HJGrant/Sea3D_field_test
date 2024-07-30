import cv2
import numpy as np
import os
import datetime

gst_string = "udpsrc port=5001 ! application/x-rtp,media=video,encoding-name=H264 ! queue ! rtpjitterbuffer latency=500 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! video/x-raw, format=(string)BGR ! appsink " #xvimagesink
cam1 = cv2.VideoCapture(gst_string, cv2.CAP_GSTREAMER)

try:
    while True:
        _,frame = cam1.read()

        cv2.imshow("ORIN", frame)

        key = cv2.waitKey(1)
        
        if key == ord('s'):
            print("Saving File!")
            file_path = os.path.join("data/", "frame_" + datetime.datetime.now().strftime('%d-%m-%Y_%H:%M:%S') + '.png')
            cv2.imwrite(file_path, frame)

        if key == ord('q'):
            break
except:
    print("Could Note Get Stream!")

finally:
    cam1.release()
    cv2.destroyAllWindow()
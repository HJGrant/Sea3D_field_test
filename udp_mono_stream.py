from threading import Thread, Lock
import cv2
import numpy as np
from functions.gstreamer.gstreamer_pipeline import gstreamer_pipeline
import datetime
from time import time
import queue
import os

class vStream:
    def __init__(self, src, udp_port):
        self.width = 1920
        self.height = 1080
        self.capture = cv2.VideoCapture(gstreamer_pipeline(camera_id=src, flip_method=2, display_width=self.width, display_height=self.height))
        self.fps = 60

        self.udp_stream = cv2.VideoWriter()       
        #in this stream we are applying CUDA accelerated vidoe encodig wih 'nvv4l2h264enc' and also accelerated scaling with nvvidconv
        self.udp_stream.open(f'appsrc ! video/x-raw, format=BGR ! videoconvert ! video/x-raw, format=I420 ! nvvidconv ! video/x-raw(memory:NVMM),width=(int){self.width},height=(int){self.height},format=NV12 !'
                             f' nvv4l2h264enc bitrate=8000000 insert-vui=1 ! h264parse ! rtph264pay config-interval=1 pt=96 ! '
                             f'udpsink host=192.168.194.75 port={udp_port}', cv2.CAP_GSTREAMER, 0, float(self.fps), (int(self.width),int(self.height))) 

        self.update_thread = Thread(target=self.update, args=())
        self.update_thread.daemon=True
        self.update_thread.start()

    def update(self):
        start = time()
        while True:
            ret, self.frame = self.capture.read()

            if ret:
                self.udp_stream.write(self.frame)
            else:
                print('Not able to write frame to stream.')
            
    def getFrame(self):
        return 
    
    def release(self):
        self.update_thread.join()
        self.capture.release()
        self.udp_stream.release()
    

if __name__ == "__main__":
    parent_dir = "./mono_data/"
    dir = "mono_calib_" + datetime.datetime.now().strftime('%d-%m-%Y_%H:%M:%S')
    start = time()

    data_dir = os.path.join(parent_dir, dir)

    os.mkdir(data_dir)

    cam1 = vStream(0, udp_port=5001)
    delay = 3

    try:
        
        while True:
            
            frame = cam1.getFrame()

            if time() - start > delay:
                print("Saving a Frame!")
                save_path = os.path.join(data_dir, "direct_frame_" + datetime.datetime.now().strftime('%H:%M:%S'))
                cv2.imwrite(save_path, frame)

                start = time()
        
    except Exception as e:
        print(f"Could not get frame: {e}")

    finally:
        cam1.release()
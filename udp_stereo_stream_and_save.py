from threading import Thread, Lock
import cv2
import numpy as np
from functions.gstreamer.gstreamer_pipeline import gstreamer_pipeline
import datetime
import queue
import os

class vStream:
    def __init__(self, src, data_dir, udp_port):
        self.width = 1920
        self.height = 1080
        self.capture = cv2.VideoCapture(gstreamer_pipeline(camera_id=src, flip_method=0, display_width=self.width, display_height=self.height))
        self.fps = 60

        self.udp_stream = cv2.VideoWriter()       
        #in this stream we are applying CUDA accelerated vidoe encodig wih 'nvv4l2h264enc' and also accelerated scaling with nvvidconv
        self.udp_stream.open(f'appsrc ! video/x-raw, format=BGR ! videoconvert ! video/x-raw, format=I420 ! nvvidconv ! video/x-raw(memory:NVMM),width=(int){self.width},height=(int){self.height},format=NV12 !'
                             f' nvv4l2h264enc bitrate=8000000 insert-vui=1 ! h264parse ! rtph264pay config-interval=1 pt=96 ! '
                             f'udpsink host=192.168.194.75 port={udp_port}', cv2.CAP_GSTREAMER, 0, float(self.fps), (int(self.width),int(self.height))) 

        gst_out= gst_out= f"appsrc ! video/x-raw,format=BGR ! queue ! videoconvert ! video/x-raw,format=BGRx ! nvvidconv ! nvv4l2h264enc insert-vui=1 ! avimux ! filesink location={data_dir}/frame_src_{src}_{datetime.datetime.now().strftime('%d-%m-%Y_%H:%M:%S')}.avi sync=true buffer-mode=0 buffer-size=3 "                  
        self.video_save = cv2.VideoWriter(gst_out, cv2.CAP_GSTREAMER, 0,float(45), (1920,1080))

        self.update_thread = Thread(target=self.update, args=())
        self.update_thread.daemon=True
        self.update_thread.start()

    def update(self):
        while True:
            ret, self.frame = self.capture.read()

            if ret:
                self.udp_stream.write(self.frame)
            else:
                print('Not able to write frame to stream.')

            try:
                self.video_save.write(self.frame)
            except:
                print("Not able to to save the frame to disk.")
            
    def getFrame(self):
        return self.frame
    
    def release(self):
        self.update_thread.join()
        self.capture.release()
        self.udp_stream.release()
    

if __name__ == "__main__":
    data_dir = "./data/" + datetime.datetime.now().strftime('%d-%m-%Y_%H:%M:%S')

    os.makedirs(data_dir)

    cam1 = vStream(0, data_dir, udp_port=5001)
    cam2 = vStream(1, data_dir, udp_port=5002)
    try:
        while True:
            frame1 = cam1.getFrame()
            frame2 = cam2.getFrame()
        
    except Exception as e:
        print(f"Could not get frame: {e}")

    finally:
        cam1.release()
        cam2.release()

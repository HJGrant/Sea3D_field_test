from threading import Thread, Lock
import cv2
import numpy as np
from functions.gstreamer.gstreamer_pipeline import gstreamer_pipeline
import datetime
import queue

class vStream:
    def __init__(self, src, udp_port):
        self.width = 960
        self.height = 480
        self.capture = cv2.VideoCapture(gstreamer_pipeline(camera_id=src, flip_method=0, display_width=self.width, display_height=self.height))
        self.fps = 60
        #self.frame_queue = queue.Queue(maxsize=100)
        self.lock = Lock()
        self.frame = None

        self.udp_stream = cv2.VideoWriter()       
        #in this stream we are applying CUDA accelerated vidoe encodig wih 'nvv4l2h264enc' and also accelerated scaling with nvvidconv
        self.udp_stream.open(f'appsrc ! video/x-raw, format=BGR ! videoconvert ! video/x-raw, format=I420 ! nvvidconv ! video/x-raw(memory:NVMM),width=(int){self.width},height=(int){self.height},format=NV12 ! '
                             'nvv4l2h264enc bitrate=8000000 insert-vui=1 ! h264parse ! rtph264pay config-interval=1 pt=96 ! '
                             f'udpsink host=192.168.194.75 port={udp_port}', cv2.CAP_GSTREAMER, 0, float(self.fps), (int(self.width),int(self.height))) 


        self.update_thread = Thread(target=self.update, args=())
        self.update_thread.daemon=True
        self.update_thread.start()

    def update(self):
        while True:
            _, self.frame = self.capture.read()
            self.udp_stream.write(self.frame)
            
    def getFrame(self):
        return self.frame
    
    def release(self):
        self.update_thread.join()
        self.stream_thread.join()
        self.capture.release()
        self.udp_stream.release()
    

if __name__ == "__main__":

    cam1 = vStream(0, udp_port=5001)
    cam2 = vStream(1, udp_port=5002)
    try:
        while True:
            frame1 = cam1.getFrame()
            frame2 = cam2.getFrame()
            if frame1 is not None:
                #cv2.imshow('FRAME1', frame1)
                #cv2.imshow('FRAME2', frame2)
                pass

            key = cv2.waitKey(1)
            if key == ord('q'):
                break
        
    except Exception as e:
        print(f"Could not get frame: {e}")

    finally:
        cam1.release()
        cam2.release()
from threading import Thread, Lock
import cv2
import numpy as np
from functions.gstreamer.gstreamer_pipeline import gstreamer_pipeline
import datetime
import queue

class vStream:
    def __init__(self, src, udp_port):
        self.capture = cv2.VideoCapture(gstreamer_pipeline(camera_id=src, flip_method=0))
        self.width = 640
        self.height = 320
        self.fps = 60
        self.frame_queue = queue.Queue(maxsize=100)
        self.lock = Lock()

        self.udp_stream = cv2.VideoWriter()
        #self.udp_stream.open(f'appsrc ! video/x-raw,format=BGR ! queue ! videoconvert ! x264enc insert-vui=1 ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=192.168.194.75 port={udp_port}', cv2.CAP_GSTREAMER, 0, float(self.fps), (int(self.width),int(self.height))) 
        self.udp_stream.open("appsrc ! video/x-raw, format=BGR ! videoconvert ! video/x-raw, format=I420 ! nvvidconv ! video/x-raw(memory:NVMM), format=NV12 ! "
                             "nvv4l2h264enc bitrate=8000000 insert-vui=1 ! h264parse ! rtph264pay config-interval=1 pt=96 ! "
                             f"udpsink host=192.168.194.75 port={udp_port}", cv2.CAP_GSTREAMER, 0, float(self.fps), (int(self.width),int(self.height))) 


        self.update_thread = Thread(target=self.update, args=())
        self.update_thread.daemon=True
        self.update_thread.start()

        self.stream_thread = Thread(target=self.send_to_stream, args=())
        self.stream_thread.daemon=True
        self.stream_thread.start()

    def update(self):
        while True:
            ret, frame = self.capture.read()
            if ret:
                if not self.frame_queue.full():
                    self.frame_queue.put(frame)
    
    def send_to_stream(self):
        while True:
            try:
                frame = self.frame_queue.get_nowait()
                frame = cv2.resize(frame, (self.width, self.height))
                self.udp_stream.write(frame)
            except queue.Empty:
                pass

    def getFrame(self):
        try:
            frame = self.frame_queue.queue[0]  # Peek at the front of the queue without removing it
        except IndexError:
            frame = None
        return frame
    
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
            if frame1 is not None and frame2 is not None:
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
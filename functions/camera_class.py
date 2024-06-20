from threading import Thread
import cv2
import time
from .gstreamer.gstreamer_pipeline import __gstreamer_pipeline

class vStream:
    def __init__(self, src, file):
        self.capture = cv2.VideoCapture(__gstreamer_pipeline(camera_id=src, flip_method=0))

        self.out = cv2.VideoWriter()
        self.out.open("appsrc ! video/x-raw, format=(string)BGR ! "
        "videoconvert ! video/x-raw, format=(string)I420 ! nvvidconv ! "
        "video/x-raw(memory:NVMM), format=(string)NV12 ! nvv4l2h264enc ! "
        "h264parse ! qtmux ! filesink location="+str(file), cv2.CAP_GSTREAMER, 0, 60, (1920, 1080))

        self.thread = Thread(target=self.update, args=())
        self.threadhread.daemon=True
        self.thread.start()

    def update(self):
        while True:
            _, self.frame = self.capture.read()
            self.out.write(self.frame)

        
    def getFrame(self):
        return self.frame
    

if __name__ == "__main__":

    cam1 = vStream(0)
    cam2 = vStream(1)

    while True:
        try:
            cv2.imshow('Frame 1', cam1.getFrame())
            cv2.imshow('Frame 2', cam2.getFrame())

        except:
            print("Could not get frame.")

        if cv2.waitKey(1) == ord('q'):
            cam1.capture.release()
            cam2.capture.release()
            cv2.destroyAllWindows()
            exit(1)
            break
        
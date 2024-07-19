from threading import Thread
import cv2
import numpy as np
from gstreamer.gstreamer_pipeline import gstreamer_pipeline, gstreamer_pipeline_gray8

class vStream:
    def __init__(self, src, width, height):
        self.capture = cv2.VideoCapture(gstreamer_pipeline(camera_id=src, display_width=width, display_height=height), cv2.CAP_GSTREAMER)

        self.thread = Thread(target=self.update, args=())
        self.thread.daemon=True
        self.thread.start()

    def update(self):
        while True:
            try:
                ret, self.frame = self.capture.read()
            except Exception as e:
                print(f"Could Not Capture Frame : {e}")

    def getFrame(self):
        return self.frame
    
    def release(self):
        self.capture.release()
        self.thread.join()
        cv2.destroyAllWindows()
 

width=960
height=480

cam1 = vStream(0, width, height)
cam2 = vStream(1, width, height)

while True:
    try:
        frame1 = cam1.getFrame()
        frame2 = cam2.getFrame()

        stereo = np.hstack((frame1, frame2))
        cv2.imshow("STEREO", stereo)

        key = cv2.waitKey(1)

        if key == ord('q'):
            cam1.capture.release()
            cam2.capture.release()
            cv2.destroyAllWindows()
            break

    except Exception as e:
        print(f"Could not get frame: {e}")
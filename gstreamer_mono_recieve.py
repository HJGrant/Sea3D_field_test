from threading import Thread, Lock
import cv2
import numpy as np
import datetime
from time import time
import os


class VideoRecieve:
    def __init__(self, udp_port):
        print("Setting Up Stream!")
        #gst_string = f'udpsrc port={udp_port} ! application/x-rtp, payload=96 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! video/x-raw, format=(string)BGR ! appsink ' #xvimagesink
        gst_string = f'udpsrc port={udp_port} ! application/x-rtp,media=video,payload=96,clock-rate=90000,encoding-name=H264 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! appsink ' #xvimagesink
        self.capture = cv2.VideoCapture(gst_string, cv2.CAP_GSTREAMER)
        self.width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = 60
        self.lock = Lock()
        self.frame = None

        self.update_thread = Thread(target=self.update)
        self.update_thread.daemon = True
        self.update_thread.start()

    def update(self):
        while True:
            try:
                ret, self.frame = self.capture.read()
            except Exception as e:
                print(f"Could Not Get Frame: {e}")

    def getFrame(self):
        return self.frame
    
    def release(self):
        self.stop_event.set()
        self.update_thread.join()
        self.capture.release()
    
if __name__ == "__main__":

    cam1 = VideoRecieve(udp_port=5001)

    data_path = "mono_data/mono_data_" + datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
    data_path = os.path.join(os.getcwd(), data_path)

    print(data_path)

    os.mkdir(data_path)

    delay = 5
    index = 0

    try:
        while True:
            frame = cam1.getFrame()
            key = cv2.waitKey(1)

            if frame is not None:
                cv2.imshow("FRAME", frame)

                if key == ord('s'):
                    file_path = "frame_" + datetime.datetime.now().strftime("%H:%M:%S") + ".png"
                    file_path = os.path.join(data_path, file_path)
                    cv2.imwrite(file_path, frame)

                if key == ord('d'):
                    start = time()
                    while time() - start <= delay:
                        frame = cam1.getFrame()

                    file_path = "frame_" + str(index) + ".png"
                    file_path = os.path.join(data_path, file_path)
                    cv2.imwrite(file_path, frame)

                    index += 1
            
            if key == ord('q'):
                break

    except Exception as e:
        print(f'Exception: {e}')
        
    finally:    
        cam1.capture.release()
        cv2.destroyAllWindows()
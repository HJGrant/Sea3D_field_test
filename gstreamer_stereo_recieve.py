from threading import Thread, Lock
import cv2
import numpy as np
import datetime


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
    width = 960
    height = 480


    cam1 = VideoRecieve(udp_port=5001)
    cam2 = VideoRecieve(udp_port=5002)

    try:
        while True:
            frame_left = cam1.getFrame()
            frame_right = cam2.getFrame()
            key = cv2.waitKey(1)

            if frame_left is not None and frame_right is not None:
                #cv2.imshow("FRAME", frame_left)
                frame_left = cv2.resize(frame_left, (width, height))
                frame_right = cv2.resize(frame_right, (width, height))

                stereo = np.hstack((frame_left, frame_right))
                cv2.imshow("stereo", stereo)

                if key == ord('s'):
                    cv2.imwrite("./data/stereo_"+ datetime.datetime.now().strftime('%d-%m-%Y_%H:%M:%S') + ".jpg", stereo)
            
            if key == ord('q'):
                break

    except Exception as e:
        print(f'Exception: {e}')
        
    finally:    
        cam1.capture.release()
        cv2.destroyAllWindows()
from threading import Thread, Lock, Event
import queue
import cv2
import numpy as np



class VideoRecieve:
    def __init__(self, udp_port):
        print("Setting Up Stream!")
        #gst_string = f'udpsrc port={udp_port} ! application/x-rtp, payload=96 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! video/x-raw, format=(string)BGR ! appsink ' #xvimagesink
        gst_string = f'udpsrc port={udp_port} ! application/x-rtp,media=video,payload=96,clock-rate=90000,encoding-name=H264 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! appsink ' #xvimagesink
        self.capture = cv2.VideoCapture(gst_string, cv2.CAP_GSTREAMER)
        self.width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = 60
        self.frame_queue = queue.Queue(maxsize=100)
        self.stop_event = Event()
        self.lock = Lock()

        self.update_thread = Thread(target=self.update)
        self.update_thread.daemon = True
        self.update_thread.start()

    def update(self):
        while not self.stop_event.is_set():
            ret, frame = self.capture.read()
            if ret:
                try:
                    self.frame_queue.put(frame)
                except queue.Full:
                    print('Queue Full, Dropping Frame!')

    def getFrame(self):
        try:
            frame = self.frame_queue.get_nowait()
            return frame
        except queue.Empty:
            return None
        except Exception as e:
            print(f'Exception in getFrame: {e}')
            return None
    
    def release(self):
        self.stop_event.set()
        self.update_thread.join()
        self.capture.release()
    
if __name__ == "__main__":

    cam1 = VideoRecieve(udp_port=5001)
    cam2 = VideoRecieve(udp_port=5002)

    try:
        while True:
            frame_left = cam1.getFrame()
            frame_right = cam2.getFrame()
            key = cv2.waitKey(1)
            if frame_left is not None and frame_right is not None:
                frame_left = cv2.resize(frame_left, (cam1.width, cam1.height))
                frame_right = cv2.resize(frame_right, (cam2.width, cam2.height))

                #cv2.imshow("FRAME", frame_left)
                stereo = np.hstack((frame_left, frame_right))
                cv2.imshow("stereo", stereo)

                if key == ord('s'):
                    cv2.imwrite(".data/stereo.jpg", frame_left)
            
            if key == ord('q'):
                break

    except Exception as e:
        print(f'Exception: {e}')
    finally:    
        cam1.capture.release()
        cv2.destroyAllWindows()
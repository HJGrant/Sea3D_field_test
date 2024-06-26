import cv2
print(cv2.__version__)

def gstreamer_pipeline(
        camera_id,
        sensor_mode=0,          #4 = 3856x2180 and 90fps; 3 = 3856 x 2180 FR = 29.999999 fps; 2 = 1928 x 1090 FR = 59.999999 fps;
        capture_width=3856,
        capture_height=2180,
        display_width=1920,
        display_height=1080,
        framerate=30,
        flip_method=0,
    ):
    return (
            "nvarguscamerasrc sensor-id=%d sensor-mode=%d blocksize=12609120 ! "       #12609120
            "video/x-raw(memory:NVMM), "
            "width=(int)%d, height=(int)%d,"
            "format=(string)NV12 ! "
            "nvvidconv flip-method=%d ! "
            "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
            "videoconvert ! "
            "video/x-raw, format=(string)BGR ! "
            "appsink "
            % (
                    camera_id,
                    sensor_mode,
                    capture_width,
                    capture_height,
                    flip_method,
                    display_width,
                    display_height
            )
    )

if __name__ == "__main__":

        cam1 = cv2.VideoCapture(gstreamer_pipeline(camera_id=0, flip_method=0, display_height=320, display_width=640), cv2.CAP_GSTREAMER)
        cam2 = cv2.VideoCapture(gstreamer_pipeline(camera_id=1, flip_method=0, display_height=320, display_width=640), cv2.CAP_GSTREAMER)

        udp_stream = cv2.VideoWriter()
        udp_stream.open(f'appsrc ! video/x-raw, format=BGR ! videoconvert ! video/x-raw, format=I420 ! nvvidconv ! video/x-raw(memory:NVMM),format=NV12 ! '
                             'nvv4l2h264enc bitrate=8000000 insert-vui=1 ! h264parse ! rtph264pay config-interval=1 pt=96 ! '
                             f'udpsink host=192.168.194.75 port=5001', cv2.CAP_GSTREAMER, 0, float(60), (int(640),int(320))) 


        #check if video capture object was properly initialised and able to open
        if not cam1.isOpened():
                print("Cannot open camera 1")
                exit()

        if not cam2.isOpened():
                print("Cannot open camera 1")
                exit()

        while True:
                try:
                        ret, frame1 = cam1.read()
                        ret, frame2 = cam2.read()

                        udp_stream.write(frame1)

                except Exception as e:
                       frame1 = None
                       frame2 = None
                       print(f"Could Not Get Frame: {e}")

                cv2.imshow('FRAMOS1',frame1)
                cv2.imshow('FRAMOS2', frame2)
                cv2.moveWindow('FRAMOS1', 0, 250)
                cv2.moveWindow('FRAMOS2', 1100, 250)

                if cv2.waitKey(1) == ord("q"):
                        break


        cv2.destroyAllWindows()
        cam1.release()
        cam2.release()
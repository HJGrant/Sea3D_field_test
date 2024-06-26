import cv2 
import numpy as np
import datetime
import os
import csv
from functions.pinger import save_ping_data
from functions.camera_class import vStream

def make_directories():
    #make a directory for saving the data
    parent_dir = "/home/itr/Documents/test_setup"
    dir = "data_" + datetime.datetime.now().strftime('%d-%m-%Y_%H:%M:%S')

    data_dir = os.path.join(parent_dir, dir)

    os.mkdir(data_dir)

    #initialise csv for saving the pinger data
    ping_file_name = "ping_data_" + datetime.datetime.now().strftime('%d-%m-%Y_%H:%M:%S') + ".csv"
    ping_file = os.path.join(data_dir, ping_file_name)

    ping_writer = open(ping_file, 'w', newline='')
    ping_csv = csv.writer(ping_writer, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    ping_csv.writerow(["DISTANCE", "CONFIDENCE", "TIME", "DATE"])

    #initialise video file strings
    left_stream = os.path.join(data_dir, 'left_stream_' + datetime.datetime.now().strftime('%d-%m-%Y_%H:%M:%S') + '.mp4') 
    right_stream = os.path.join(data_dir, 'right_stream_' + datetime.datetime.now().strftime('%d-%m-%Y_%H:%M:%S') + '.mp4') 

    return ping_csv, left_stream, right_stream

ping_csv, left_stream, right_stream =  make_directories()
cam1 = vStream(0)
cam2 = vStream(1)

while True:
    save_ping_data(ping_csv)

    try:
        cv2.imshow(cam1.getFrame())
        cv2.imshow(cam2.getFrame())
    except:
        print("Can't get Frames!")

    if cv2.waitKey(1) == ord('q'):
        cam1.capture.release()
        cam2.capture.release()
        cv2.destroyAllWindows()
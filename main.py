#import cv2 
import numpy as np
import datetime
import os
import csv
from functions.pinger import save_ping_data
from functions.stereo_stream import save_video, initialize_video_writer

def make_directories():
    global ping_csv
    global data_dir

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

make_directories()
initialize_video_writer(data_dir)

while True:
    save_ping_data(ping_csv)
    save_video(data_dir)    
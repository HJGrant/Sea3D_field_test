from brping import Ping1D
import os
import csv
import datetime

def save_ping_data(ping_csv):
    data = myPing.get_distance()
    if data:
        print("Distance: %s\tConfidence: %s%%" % (data["distance"], data["confidence"]))
    else:
        print("Failed to get distance data")

    ping_csv.writerow([str(data['distance']), str(data['confidence']), datetime.datetime.now().strftime('%H:%M:%S:%f')[:-3], datetime.datetime.now().strftime('%d-%m-%Y')])


myPing = Ping1D()
myPing.connect_serial("/dev/ttyUSB0", 115200)
myPing.set_speed_of_sound(1450000)

if myPing.initialize() is False:
    print("Failed to initialize Ping!")
    exit(1)
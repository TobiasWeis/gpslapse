#!/usr/bin/python
'''
this project is meant to be installed in a car.
attached will be 
- a IMU sensor via USB (tinkerforge IMU brick),
- a USB GPS mouse
- a USB camera (Logitech C920)

we want to synchronously dump image, accelerometer/gyroscope and GPS data,
save it to a database in a queryable format for image processing projects
'''
import sys
from modules import CAM, GPS, Dumper
import ConfigParser
import time
import select


Config = ConfigParser.ConfigParser()
Config.read("config.ini")

threads = []

# setup modules
#imu = IMU.IMU(Config)
#threads.append(imu)
#imu.start()

# use gps ?
_use_gps = Config.getboolean("GPS", "USE_GPS")
if _use_gps:
    gps = GPS.GPS(Config)
    threads.append(gps)
    gps.start()

cam = CAM.CAM(Config)
threads.append(cam)
cam.start()

dumper = Dumper.Dumper(Config)
threads.append(dumper)
dumper.start()


# wait a little for the user to see if everything went right
time.sleep(2)

# start capture
shutdown=False

output_path = Config.get("CAM", "FILEPATH")

cnt_frames_total = 0

_wait = 5
ts_last_saved = time.time()

while shutdown==False:
    while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        line = sys.stdin.readline()
        if line:
            print "Keyboard Interrupt, shutting down."
            shutdown = True
        else:
            # stdin is gone/closed, exit
            print "EOF!"
            shutdown = True
    else:
        for t in threads:
            if t.shutdown == True:
                print "One or more threads terminated, shutting down."
                shutdown = True
        #print(imu.get())
        #print(cam.get())

        cnt_frames_total += 1
        #http://stackoverflow.com/questions/1781571/how-to-concatenate-two-dictionaries-to-create-a-new-one-in-python
        # only dump we have a gps coordinate
        if _use_gps:
            if gps.get()[0]:
                if time.time() - ts_last_saved > _wait:
                    print "Saving"
                    frame = {}
                    frame["fn"] = cnt_frames_total
                    #frame_total = dict(imu.get(), **cam.get())
                    frame_total = dict(cam.get())
                    frame_total.update(frame)

                    frame_total.update(gps.get()[1])
                    fname = output_path + "%d" % frame_total["ts_cam"]  + ".xml"
                    dumper.dump(frame_total, fname)
                    ts_last_saved = time.time()
            else:
                print "Waiting for GPS to become ready"
        else:
            if time.time() - ts_last_saved > _wait:
                print "Saving"
                frame = {}
                frame["fn"] = cnt_frames_total
                frame_total = dict(imu.get(), **cam.get())
                frame_total.update(frame)

                fname = output_path + "%d" % frame_total["ts_cam"]  + ".xml"
                dumper.dump(frame_total, fname)
                ts_last_saved = time.time()

# close all threads
for t in threads:
    t.shutdown = True
    t.join()


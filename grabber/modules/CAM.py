from __future__ import print_function
import __builtin__

import cv2
import threading
import os

from utils import *

def print(*args, **kwargs):
    '''custom print function, maybe use for logging later'''
    __builtin__.print("[CAM - %s] %s " % (tsms2hr(tsms()), args[0]))

class CAM(threading.Thread):
    def __init__(self, config):
        threading.Thread.__init__(self)
        self.shutdown = False

        self.device = int(config.get("CAM", "DEVICE"))
        print("device-number: %d" % (self.device))
        self.cam = cv2.VideoCapture(self.device)
        if not self.cam.isOpened():
            print("Could not open Camera !")
        else:
            print("Successfully opened device number %d" % self.device)

        # get the path where images should be saved to
        self.path = config.get("CAM", "FILEPATH")
        if not os.path.isdir(self.path):
            print("Creating image directory %s" % self.path)
            os.mkdir(self.path)

        # set parameters
        self.cam.set(3, config.getint("CAM", "WIDTH")) # width
        self.cam.set(4, config.getint("CAM", "HEIGHT"))  # height

        # lets see if opencv took our parameters,
        # and if the cam supports it:
        self.w = self.cam.get(3)
        self.h = self.cam.get(4)

        print("P#3: %s" % self.w)
        print("P#4: %s" % self.h)

        # fps stuff
        self.last_shown_fps = time.time()
        self.cnt_frames = 0

    def run(self):
        while not self.shutdown:
            ret,self.frame = self.cam.read()
            self.cnt_frames += 1

            if time.time() - self.last_shown_fps >= 1:
                print("%d fps" % self.cnt_frames)
                self.cnt_frames = 0
                self.last_shown_fps = time.time()

            self.ts = tsms()
            time.sleep(.001)
            # FIXME: semaphore ?


    def get(self):
        frame = {}
        frame["ts_cam"] = self.ts
        frame["uri"] = "%d" % frame["ts_cam"] + ".png"
        frame["imgwidth"] = self.w
        frame["imgheight"] = self.h
        cv2.imwrite(self.path + frame["uri"], self.frame)
        return frame



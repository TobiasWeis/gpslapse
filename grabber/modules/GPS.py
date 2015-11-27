from __future__ import print_function
import __builtin__
import threading
from time import *
import time
from utils import *
from gps import *

def print(*args, **kwargs):
    '''custom print function, maybe use for logging later'''
    __builtin__.print("[GPS - %s] %s" % (tsms2hr(tsms()), args[0]))

class GPS(threading.Thread):
    def __init__(self, config):
        threading.Thread.__init__(self)
        self.shutdown = False
        self.gpsd = gps(mode=WATCH_ENABLE)
        self.ts = -1
        print("Started.")

    def run(self):
        while not self.shutdown:
            self.gpsd.next()
            self.ts = tsms()
        print("Shutting down.")

    def get(self):
        if self.gpsd.fix.latitude == 0.0:
            print("GPS not ready yet")
            return False, -1

        frame = {}
        frame["ts_gps"] = self.ts
        frame["latitude"] = self.gpsd.fix.latitude
        frame["longitude"] = self.gpsd.fix.longitude
        frame["altitude"] = self.gpsd.fix.altitude
        frame["eps"] = self.gpsd.fix.eps
        frame["epx"] = self.gpsd.fix.epx
        frame["epv"] = self.gpsd.fix.epv
        frame["ept"] = self.gpsd.fix.ept
        frame["speed"] = self.gpsd.fix.speed
        frame["clibm"] = self.gpsd.fix.climb
        frame["track"] = self.gpsd.fix.track
        frame["mode"] = self.gpsd.fix.mode
        #frame["sats"] = self.gpsd.satellites # problems converting to dict for XML dumper

        return True, frame

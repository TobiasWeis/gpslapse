from __future__ import print_function
import __builtin__
import threading
from utils import *
#import dicttoxml
import datetime

import sys
sys.path.append("../")
from common import DBInterface


def print(*args, **kwargs):
    '''custom print function, maybe use for logging later'''
    __builtin__.print("[Dumper - %s] %s " % (tsms2hr(tsms()), args[0]))


class Dumper(threading.Thread):
    def __init__(self, config):
        threading.Thread.__init__(self)
        self.shutdown = False

        self.format = config.get("DUMPER", "FORMAT") 
        self.folder = config.get("CAM", "FILEPATH")
        print("Started as %s dumper" % self.format)

        if self.format == "SQLite":
            print("Using SQLite, inserting sensor and sequence information")
            # open database
            self.dbi = DBInterface.DBInterface()

            # write sensor, ged id
            self.sensor_id = self.dbi.insert_sensor("Logitech C920")
            if self.sensor_id is None:
                print("Sensor was already in database, re-using")
                self.sensor_id = self.dbi.get_sensor_id_from_name("Logitech C920")

            # write sequence, get id
            self.sequence_id = self.dbi.insert_sequence(datetime.datetime.now(), self.sensor_id, self.folder)


    def run(self):
        # may use it later to have a queue
        pass

    def dump(self, frame, fname):
        if self.format == "XML":
            # frame is a dict with all values in it
            xml = dicttoxml.dicttoxml(frame)
            f = open(fname, 'w+')
            f.write(xml)
            f.close()
        elif self.format == "SQLite":
            self.dbi.insert_frame(id_sequence=self.sequence_id, img_uri=frame["uri"],ts_cam=frame["ts_cam"],img_w=frame["imgwidth"], img_h=frame["imgheight"],lat=frame["latitude"],lon=frame["longitude"], speed=frame["speed"], ts_gps=frame["ts_gps"],altitude=frame["altitude"]  )





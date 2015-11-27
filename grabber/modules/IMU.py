from __future__ import print_function
import __builtin__
import threading
import time
from utils import *
from tinkerforge.ip_connection import IPConnection
from tinkerforge import brick_imu

'''
FIXME: it is not really necessary to have the IMU module run
in a thread, as we use a callback function anyway
'''

def print(*args, **kwargs):
    '''custom print function, maybe use for logging later'''
    __builtin__.print("[IMU - %s] %s" % (tsms2hr(tsms()), args[0]))

class IMU(threading.Thread):
    def __init__(self, config):
        threading.Thread.__init__(self)
        self.shutdown = False

        # DAEMON CONNECTION CONFIG
        self.host = config.get("IMU", "HOST")
        self.port = config.getint("IMU", "PORT")
        self.uid = config.get("IMU", "UID")

        # WHAT DATA SHOULD BE READ AND RETURNED ?
        self.return_quat = config.getboolean("IMU", "DATA_QUATERNION")
        self.return_accel = config.getboolean("IMU", "DATA_ACCELEROMETER")
        self.return_avel = config.getboolean("IMU", "DATA_AVEL")

        print("host: %s" % (self.host))
        print("port: %s" % (self.port))
        print("uid: %s" % (self.uid))

        self.ipcon = IPConnection() # Create IP connection
        self.imu = brick_imu.IMU(self.uid, self.ipcon) # Create device object

        self.ipcon.connect(self.host, self.port) # Connect to brickd
        # Don't use device before ipcon is connected

        # Set period for quaternion callback to 1/10s
        if self.return_quat:
            self.imu.set_quaternion_period(10)
            # Register quaternion callback
            self.imu.register_callback(self.imu.CALLBACK_QUATERNION, self.cb_quaternion)
            self.quaternion = []

        if self.return_avel:
            self.imu.set_angular_velocity_period(10)
            self.imu.register_callback(self.imu.CALLBACK_ANGULAR_VELOCITY, self.cb_avel)
            self.avel = []

        if self.return_accel:
            self.imu.set_acceleration_period(10)
            self.imu.register_callback(self.imu.CALLBACK_ACCELERATION, self.cb_acceleration)
            self.acceleration = []

    def cb_acceleration(self, x,y,z):
        self.acceleration = [x,y,z]
        self.ts_acceleration = tsms()

    def cb_avel(self, ax,ay,az):
        # deg/13.375s
        self.avel = [ax,ay,az]
        self.ts_avel = tsms()

    def cb_quaternion(self, x, y, z, w):
        # FIXME: semaphore ?
        self.quaternion = [x,y,z,w]
        self.ts_quaternion = tsms()

    def quit(self):
        self.ipcon.disconnect()

    def run(self):
        while not self.shutdown:
            time.sleep(1)
        print("Shutting down.")

    def get(self):
        frame = {}
        frame["ts_acceleration"] = self.ts_acceleration
        frame["ts_quaternion"] = self.ts_quaternion
        # FIXME: semaphore ?
        if self.return_quat:
            frame["quaternion"] = self.quaternion
        if self.return_accel:
            frame["acceleration"] = self.acceleration
        if self.return_avel:
            frame["avel"] = self.avel
        return frame

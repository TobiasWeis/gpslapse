#!/usr/bin/python
import cv2
import numpy as np
import math

class gauge():
    def __init__(self):
        self.speedMax = 200
        self.tachoSize = 100
        self.activeAngles = math.radians(300)
        self.restAngles = (2.*math.pi - self.activeAngles)

    def paint(self, speed):
        im = np.zeros((480,640,4), np.uint8)
        m = (im.shape[1]/2, im.shape[0]/2)

        tick = self.activeAngles / float(self.speedMax)

        # draw speed texts and ticks
        for s in range(0,self.speedMax+5,10):
            p1 = ((self.tachoSize-10)*math.cos(s*tick - math.pi - self.restAngles), (self.tachoSize - 10)*math.sin(s*tick - math.pi - self.restAngles))
            p2 = (self.tachoSize*math.cos(s*tick - math.pi - self.restAngles), self.tachoSize*math.sin(s*tick - math.pi - self.restAngles))
            p3 = ((self.tachoSize + 30)*math.cos(s*tick - math.pi - self.restAngles), (self.tachoSize+30)*math.sin(s*tick - math.pi - self.restAngles))

            cv2.line(im, (int(m[0]+p1[0]), int(m[1]+p1[1])), (int(m[0]+p2[0]),int(m[1]+p2[1])), (255,255,255, 255), 3)

            if s % 50 == 0:
                cv2.putText(im, "%d" % s, (int(m[0]+p3[0]-12),int(m[1]+p3[1])), cv2.FONT_HERSHEY_SIMPLEX, .7, (255,0,0,56), 10)
                cv2.putText(im, "%d" % s, (int(m[0]+p3[0]-12),int(m[1]+p3[1])), cv2.FONT_HERSHEY_SIMPLEX, .7, (128,128,128,255), 3)
                cv2.putText(im, "%d" % s, (int(m[0]+p3[0]-12),int(m[1]+p3[1])), cv2.FONT_HERSHEY_SIMPLEX, .7, (255,255,255,255), 1)


        angle = speed*tick - self.restAngles

        p = (self.tachoSize*math.cos(angle - math.pi), self.tachoSize*math.sin(angle - math.pi))
        cv2.line(im, (m[0],m[1]), (int(m[0]+p[0]),int(m[1]+p[1])), (255,0,0, 255), 3)

        return im

#!/usr/bin/python
import numpy as np
import cv2
from common import DBInterface
from gauge import *
import math
from utils import *
import os
import datetime
import time
from multiprocessing import Pool

from osmmap import *
from basemap import *
from settings import *

settings = Settings()
g = gauge()

bm = BaseMap()
om = OSMMap()

# get coordinates from database
dbi = DBInterface.DBInterface()
print "Getting all sequences"
sequences = dbi.get_all_sequences()
frames = []

coordt = []
np_coords = np.empty((0,2), np.float64)

kms = 0.
old_coords = None

for s in sequences[:]:
    if s.id == 56:
        folder = s.folder
        print "Reading images from %s" % folder
        print "Got sequence w/ id: ", s.id
        sframes = dbi.get_frames(s.id)[::1] # FIXME: remove limit to 200

        # first run, get all coords
        s = time.time()
        last = []
        for i,f in enumerate(sframes):
            print "%d/%d" % (i, len(sframes))
            coordt.append([f.lat, f.lon])
            if f.lat == None or f.lon == None:
                print "lat or lon was None !"
                np_coords = np.append(np_coords, np.array([[last[0], last[1]]]), axis=0)
            else:
                last = [f.lat, f.lon]
                np_coords = np.append(np_coords, np.array([[f.lat, f.lon]]), axis=0)
        om.coordinates = np_coords
        print "First run took: ", time.time() - s


        # second run, do gauge, images, km calculations, map
        s = time.time()
        for i,f in enumerate(sframes):
            img = cv2.imread(folder + "/" + f.img_uri)

            if f.speed != None:
                kmh = int((f.speed)*60*60)/1000
            else:
                kmh = 0 

            s1 = time.time()
            om.plot_map(i,kmh, settings.outdir + "/map_image_%08d.png" % (i))
            print "Map took: ", time.time() - s1

            if settings.compute_kmh:
                if old_coords == None:
                    if f.lat != None and f.lon != None:
                        old_coords = [f.lat, f.lon]
                else:
                    if f.lat != None and f.lon != None:
                        dx = 71.5 * (f.lon - old_coords[1])
                        dy = 111.3 * (f.lat - old_coords[0])
                        old_coords = [f.lat, f.lon]
                        kms += math.sqrt(dx * dx + dy * dy)
                        #t_gps = f.ts_gps
                        #t_str = datetime.datetime.fromtimestamp(int(t_gps)).strftime('%d.%m.%Y %H:%M:%S')
                        cv2.putText(img,"%.2f km" % (kms), (10,40), cv2.FONT_HERSHEY_SIMPLEX, 1, 255)

            s1 = time.time()
            if settings.compute_gauge:
                speedgauge = g.paint(kmh)
                gaugename = settings.outdir + "/gauge_%08d.png" %i
                cv2.imwrite(gaugename, speedgauge)

            if settings.compute_images:
                cv2.imwrite(settings.outdir + "/img_%08d.png" %i, img)
        print "Second run took: ", time.time() - s

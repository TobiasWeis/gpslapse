#!/usr/bin/python
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import matplotlib.image as image
import numpy as np
import cv2
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
from common import DBInterface
import pickle
from gauge import *
import math
from utils import *
from smopy import smopy
import os
import datetime

outdir = "/data/tmp_files/"
try:
    os.mkdir(outdir)
except:
    print "Directory already exists"

class OSMMap():
    def __init__(self):
        self.values = np.empty((0,2), np.float64)
        self.coordinates = np.empty((0,2), np.float64)

        self.fig2, self.axes2 = plt.subplots(nrows=1)
        self.initial = True
        self.initial_coords = True
        self.map = None
        self.fig_map, ax = plt.subplots(ncols=1, nrows=1)

    # ts is just cnt of the array
    def plot_map(self, ts):
        if self.initial_coords:
            # for whole sequences
            if True:
                ll_lon = np.min(self.coordinates[:,1]) - 0.0001 
                ll_lat = np.min(self.coordinates[:,0]) - 0.0001

                ur_lon = np.max(self.coordinates[:,1]) + 0.0001
                ur_lat = np.max(self.coordinates[:,0]) + 0.0001

                #47.623333, 3.306532
                #ll_lat = 47.623333
                #ll_lon = 3.306532

                # 48.043356, 18.272896
                #ur_lat = 52.604856
                #ur_lon = 18.272896
            else:
                # for area around current position
                ll_lon = self.coordinates[ts,1] - 0.001
                ll_lat = self.coordinates[ts,0] - 0.001
                ur_lon = self.coordinates[ts,1] + 0.001
                ur_lat = self.coordinates[ts,0] + 0.001
            
            # get map
            try:
                print "Getting map"
                self.map = smopy.Map((ll_lat, ll_lon, ur_lat, ur_lon), z=6)
                x,y = self.map.to_pixels(self.coordinates[:,0], self.coordinates[:,1])

                self.fig_map, ax = plt.subplots(ncols=1, nrows=1)
                ax = self.map.show_mpl(ax=ax)
                ax.plot(x,y,'go', ms=2, mew=0)

                cc = self.map.to_pixels(self.coordinates[ts,0], self.coordinates[ts,1])
                self.current_coord = ax.plot(cc[0], cc[1], 'ro', ms=10)

                # only if we do not refresh the map
                self.initial_coords = False
            except Exception,e:
                print "Exception in plot_map: ", e
        else:
            try:
                self.current_coord[0].set_xdata(self.map.to_pixels(self.coordinates[ts,0], self.coordinates[ts,1])[0])
                self.current_coord[0].set_ydata(self.map.to_pixels(self.coordinates[ts,0], self.coordinates[ts,1])[1])
            except Exception, e:
                print e

        return fig2data(self.fig_map)

class BalticMap():
    def __init__(self):

        '''
        self.fig = plt.figure(figsize=(10,10))
        self.map = Basemap(
                urcrnrlat=71.8,
                urcrnrlon=37.7,
                llcrnrlat=48.,
                llcrnrlon=3.08,
                    #resolution='h', 
                    resolution='l',
                    area_thresh=5000,
                    projection='cass', lat_0 = 50., lon_0 = 30.
                    )
        '''
        self.fig = plt.figure(figsize=(10,20))


        ax = self.fig.add_axes([0, 0, 1, 1])
        ax.axis('off')

        self.map = Basemap(
                #49.267693, 8.406459 # medersche
                #50.166281, 8.659168 # frankfurt mellsig
                urcrnrlat = 51.7,
                urcrnrlon = 10.1,
                llcrnrlat = 48.3,
                llcrnrlon = 6.1,
                    #resolution='h', 
                    resolution='c',
                    area_thresh=5000,
                    projection='cass', lat_0 = 50., lon_0 = 8.65
                    )

        #'''

        self.map.etopo()
        self.map.drawcountries(color='k', linewidth=1)
        self.map.drawcoastlines(color='k', linewidth=1)

        self.g = gauge()

    def show_coords(self, coords):
        lat,lon = coords[0], coords[1]
        print "Plotting for coordinates lat: ",lat," ,lon: ",lon
        x,y = self.map(lon, lat)
        self.map.plot(x, y, 'bo', markersize=10)

        benz = np.array(Image.open('jaguar.png'))
        im = OffsetImage(benz, zoom=1)
        ab = AnnotationBbox(im, (x,y), xycoords='data', frameon=False)

        # Get the axes object from the basemap and add the AnnotationBbox artist
        self.map._check_ax().add_artist(ab)
        plt.show()

    def get_angle(self, x1, y1, x2, y2):
        from math import atan2, degrees, pi
        dx = x2 - x1
        dy = y2 - y1
        rads = atan2(-dy,dx)
        rads %= 2*pi
        degs = degrees(rads)
        return degs


    def rotateAndScale(self, img, scaleFactor = 0.5, degreesCCW = 30):
        (oldY,oldX) = img.shape[0:2] #note: numpy uses (y,x) convention but most OpenCV functions use (x,y)
        M = cv2.getRotationMatrix2D(center=(oldX/2,oldY/2), angle=degreesCCW, scale=scaleFactor) #rotate about center of image.

        #choose a new image size.
        newX,newY = oldX*scaleFactor,oldY*scaleFactor
        #include this if you want to prevent corners being cut off
        r = np.deg2rad(degreesCCW)
        newX,newY = (abs(np.sin(r)*newY) + abs(np.cos(r)*newX),abs(np.sin(r)*newX) + abs(np.cos(r)*newY))

        #So I will find the translation that moves the result to the center of that region.
        (tx,ty) = ((newX-oldX)/2,(newY-oldY)/2)
        M[0,2] += tx #third column of matrix holds translation, which takes effect after rotation.
        M[1,2] += ty

        rotatedImg = cv2.warpAffine(img, M, dsize=(int(newX),int(newY)))
        return rotatedImg

    def show_coord_train(self, coords, cnt=0):
        thismap = self.map
        #thismap = pickle.load(open('map.pickle','rb'))

        for i in range(0,len(coords)-1):
            lat,lon = coords[i][0], coords[i][1]
            lat1,lon1 = coords[i+1][0], coords[i+1][1]

            #print "Plotting for coordinates lat: ",lat," ,lon: ",lon
            x,y = thismap(lon, lat)
            x1,y1 = thismap(lon1, lat1)
            thismap.plot(x, y, 'bo', markersize=10)
            thismap.plot((x,x1),(y,y1), 'b-')

        x_o, y_o = 0,0 
        try:
            lat_o, lon_o = coords[-2][0], coords[-2][1]
            x_o, y_o = thismap(lon_o, lat_o)
        except Exception as e:
            print e
            pass

        lat,lon = coords[-1][0], coords[-1][1]
        x,y = thismap(lon, lat)

        thismap.plot(x, y, 'bo', markersize=10)

        # rotate car icon acoording to last two coordinates
        benz = cv2.imread("jaguar.png", -1)

        try:
            ang = 180 - self.get_angle(x,y,x_o,y_o)
            dst = self.rotateAndScale(benz, 1., ang)
        except Exception as e:
            print "Rotate: ", e
            dst = benz
            pass

        # only plot the benz for the last coord 
        # if you want to rotate by 90, use np.rot90(benz)
        im = OffsetImage(dst, zoom=1.)
        try:
            self.ab.remove()
            del self.ab
        except Exception as e:
            print e
            pass
        self.ab = AnnotationBbox(im, (x,y), xycoords='data', frameon=False)

        # Get the axes object from the basemap and add the AnnotationBbox artist
        thismap._check_ax().add_artist(self.ab)
        with open('./tmp_files/map_image_%08d.png' % cnt, 'w') as outfile:
            self.fig.canvas.print_png(outfile)

bm = BalticMap()
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
    if s.id == 51:
        print "Got sequence w/ id: ", s.id
        sframes = dbi.get_frames(s.id)
        # first run, get all coords
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


        # second run, do gauge, images, km calculations, map
        for i,f in enumerate(sframes):
            img = cv2.imread("/media/weis/Transcend/Testfahrt/" + f.img_uri)

            cv2.imwrite(outdir + "/map_image_%08d.png" % i, cv2.cvtColor(om.plot_map(i), cv2.COLOR_BGR2RGB))

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
                    #cv2.putText(img,"%s - %.2f km" % (t_str, kms), (10,40), cv2.FONT_HERSHEY_SIMPLEX, 1, 255)

            speedgauge = None
            if f.speed != None:
                speedgauge = bm.g.paint(int((f.speed)*60*60)/1000)
            else:
                speedgauge = bm.g.paint(int((0)*60*60)/1000)

            gaugename = outdir + "/gauge_%08d.png" %i
            #print gaugename
            cv2.imwrite(gaugename, speedgauge)
            cv2.imwrite(outdir + "/img_%08d.png" %i, img)
            #bm.show_coord_train(coordt, i)

print "Got %d frames !" % (len(frames))

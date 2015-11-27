#!/usr/bin/python
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import matplotlib.image as image
import numpy as np
import cv2
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
from common import DBInterface

class BalticMap():
    def __init__(self):

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
        self.map = Basemap(
                #49.267693, 8.406459 # medersche
                #50.166281, 8.659168 # frankfurt mellsig
                urcrnrlat = 50.5,
                urcrnrlon = 8.8,
                llcrnrlat = 49.5,
                llcrnrlon = 8.5,
                    #resolution='h', 
                    resolution='l',
                    area_thresh=5000,
                    projection='cass', lat_0 = 50., lon_0 = 8.65
                    )
        '''

        self.map.etopo()
        self.map.drawcountries(color='k', linewidth=1)
        self.map.drawcoastlines(color='k', linewidth=1)

    def show_coords(self, coords):
        lat,lon = coords[0], coords[1]
        print "Plotting for coordinates lat: ",lat," ,lon: ",lon
        x,y = self.map(lon, lat)
        self.map.plot(x, y, 'bo', markersize=10)

        benz = np.array(Image.open('benz.png'))
        # if you want to rotate by 90, use np.rot90(benz)
        im = OffsetImage(benz, zoom=1)
        ab = AnnotationBbox(im, (x,y), xycoords='data', frameon=False)

        # Get the axes object from the basemap and add the AnnotationBbox artist
        self.map._check_ax().add_artist(ab)
        plt.show()

    def show_coord_train(self,coords):
        for i in range(0,len(coords)-1):
            lat,lon = coords[i][0], coords[i][1]
            lat1,lon1 = coords[i+1][0], coords[i+1][1]

            print "Plotting for coordinates lat: ",lat," ,lon: ",lon
            x,y = self.map(lon, lat)
            x1,y1 = self.map(lon1, lat1)
            self.map.plot(x, y, 'bo', markersize=10)
            self.map.plot((x,x1),(y,y1), 'b-')

        lat,lon = coords[-1][0], coords[-1][1]
        print "Plotting for coordinates lat: ",lat," ,lon: ",lon
        x,y = self.map(lon, lat)
        self.map.plot(x, y, 'bo', markersize=10)

        # only plot the benz for the last coord 
        benz = np.array(Image.open('benz.png'))
        # if you want to rotate by 90, use np.rot90(benz)
        im = OffsetImage(benz, zoom=1)
        ab = AnnotationBbox(im, (x,y), xycoords='data', frameon=False)

        # Get the axes object from the basemap and add the AnnotationBbox artist
        self.map._check_ax().add_artist(ab)
        plt.savefig("map_image.png")
        plt.show()

bm = BalticMap()

# get coordinates from database
dbi = DBInterface.DBInterface()
print "Getting all sequences"
sequences = dbi.get_all_sequences()
frames = []

coordt = []

for s in sequences[:1]:
    print "Got sequence w/ id: ", s.id
    for f in dbi.get_frames(s.id):
        coordt.append([f.lat, f.lon])


print "Got %d frames !" % (len(frames))
bm.show_coord_train(coordt)

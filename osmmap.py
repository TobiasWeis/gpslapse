import smopy
import numpy as np
from utils import *
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
import cv2

class OSMMap():
    def __init__(self):
        self.values = np.empty((0,2), np.float64)
        self.coordinates = np.empty((0,2), np.float64)

        self.fig2, self.axes2 = plt.subplots(nrows=1)
        self.initial = True
        self.initial_coords = True
        self.map = None
        self.fig_map, ax = plt.subplots(ncols=1, nrows=1)

    def get_angle(self, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        rads = atan2(-dy,dx)
        rads %= 2*pi
        degs = degrees(rads)
        return degs


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
                #x,y = self.map.to_pixels(self.coordinates[:,0], self.coordinates[:,1])

                self.fig_map, ax = plt.subplots(ncols=1, nrows=1)
                ax = self.map.show_mpl(ax=ax)
                
                for i in range(0,self.coordinates.shape[0]):
                    coords = self.map.to_pixels(self.coordinates[i,0], self.coordinates[i,1])
                    ax.plot(coords[0], coords[1], 'bo', ms=3)

                cc = self.map.to_pixels(self.coordinates[ts,0], self.coordinates[ts,1])
                self.current_coord = ax.plot(cc[0], cc[1], 'ro', ms=10)

                # only if we do not refresh the map
                self.initial_coords = False # FIXME: test!
            except Exception,e:
                print "Exception in plot_map: ", e
        else:
            try:
                self.current_coord[0].set_xdata(self.map.to_pixels(self.coordinates[ts,0], self.coordinates[ts,1])[0])
                self.current_coord[0].set_ydata(self.map.to_pixels(self.coordinates[ts,0], self.coordinates[ts,1])[1])
            except Exception, e:
                print e

        return fig2data(self.fig_map)


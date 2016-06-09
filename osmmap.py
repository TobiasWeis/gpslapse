import smopy
import numpy as np
from utils import *
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
import cv2
import pickle
import os

class OSMMap():
    def __init__(self):
        self.values = np.empty((0,2), np.float64)
        self.coordinates = np.empty((0,2), np.float64)

        self.fig2, self.axes2 = plt.subplots(nrows=1)
        self.initial = True
        self.initial_coords = True
        self.map = None
        self.topspeed = 120.
        self.scalefac = 255. / self.topspeed # 200 kmh mapped to colors
        self.zoom = 6

    def get_angle(self, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        rads = atan2(-dy,dx)
        rads %= 2*pi
        degs = degrees(rads)
        return degs

    def cut_map(self, img):
        '''
        cannot plot without borders,
        currently the border is transparent, so we compute max/min of non-alpha-values
        and return the image without borders
        '''
        ul_y = np.min(np.where(img[:,:,3] > 0)[0]) 
        lr_y = np.max(np.where(img[:,:,3] > 0)[0]) 
        ul_x = np.min(np.where(img[:,:,3] > 0)[1]) 
        lr_x = np.max(np.where(img[:,:,3] > 0)[1]) 

        img_new = img[ul_y:lr_y, ul_x:lr_x,:]
        return img_new


    # ts is just cnt of the array
    def plot_map(self, ts, speed, outfile):
        if self.initial_coords:
            # for whole sequences
            if True:
                lat_min = np.min(self.coordinates[:,0]) - 0.0001
                lat_max = np.max(self.coordinates[:,0]) + 0.0001

                lon_min = np.min(self.coordinates[:,1]) - 0.0001 
                lon_max = np.max(self.coordinates[:,1]) + 0.0001
            else:
                # for area around current position
                ll_lon = self.coordinates[ts,1] - 0.001
                ll_lat = self.coordinates[ts,0] - 0.001
                ur_lon = self.coordinates[ts,1] + 0.001
                ur_lat = self.coordinates[ts,0] + 0.001
            
            # get map
            try:
                mapfilename = "%f_%f_%f_%f_%d.p" % (lat_min, lon_min, lat_max, lon_max, self.zoom)

                if os.path.isfile(mapfilename):
                    print "Loading with pickle"
                    self.map = pickle.load( open(mapfilename, "rb" ) ) 
                else:
                    print "Getting map from OSM"
                    self.map = smopy.Map((lat_min, lon_min, lat_max, lon_max), z=self.zoom)
                    pickle.dump(self.map, open(mapfilename , "wb" ) )

                #self.fig_map, ax = plt.subplots(ncols=1, nrows=1, frameon=False, figsize=(20,20))

                self.fig_map = plt.figure(figsize=(10,10), frameon=False)
                ax = plt.Axes(self.fig_map, [0., 0., 1., 1.])
                ax.set_axis_off()
                self.fig_map.add_axes(ax)

                self.ax = self.map.show_mpl(ax=ax, figsize=(10,10))
                
                for i in range(0,self.coordinates.shape[0]):
                    coords = self.map.to_pixels(self.coordinates[i,0], self.coordinates[i,1])
                    self.ax.plot(coords[0], coords[1], 'bo', ms=10, markeredgecolor='b')

                cc = self.map.to_pixels(self.coordinates[ts,0], self.coordinates[ts,1])
                self.current_coord = self.ax.plot(cc[0], cc[1], 'ro', ms=12)

                # only if we do not refresh the map
                self.initial_coords = False
            except Exception,e:
                print "Exception in plot_map: ", e
        else:
            try:
                g = min(1., self.scalefac * speed / 255.)
                r = max(0., 1. - g)
                b = 0.
               
                cx = self.map.to_pixels(self.coordinates[ts,0], self.coordinates[ts,1])[0]
                cy = self.map.to_pixels(self.coordinates[ts,0], self.coordinates[ts,1])[1]

                self.current_coord[0].set_xdata(cx)
                self.current_coord[0].set_ydata(cy)
                self.current_coord[0].set_color([r,g,b])
            except Exception, e:
                print e

        cv2.imwrite(outfile, self.cut_map(fig2data(self.fig_map)))

        #self.fig_map.savefig(outfile, transparent=True, dpi=80)
        #self.fig_map.savefig(outfile, dpi=200)
        #self.fig_map.canvas.print_png(outfile)
        #return fig2data(self.fig_map)


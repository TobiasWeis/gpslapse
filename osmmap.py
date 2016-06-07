import smopy
import numpy as np
from utils import *

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

                ax.plot(x,y,'go', ms=10, mew=0)

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


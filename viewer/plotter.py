import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from smopy import smopy

from utils import *

from mpl_toolkits.basemap import Basemap

class Plotter():
    def __init__(self):
        self.values = np.empty((0,2), np.float64)
        self.imu_values = np.empty((0,9), np.float64)
        self.coordinates = np.empty((0,2), np.float64)

        self.fig, self.axes = plt.subplots(nrows=10)
        self.fig2, self.axes2 = plt.subplots(nrows=1)
        self.initial = True
        self.initial_coords = True
        self.labels = ['yaw', 'pitch', 'roll', 'accx', 'accy', 'accz', 'avelx', 'avely', 'avelz', 'speed']
        self.map = None

    def plot(self, ts):
        if self.initial:
            self.lines = [ax.plot(self.imu_values[:,i]) for ax,i in zip(self.axes, range(0,9))]
            self.lines.append(self.axes[9].plot(self.values[:,0]))
            self.lines.append(self.axes[9].plot(self.values[:,1]))
            for i in range(0,len(self.axes)):
                self.axes[i].set_title(self.labels[i])
            self.axvlines = [self.axes[i].axvline(ts, color='k') for i in range(0,10)]
            self.initial = False

        for i in range(0,len(self.axes)):
            self.axvlines[i].set_xdata(ts)

        #plt.draw()
        #self.fig.canvas.draw()
        self.ret = fig2data(self.fig)

        return self.ret

    def plot_map(self, ts):
        if self.initial_coords:

            # for whole sequences
            if True:
                ll_lon = min(self.coordinates[:,1]) - 0.0001 
                ll_lat = min(self.coordinates[:,0]) - 0.0001

                ur_lon = max(self.coordinates[:,1]) + 0.0001
                ur_lat = max(self.coordinates[:,0]) + 0.0001
            else:
                # for area around current position
                ll_lon = self.coordinates[ts,1] - 0.001
                ll_lat = self.coordinates[ts,0] - 0.001
                ur_lon = self.coordinates[ts,1] + 0.001
                ur_lat = self.coordinates[ts,0] + 0.001
            
            # get map
            try:
                print "Getting map"
                self.map = smopy.Map((ll_lat, ll_lon, ur_lat, ur_lon), z=13)
                x,y = self.map.to_pixels(self.coordinates[:,0], self.coordinates[:,1])

                self.fig_map, ax = plt.subplots(ncols=1, nrows=1)
                ax = self.map.show_mpl(ax=ax)
                ax.plot(x,y,'go', ms=2, mew=0)

                cc = self.map.to_pixels(self.coordinates[ts,0], self.coordinates[ts,1])
                self.current_coord = ax.plot(cc[0], cc[1], 'ro', ms=5)

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


    def plot_coords(self, ts):

        if self.initial_coords:
            #self.axes2.plot(self.coordinates[:,0], self.coordinates[:,1], 'k.')
            #self.current_coord = self.axes2.plot(self.coordinates[ts,0], self.coordinates[ts,1], 'b.')

            ll_lon = min(self.coordinates[:,1]) - 0.01 
            ll_lat = min(self.coordinates[:,0]) - 0.01

            ur_lon = max(self.coordinates[:,1]) + 0.01
            ur_lat = max(self.coordinates[:,0]) + 0.01


            self.m = Basemap(llcrnrlon=ll_lon, llcrnrlat=ll_lat, urcrnrlon=ur_lon, urcrnrlat=ur_lat,\
                resolution='h',projection='merc', ax=self.axes2)


            x, y = self.m(self.coordinates[:,1], self.coordinates[:,0])
            self.m.drawmapboundary(fill_color='black')
            self.m.fillcontinents(color='white',lake_color='black', zorder=0)
            self.m.drawcoastlines()
            self.m.drawcountries()

            #m.drawrivers()
            self.m.plot(x,y, 'k.')
            self.current_coord = self.m.plot(self.m(self.coordinates[ts,1], self.coordinates[ts,0]), 'bo')
            self.initial_coords = False
        else:
            self.current_coord[0].set_xdata(self.m(self.coordinates[ts,1], self.coordinates[ts,0])[0])
            self.current_coord[0].set_ydata(self.m(self.coordinates[ts,1], self.coordinates[ts,0])[1])

        tmp = fig2data(self.fig2)
        return tmp


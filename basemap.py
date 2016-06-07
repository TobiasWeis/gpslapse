from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import matplotlib.image as image
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import numpy as np
from PIL import Image
from math import atan2, degrees, pi

class BaseMap():
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


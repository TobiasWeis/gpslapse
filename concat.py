#!/usr/bin/python
import numpy as np 
import cv2
import glob

outdir = "/data/tmp_files/"

files = glob.glob(outdir + "/img_*.png")
files.sort()

for cnt, f in enumerate(files):
    img = cv2.resize(cv2.imread(f), (640*2, 480*2))
    # add alpha-channel
    img = cv2.merge((img[:,:,0], img[:,:,1], img[:,:,2], np.zeros_like(img[:,:,1]) + 255))

    #num = f[:-4][16:]
    num = f[:-4][-8:]
    print "num: ", num
    map_fname = outdir + "/map_image_"+num+".png"
    print map_fname
    gauge_fname = outdir + "/gauge_"+num+".png"
    print gauge_fname
    
    # map image is 800x1600 ( for now ), need to rescale !
    # 1600 needs to fit in 480*2
    # 480 * 2 = 960

    mw = 400
    mh = 200
    map = cv2.resize(cv2.imread(map_fname), (mw, mh))

    gauge = cv2.resize(cv2.imread(gauge_fname, -1), (520,400))
    gauge = gauge[70:-90,:,:]

    roi = img[480*2 - (mh - 20) : 480*2 - 20, 640*2 - (mw-20) : 640*2 - 20 , 0:3] 

    #img[480*2 - (800 - 20) : 480*2 - 20, 640*2 - (400-20) : 640*2 - 20 ] = map[20:-20, 20:-20]

    dst = np.zeros_like(img)
    dst = cv2.addWeighted( roi, .5, map[20:-20, 20:-20], .5, 0.0, dst);
    img[480*2 - (mh - 20) : 480*2 - 20, 640*2 - (mw-20) : 640*2 - 20, 0:3] = dst

    gauge_left = (img.shape[1] - gauge.shape[1]) / 2
    gauge_top = (img.shape[0] - gauge.shape[0])

    roi = img[gauge_top:gauge_top+gauge.shape[0], gauge_left:gauge_left+gauge.shape[1]]
    dst = roi
    dst[gauge[:,:,3] >0] = cv2.addWeighted( roi[gauge[:,:,3] > 0], .5, gauge[gauge[:,:,3] > 0], .5, 0.0, dst);
    roi[gauge[:,:,3] > 0] = dst[gauge[:,:,3] > 0]

    img[gauge_top:gauge_top+gauge.shape[0], gauge_left:gauge_left+gauge.shape[1]] = roi

    cv2.imshow("img", img)
    cv2.imwrite(outdir + "/conc_%08d.png" % cnt, img)

    cv2.waitKey(10)

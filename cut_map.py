#!/usr/bin/python
import glob
import cv2

maps = glob.glob("/data/tmp_files/map*.png")
maps.sort()

ul = [150,150] 
lr = [513,332]

for m in maps:
    #load
    img = cv2.imread(m)
    #crop
    crop = img[150:332, 150:513]
    #save
    cv2.imwrite(m, crop)


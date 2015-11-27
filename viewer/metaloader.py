import context
import os
import glob
import datetime
import numpy as np
from math import *
from xml2dict import *
import time

import ntpath

from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtGui import *

import sys
sys.path.append("../")
from common import DBInterface

class Metaloader(object):
    '''
    superclass, defines functions and properties to be implemented,
    for XML or SQL loader ( SQL not yet implemented )

    meta informations:
    -- sequences:
    -- frames:
            meta["ts"]          timestamp
            meta["time"]        human readable time string
            meta["uri"]         uri of image file

            meta["accx"]        accelerometer values
            meta["accy"]    
            meta["accz"] 

            meta["avelx"]       gyroscope values ( angular velocity )
            meta["avely"]
            meta["avelz"]

            meta["yaw"]         yaw 
            meta["pitch"]       pitch
            meta["roll"]        roll 

            meta["lat"]         gps latitude
            meta["lon"]         gps longitude
            meta["speed"]       gps speed in km/h

            meta["speedlimit"]  if known, speedlimit at that coordinate
    '''
    def __init__(self, sequenceFolder=None, startframe=0, parse=False):
        self.seqFolder = sequenceFolder
        self.startframe = startframe

        self.parse = parse

        self.seqSTime = 0
        self.seqETime = 0
        self.seqLength = 0

        # these arrays will hold the values for the whole sequence, needed to speed up plotting
        self.coordinates = np.empty((0,2), np.float64)
        self.speedinfo = np.empty((0,2), np.float64)
        self.imu_values = np.empty((0,9), np.float64)
        self.context = context.Context()

        self.framesMeta = []

        #self.parseSequenceMeta()
        #self.parseFrameMeta()


    def parseSequenceMeta(self):
        pass

    def parseFrameMeta(self):
        pass

    def getSequenceMeta(self):
        pass

    def getTurnrate(self, trmin, trmax):
        matching_files = []
        for i,f in enumerate(self.framesMeta):
            if f["avelz"] > trmin and f["avelz"] < trmax:
                matching_files.append([self.framesMeta[i-1]["uri"], f["uri"]])
        return matching_files

    def getTurnrateWithSpeed(self, trmin, trmax, smin, smax):
        matching_files = []
        for i,f in enumerate(self.framesMeta):
            if f["avelz"] > trmin and f["avelz"] < trmax and f["speed"] > smin and f["speed"] < smax:
                matching_files.append([self.framesMeta[i-1]["uri"], f["uri"]])
        return matching_files


    def getFrameMeta(self, cnt):
        meta = self.framesMeta[cnt]
        ret_str = ""

        ret_str += "\nFilename: %s" % meta["uri"]
        ret_str += "\nTime: %s " % meta["time"]
        ret_str += "\n"
        ret_str += "\nSpeed: %d" % meta["speed"]
        try:
            ret_str += "\nSpeedLimit: %d" % meta["speedlimit"]
            ret_str += "\nLanes: %d" % meta["nlanes"]
            ret_str += "\nType: %s" % meta["highwaytype"]
            ret_str += "\nName: %s" % meta["name"]
            ret_str += "\nOneway: %d" % meta["oneway"]
        except:
            pass
        ret_str += "\n"
        ret_str += "%f, %f" % (meta["lat"], meta["lon"])
        # FIXME: not present in XML yet, but already implemented in grabber
        #ret_str += "\nResolution: %d,%d" % (r.root.imgwidth, r.root.imgheight)

        # load the xml file accoring to the current filename

        return None, ret_str

class MetaloaderSQLite(Metaloader):
    def __init__(self,  forceparse = False):
        super(MetaloaderSQLite, self).__init__()
        self.forceparse = forceparse

        self.dbi = DBInterface.DBInterface()
        self.annotCars = []

    def getAllSequences(self):
        return self.dbi.get_all_sequences()

    def clear(self):
        self.coordinates = np.empty((0,2), np.float64)
        self.speedinfo = np.empty((0,2), np.float64)
        self.imu_values = np.empty((0,9), np.float64)
        self.context = context.Context()

        self.framesMeta = []
        self.annotCars = []

    def parseSequenceMeta(self, id_sequence, progressDialog = True, annotations = True):
        # get sequence details
        self.sequence = self.dbi.get_sequence_meta(id_sequence)
        self.frames = self.dbi.get_frames(id_sequence = id_sequence)

        # open progress dialog
        if progressDialog:
            progress = QtGui.QProgressDialog("Reading sequence files...", "Cancel", 0, len(self.frames))
            progress.setWindowModality(QtCore.Qt.WindowModal)
            progress.show()

        cnt = 0
        for f in self.frames:
            frame_id = self.dbi.get_frame_id_from_uri(ntpath.basename(f.img_uri))

            if annotations:
                self.annotcars = self.dbi.get_annot_cars(frame_id)

                annots = []
                for a in self.annotcars:
                    annots.append(a)
                self.annotCars.append(annots)

            cnt += 1
            if progressDialog:
                progress.setValue(cnt)
            meta = {}

            # get timestamp of cam
            ts = f.ts_cam
            mytime = datetime.datetime.fromtimestamp(long(f.ts_cam)/1000.).strftime('%Y-%m-%d %H:%M:%S')

            meta["img_w"] = f.img_w
            meta["img_h"] = f.img_h

            meta["ts"] = f.ts_cam
            meta["time"] = mytime
            meta["uri"] = f.img_uri

            # get accelerometer data
            meta["accx"] = f.accx
            meta["accy"] = f.accy
            meta["accz"] = f.accz

            meta["avelx"] = f.avelx
            meta["avely"] = f.avely
            meta["avelz"] = f.avelz

            try:
                meta["yaw"] = f.yaw
                meta["pitch"] = f.pitch
                meta["roll"] = f.roll
            except:
                meta["yaw"] = 0.
                meta["pitch"] = 0.
                meta["roll"] = 0.


            self.imu_values = np.append(self.imu_values, np.array([[meta["yaw"], meta["pitch"], meta["roll"], meta["accx"],meta["accy"],meta["accz"],meta["avelx"], meta["avely"], meta["avelz"]]]), axis=0)

            # get GPS
            meta["lat"] = f.lat
            meta["lon"] = f.lon

            # FIXME: parse context if not available
            if (f.ts_context is None and self.parse) or self.forceparse:
                cstr, cdict = self.context.getStreetContext(meta["lat"], meta["lon"])

                f.ts_context = int(round(time.time() * 1000)) # FIXME TOBI !

                # update database record
                print "Adding context-information:"
                for k,v in cdict.iteritems():
                    print k, ":", v
                    if k == "highwaytype":
                        f.context_highwaytype = unicode(v)
                    if k == "nlanes":
                        f.context_nlanes = int(v)
                    if k == "name":
                        f.context_streetname = unicode(v)
                    if k == "speedlimit":
                        f.context_speedlimit = int(v)
                    if k == "oneway":
                        f.context_oneway = int(v)

                self.dbi.update_frame(f)

            meta["speedlimit"] = f.context_speedlimit 
            meta["nlanes"] = f.context_nlanes
            meta["highwaytype"] = f.context_highwaytype
            meta["name"] = f.context_streetname
            meta["oneway"] = f.context_oneway

             # get speedinfo
            try:
                speed = float(f.speed)*60*60/1000.
                meta["speed"] = speed
            except:
                print "Problem with speed"
                meta["speed"] = 0.

            self.coordinates = np.append(self.coordinates, np.array([[meta["lat"], meta["lon"]]]), axis=0)
            self.speedinfo = np.append(self.speedinfo, np.array([[meta["speed"], meta["speedlimit"]]]), axis=0)
           
            self.framesMeta.append(meta)
        
        if progressDialog:
            progress.close()

        return self.sequence.folder, self.frames


class MetaloaderXML(Metaloader):
    def __init__(self, sequenceFolder, startframe, forcereparse = False):
        self.forcereparse = forcereparse
        super(MetaloaderXML, self).__init__(sequenceFolder=sequenceFolder, startframe=startframe)
        print "FORCING REPARSE OF CONTEXT"
        print "Getting Meta for ", self.seqFolder

    def parseSequenceMeta(self):
        self.xmlfiles = [os.path.basename(x) for x in glob.glob(self.seqFolder + '/*.xml')] 
        self.xmlfiles.sort()
        self.xmlfiles = self.xmlfiles[self.startframe:]

        # open progress dialog
        progress = QtGui.QProgressDialog("Reading sequence files...", "Cancel", 0, len(self.xmlfiles))
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.show()

        cnt = 0
        for f in self.xmlfiles:
            progress.setValue(cnt)
            cnt += 1
            meta = {}

            s = open(self.seqFolder + f, 'r')
            xml = XML2Dict()
            r = xml.fromstring(s.read())

            # get timestamp of cam
            ts = r.root.ts_cam.value
            mytime = datetime.datetime.fromtimestamp(long(r.root.ts_cam.value)/1000.).strftime('%Y-%m-%d %H:%M:%S')

            meta["ts"] = r.root.ts_cam.value
            meta["time"] = mytime
            meta["uri"] = r.root.uri.value

            # get accelerometer data
            accels = []
            try:
                for i in r.root.acceleration.item:
                    accels.append(float(i.value))
                meta["accx"] = accels[0]
                meta["accy"] = accels[1]
                meta["accz"] = accels[2]
            except:
                meta["accx"] = 0
                meta["accy"] = 0
                meta["accz"] = 0

            avels = []
            try:
                for i in r.root.avel.item:
                    avels.append(float(i.value))
                meta["avelx"] = avels[0]
                meta["avely"] = avels[1]
                meta["avelz"] = avels[2]
            except:
                meta["avelx"] = 0
                meta["avely"] = 0
                meta["avelz"] = 0

            # get preprocessed quaternion
            quaternion = []
            for i in r.root.quaternion.item:
                quaternion.append(float(i.value))

            x = quaternion[0]
            y = quaternion[1]
            z = quaternion[2]
            w = quaternion[3]

            meta["yaw"] = degrees(atan2(2*x*y + 2*w*z, w*w + x*x - y*y - z*z))
            meta["pitch"] = degrees(-asin(2*w*y - 2*x*z))
            meta["roll"]  = degrees(-atan2(2*y*z + 2*w*x, -w*w + x*x + y*y - z*z))

            self.imu_values = np.append(self.imu_values, np.array([[meta["yaw"], meta["pitch"], meta["roll"], meta["accx"],meta["accy"],meta["accz"],meta["avelx"], meta["avely"], meta["avelz"]]]), axis=0)

            # get GPS
            lat = float(r.root.latitude.value)
            lon = float(r.root.longitude.value)
            meta["lat"] = lat
            meta["lon"] = lon

            # check context, if not there, try to download
            speedlimit = 0
            lanes = 0
            oneway = False
            highway = ""
            name = ""

            if "context" in r.root and not self.forcereparse:
                if len(r.root.context) > 0:
                    if "speedlimit" in r.root.context:
                        speedlimit = int(r.root.context.speedlimit.value)
                    if "nlanes" in r.root.context:
                        lanes = int(r.root.context.nlanes.value)
                    if "name" in r.root.context:
                        name = r.root.context.name.value
                    if "oneway" in r.root.context:
                        oneway = bool(r.root.context.oneway.value)
                    if "highwaytype" in r.root.context:
                        highway = r.root.context.highwaytype.value
                    #for k,v in r.root.context.iteritems():
                    #    print "k: ", k
                    #    print "v: ", v.value
            else:
                cstr, cdict = self.context.getStreetContext(lat, lon)
                self.updateXML(self.seqFolder + f, cdict)
            
            meta["speedlimit"] = speedlimit
            meta["nlanes"] = lanes
            meta["highwaytype"] = highway
            meta["name"] = name
            meta["oneway"] = oneway

             # get speedinfo
            speed = float(r.root.speed.value)*60*60/1000.
            meta["speed"] = speed


            self.coordinates = np.append(self.coordinates, np.array([[lat, lon]]), axis=0)
            self.speedinfo = np.append(self.speedinfo, np.array([[speed, speedlimit]]), axis=0)
           
            self.framesMeta.append(meta)

        progress.close()

    def updateXML(self, fname, cdict):
        import xml.etree.ElementTree as xml
        import lxml.etree as etree

        tree = xml.parse(fname)
        xmlRoot = tree.getroot()
        
        contexts = xmlRoot.findall("context")

        if len(contexts) >= 1: # FIXME: handle this error !
            print "More than 1 context-fields, removing all"
            for c in contexts:
                xmlRoot.remove(c)


        contexts = xmlRoot.findall("context")

        if len(contexts) == 1: #append to context
            print "Appending new elements"
            for k,v in cdict.iteritems():
                print k, ":", v
                if contexts[0].find(k) is None:
                    print "Append: ",k, " with value: ", v
                    tmp = xml.Element(k, type=type(v).__name__)
                    tmp.text = unicode(v)
                    contexts.append(tmp)
                else:
                    print k, " was already in context"
        else: 
            print "Creating new context for this file"
            child = xml.Element("context")
            for k,v in cdict.iteritems():
                print "Append: ",k, " with value: ", v
                tmp = xml.Element(k, type=type(v).__name__)
                tmp.text = unicode(v)
                child.append(tmp)
            xmlRoot.append(child)
            #tree.write("/tmp/test.xml")

        tree.write(fname)

        print "Updated XML with context: ", fname







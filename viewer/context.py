# -*- coding: utf-8 -*-
'''
context.py
use osm api to grab context for certain coordinates,
like number of lanes, type of road, etc.
'''
import overpass
import pprint
import time

class Context():
    def __init__(self):
        self.api = overpass.API()

        self.last_lat = -1
        self.last_lon = -1
        self.last_res = None

        #self.api = overpass.API(endpoint="http://overpass.osm.rambler.ru/cgi/interpreter")

    def get(self, lat, lon):
        res = self.api.Get('way["highway"~"primary|secondary|tertiary|trunk|motorway"](around:10,%f,%f)' % (lat, lon))
        return res

    def getStreetContext(self, lat,lon):
        res = None
        while res == None:
            try:
                # only query server if coordinate has changed !
                if self.last_lat != lat and self.last_lon != lon:
                    res = self.get(lat,lon)
                    self.last_res = res
                    self.last_lat = lat
                    self.last_lon = lon
                else:
                    print "Same coord"
                    res = self.last_res
            except overpass.errors.MultipleRequestsError:
                print "Multi-Request-Error, waiting a bit..."
                time.sleep(5)

        print "---- Context for ", lat, " , ", lon
        #pprint.pprint(res)
        print "------------- : "

        mydict = {}

        res_str = ""

        try:
            num_lanes = int(res["elements"][0]["tags"]["lanes"])
            print "# Lanes: %d" % num_lanes 
            res_str += "\n# Lanes: %d" % num_lanes
            mydict["nlanes"] = int(num_lanes)
        except:
            print "No lane information"
            pass

        try:
            name = res["elements"][0]["tags"]["name"]
            print "Name: ", name
            mydict["name"] = name
        except Exception, e:
            print "No street name, ", e

        try:
            oneway = res["elements"][0]["tags"]["oneway"]
            print "Oneway: ", oneway
            mydict["oneway"] = bool(oneway)
        except:
            print "No oneway info"

        try:
            speed_l = int(res["elements"][0]["tags"]["maxspeed"])
            print "Speed-L: %d " % speed_l 
            res_str += "\nSpeedLimit: %d" % speed_l
            mydict["speedlimit"] = speed_l
        except:
            print "No speed limit information"

        try:
            stype = res["elements"][0]["tags"]["highway"]
            print "Type is: %s" % stype
            res_str += "\nType: %s" % stype
            mydict["highwaytype"] = stype
        except:
            print "No type information"

        print "--------------"


        #print "Returning:"
        #print res_str
        #print "Type of res_str: ", type(res_str)

        if len(res_str) == 0:
            res_str = "No context info available"

        return res_str, mydict


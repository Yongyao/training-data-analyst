#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 16 21:07:15 2018

@author: yjiang
"""
import datetime
import csv

class SceneInfo:
   def __init__ (self, line):
      try:
        self.SCENE_ID, self.SPACECRAFT_ID, self.SENSOR_ID, self.DATE_ACQUIRED, self.COLLECTION_NUMBER, self.COLLECTION_CATEGORY,self.DATA_TYPE, self.WRS_PATH, self.WRS_ROW, self.CLOUD_COVER, self.NORTH_LAT, self.SOUTH_LAT, self.WEST_LON, self.EAST_LON, self.TOTAL_SIZE, self.BASE_URL = line.split(',')

        self.DATE_ACQUIRED = datetime.datetime.strptime(self.DATE_ACQUIRED, '%Y-%m-%d')
        self.NORTH_LAT = float(self.NORTH_LAT)
        self.SOUTH_LAT = float(self.SOUTH_LAT)
        self.WEST_LON = float(self.WEST_LON)
        self.EAST_LON = float(self.EAST_LON)
        self.CLOUD_COVER = float(self.CLOUD_COVER)
      except:
        print "WARNING! format error on {", line, "}"        

   def contains(self, lat, lon):
      return (lat > self.SOUTH_LAT) and (lat < self.NORTH_LAT) and (lon > self.WEST_LON) and (lon < self.EAST_LON)

   def intersects(self, slat, wlon, nlat, elon):
      return (nlat > self.SOUTH_LAT) and (slat < self.NORTH_LAT) and (elon > self.WEST_LON) and (wlon < self.EAST_LON)

   def month_path_row(self):
      return '{}-{}-{}'.format(self.yrmon(), self.WRS_PATH, self.WRS_ROW)

   def yrmon(self):
      return '{}-{:02d}'.format(self.DATE_ACQUIRED.year, self.DATE_ACQUIRED.month)
  
   def printInfo(self):
      print self.NORTH_LAT, self.SOUTH_LAT, self.WEST_LON, self.EAST_LON 

def filterByLocation(scene, lat, lon):
   if scene.contains(lat, lon):
      yield scene

def filterByArea(scene, slat, wlon, nlat, elon):
   if scene.intersects(slat, wlon, nlat, elon):
      yield scene

def clearest(scenes):
   if scenes:
      return min(scenes, key=lambda s: s.CLOUD_COVER)
   else:
      return None

# self.NORTH_LAT, self.SOUTH_LAT, self.WEST_LON, self.EAST_LON  
lines = [line.rstrip('\n') for line in open('/Users/yjiang/Documents/pythonWorkspace/treemap/Data/2015index.txt')]
scenes = []
lat =-2.05; lon = 110.52     # center of Reunion Island
dlat = 5; dlon = 5
for line in lines:
    scene = SceneInfo(line)
    # if scene.intersects(lat+dlat,lon-dlon,lat-dlat,lon+dlon):
    if scene.intersects(lat-dlat,lon-dlon,lat+dlat,lon+dlon):
        scenes.append(scene)
        # scene.printInfo()

print len(scenes)

# tlat = 5; tlon = 5
# print scenes[0].intersects(lat-tlat,lon-tlon,lat+tlat,lon+tlon)
# -20.61508 -22.72789 54.6966 56.92609



    

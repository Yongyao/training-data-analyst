#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import os.path
import subprocess
import tempfile
from rasterstats import zonal_stats

class RasterCopy():
   def __init__(self, gsfile, destdir):
      self.gsfile = gsfile
      self.dest = os.path.join(destdir, os.path.basename(self.gsfile))

   def __enter__(self):
      print 'Getting {0} to {1} '.format(self.gsfile, self.dest)
      ret = subprocess.check_call(['gsutil', 'cp', self.gsfile, self.dest])
      if ret == 0:
         return self.dest
      else:
         return None

   def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
      os.remove( self.dest ) # cleanup
      
class VecCopy():
   def __init__(self, gsfile, destdir):
      self.gsfile = gsfile
      self.dest = os.path.join(destdir, os.path.basename(self.gsfile))
      self.prefix_list = ['.dbf', '.prj', '.qpj', '.shp', '.shx' ]

   def __enter__(self):
      print 'Getting {0} to {1} '.format(self.gsfile, self.dest)
      for prefix in self.prefix_list:
          ret = subprocess.check_call(['gsutil', 'cp', self.gsfile+prefix, self.dest+prefix])  
      if ret == 0:
         return self.dest + '.shp'
      else:
         return None

   def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
      for prefix in self.prefix_list: 
          os.remove( self.dest + prefix) # cleanup     

def calZonal(shp_path, raster_path, output_folder): 
    with RasterCopy(raster_path, '.') as raster, \
     VecCopy(shp_path, '.') as vec :
         
         tmpfilename = os.path.join(tempfile.gettempdir(), '{0}_zonal.txt'.format(os.path.basename(raster_path)))
         f = open(tmpfilename,'w')

         stats = zonal_stats(vec, raster, stats="mean")
         for stat in stats:
             f.write(stat['mean'])
         f.close()
         
         outfilename = os.path.join(output_folder, '{0}_zonal.txt'.format(os.path.basename(raster_path)) )
         ret = subprocess.check_call(['gsutil', 'mv', tmpfilename, outfilename])
         print 'Wrote {0} ...'.format(outfilename)
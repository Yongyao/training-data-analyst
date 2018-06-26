#!/usr/bin/env python

"""
Copyright Google Inc. 2016
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import sys
# import osgeo.gdal as gdal
from osgeo import gdal, gdal_array
import os
import os.path
import subprocess
import struct
import numpy as np
import tempfile
from sklearn.externals import joblib

class LandsatReader():
   def __init__(self, gsdir, band, destdir):
      basename = os.path.basename(gsdir)
      self.gsfile = '{0}/{1}_{2}.TIF'.format(gsdir, basename, band)
      self.dest = os.path.join(destdir, os.path.basename(self.gsfile))

   def __enter__(self):
      print 'Getting {0} to {1} '.format(self.gsfile, self.dest)
      ret = subprocess.check_call(['gsutil', 'cp', self.gsfile, self.dest])
      if ret == 0:
         dataset = gdal.Open( self.dest, gdal.GA_ReadOnly )
         return dataset
      else:
         return None

   def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
      os.remove( self.dest ) # cleanup

class ModelReader():
   def __init__(self, gsfile, destdir):
      basename = os.path.basename(gsfile)
      self.gsfile = gsfile
      self.dest = os.path.join(destdir, os.path.basename(self.gsfile))

   def __enter__(self):
      print 'Getting {0} to {1} '.format(self.gsfile, self.dest)
      ret = subprocess.check_call(['gsutil', 'cp', self.gsfile, self.dest])
      if ret == 0:
         model = joblib.load(self.dest)
         return model
      else:
         return None

   def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
      os.remove(self.dest ) # cleanup

def array_to_raster(array, output_path, ref_ds):    
    Output = gdal.GetDriverByName('GTiff').Create(output_path, ref_ds.RasterXSize, ref_ds.RasterYSize, 1, gdal.GDT_Float32, options=['COMPRESS=DEFLATE'])
    Output.SetProjection(ref_ds.GetProjectionRef())
    Output.SetGeoTransform(ref_ds.GetGeoTransform()) 
    Output.GetRasterBand(1).WriteArray(array)
    Output.FlushCache()  # Write to disk.

def computeNdvi(gs_baseurl, outdir, instrument, model_url):
  if instrument is 'LANDSAT_7':
     band1 = 'B1'
     band2 = 'B2'
     band3 = 'B3'
     band4 = 'B4'
  else:
     band1 = 'B2'
     band2 = 'B3'
     band3 = 'B4'
     band4 = 'B5'

  with LandsatReader(gs_baseurl, band1, '.') as green_ds, \
     LandsatReader(gs_baseurl, band2, '.') as blue_ds, \
     LandsatReader(gs_baseurl, band3, '.') as red_ds, \
     LandsatReader(gs_baseurl, band4, '.') as nir_ds, \
     ModelReader(model_url, '.') as model:

     # define output
     tmpfilename = os.path.join(tempfile.gettempdir(), '{0}_clf.TIF'.format(os.path.basename(gs_baseurl)) )
     
     # define input
     green = green_ds.GetRasterBand(1).ReadAsArray()
     blue = blue_ds.GetRasterBand(1).ReadAsArray()
     red = red_ds.GetRasterBand(1).ReadAsArray()
     nir = nir_ds.GetRasterBand(1).ReadAsArray()
     img = np.zeros((nir_ds.RasterYSize, nir_ds.RasterXSize, 4), gdal_array.GDALTypeCodeToNumericTypeCode(red_ds.GetRasterBand(1).DataType))
     img[:, :, 0] = green
     img[:, :, 1] = blue
     img[:, :, 2] = red
     img[:, :, 3] = nir

     # pairing X and y
     rows = img.shape[0]
     cols = img.shape[1]
     band_num = img.shape[2]

     # create mask image
     mask_landsat = np.zeros((rows, cols))
     mask_landsat[~np.isnan(img[:, :, 1])] = 1
     mask = mask_landsat

     # handle missing value
     img[np.isnan(img)] = 0

     predict = model.predict(img.reshape(cols*rows, band_num))
     output = predict.reshape(rows, cols)*mask

     array_to_raster(output, tmpfilename, nir_ds)

     outfilename = os.path.join(outdir, '{0}_clf.TIF'.format(os.path.basename(gs_baseurl)) )
     ret = subprocess.check_call(['gsutil', 'mv', tmpfilename, outfilename])
     print 'Wrote {0} ...'.format(outfilename)

if __name__ == '__main__':
   computeNdvi('gs://gcp-public-data-landsat/LE07/PRE/198/057/LE71980572015351ASN00', 'gs://cloud-training-demos/landsat/', 'LANDSAT_7') # cape palmas
   computeNdvi('gs://gcp-public-data-landsat/LC08/PRE/153/075/LC81530752015348LGN00', 'gs://cloud-training-demos/landsat/', 'LANDSAT_8') # reunion

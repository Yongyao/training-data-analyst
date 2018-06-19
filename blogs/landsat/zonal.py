#!/usr/bin/env python

import apache_beam as beam
import argparse
from google.cloud import storage
# import subprocess

def list_blobs(bucket_name, input_folder):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blobs = bucket.list_blobs()
    filelist = []
    for blob in blobs:
        if(blob.name.startswith(input_folder) and blob.name.endswith('TIF')):
            filelist.append(blob.name)
    return filelist

def run():
   import os
   parser = argparse.ArgumentParser(description='Compute zonal NDVI')
   parser.add_argument('--input_folder', required=True, help='Which folder should the ndvi images be retreived?')
   parser.add_argument('--input_bucket', required=True, help='Which bucket should the ndvi images be retreived?')
   parser.add_argument('--output_file', default='output.txt', help='default=output.txt Supply a location on GCS when running on cloud')

   known_args, pipeline_args = parser.parse_known_args()
 
   p = beam.Pipeline(argv=pipeline_args)
   output_file = known_args.output_file
   input_folder = known_args.input_folder
   input_bucket = known_args.input_bucket
   
   scenes = list_blobs(input_bucket, input_folder)
   scenes = list_blobs('eostest', 'gs://eotest/landsat/output/2015-01/')
    
#==============================================================================
#    ret = subprocess.check_call(['gsutil', 'du', input_folder])
#    scenes = []
#    for f in ret:
#        scenes.append(f.split()[1])
#==============================================================================

   # Read the index file and find all scenes that cover this area
   allscenes = (p
      | 'get_scenes' >> beam.Create(scenes)
   )

   # write out info about scene
   allscenes | beam.Map(lambda (scene): '{}'.format(scene)) | 'scene_info' >> beam.io.WriteToText(output_file)


   p.run()

if __name__ == '__main__':
   run()

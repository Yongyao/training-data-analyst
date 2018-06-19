#!/usr/bin/env python

import apache_beam as beam
import argparse
from google.cloud import storage
import getZonal

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
   parser.add_argument('--input_vec', required=True, help='Which bucket should the vector be retreived?')
   parser.add_argument('--output_file', default='output.txt', help='default=output.txt Supply a location on GCS when running on cloud')
   parser.add_argument('--output_folder')

   known_args, pipeline_args = parser.parse_known_args()
 
   p = beam.Pipeline(argv=pipeline_args)
   output_file = known_args.output_file
   input_folder = known_args.input_folder
   input_bucket = known_args.input_bucket
   input_shp = known_args.input_vec
   output_folder = known_args.output_folder
   
   scenes = list_blobs(input_bucket, input_folder)    

   # Get all file names from the input folder
   allscenes = (p
      | 'get_scenes' >> beam.Create(scenes)
   )

   # write out info about scene
   allscenes | beam.Map(lambda (scene): '{}'.format(scene)) | 'scene_info' >> beam.io.WriteToText(output_file)

   # compute zonal ndvi
   allscenes | 'compute_zonal_stats' >> beam.Map(lambda (scene): getZonal.computeZonal('gs://'+ input_bucket + '/'+ input_shp, 'gs://'+ input_bucket + '/' + scene, output_folder))

   p.run()

if __name__ == '__main__':
   run()

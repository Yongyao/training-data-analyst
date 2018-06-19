#!/usr/bin/env python

import apache_beam as beam
import argparse
import subprocess

def run():
   import os
   parser = argparse.ArgumentParser(description='Compute zonal NDVI')
   parser.add_argument('--input_folder', required=True, help='Where should the ndvi images be stored? Supply a GCS location when running on cloud')
   parser.add_argument('--output_file', default='output.txt', help='default=output.txt Supply a location on GCS when running on cloud')

   known_args, pipeline_args = parser.parse_known_args()
 
   p = beam.Pipeline(argv=pipeline_args)
   output_file = known_args.output_file
   input_folder = known_args.input_folder
   
   ret = subprocess.check_call(['gsutil', 'du', input_folder])
   
   scenes = []
   for f in ret:
       scenes.append(f.split()[1])

   # Read the index file and find all scenes that cover this area
   allscenes = (p
      | 'get_scenes' >> beam.Create(scenes)
   )

   # write out info about scene
   allscenes | beam.Map(lambda (scene): '{}'.format(scene)) | 'scene_info' >> beam.io.WriteToText(output_file)


   p.run()

if __name__ == '__main__':
   run()

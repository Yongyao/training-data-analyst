#!/bin/bash

if [ "$#" -ne 2 ]; then
   echo "Usage:   ./run_oncloud.sh project-name  bucket-name"
   echo "Example: ./run_oncloud.sh cloud-training-demos  cloud-training-demos"
   exit
fi

PROJECT=$1
BUCKET=$2

gsutil -m rm -rf gs://$BUCKET/landsat-brazil/output

python ./dfndvi.py \
    --project=$PROJECT \
    --runner=DataflowRunner \
    --staging_location=gs://$BUCKET/landsat-brazil/staging \
    --temp_location=gs://$BUCKET/landsat-brazil/staging \
    --index_file=gs://mck-earth-observations/index/index_13_17.txt \
    --max_num_workers=20 \
    --autoscaling_algorithm=THROUGHPUT_BASED \
    --output_file=gs://$BUCKET/landsat-brazil/output/scenes.txt \
    --output_dir=gs://$BUCKET/landsat-brazil/output \
    --job_name=monthly-landsat \
    --save_main_session \
    --setup_file=./setup.py

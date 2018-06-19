#!/bin/bash

if [ "$#" -ne 2 ]; then
   echo "Usage:   ./run_oncloud.sh project-name  bucket-name"
   echo "Example: ./run_oncloud.sh cloud-training-demos  cloud-training-demos"
   exit
fi

PROJECT=$1
BUCKET=$2

gsutil -m rm -rf gs://$BUCKET/zonal/output

python ./zonal.py \
    --project=$PROJECT \
    --runner=DataflowRunner \
    --staging_location=gs://$BUCKET/zonal/staging \
    --temp_location=gs://$BUCKET/zonal/staging \
    --max_num_workers=10 \
    --autoscaling_algorithm=THROUGHPUT_BASED \
    --input_folder=gs://$BUCKET/landsat/output/2015-01/ \
    --input_bucket=$BUCKET \
    --output_file=gs://$BUCKET/zonal/output/scenes.txt \
    --job_name=zonal-ndvi \
    --save_main_session \
    --setup_file=./setup.py

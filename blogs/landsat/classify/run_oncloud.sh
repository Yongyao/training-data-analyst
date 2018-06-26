#!/bin/bash

if [ "$#" -ne 2 ]; then
   echo "Usage:   ./run_oncloud.sh project-name  bucket-name"
   echo "Example: ./run_oncloud.sh cloud-training-demos  cloud-training-demos"
   exit
fi

PROJECT=$1
BUCKET=$2

gsutil -m rm -rf gs://$BUCKET/landsat-clf/output

python ./dfndvi.py \
    --project=$PROJECT \
    --staging_location=gs://$BUCKET/landsat-clf/staging \
    --temp_location=gs://$BUCKET/landsat-clf/staging \
    --index_file=gs://$BUCKET/index/index_13_17_small.txt \
    --max_num_workers=20 \
    --autoscaling_algorithm=THROUGHPUT_BASED \
    --output_file=gs://$BUCKET/landsat-clf/output/scenes.txt \
    --output_dir=gs://$BUCKET/landsat-clf/output \
    --model_dir=gs://eotest-207015-mlengine/model.joblib \
    --job_name=monthly-landsat-clf \
    --save_main_session \
    --setup_file=./setup.py

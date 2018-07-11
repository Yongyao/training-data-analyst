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
    --input_folder=landsat-brazil/output/2013-01/ \
    --input_bucket=$BUCKET \
    --input_vec=shp-brazil/bra_saveas \
    --output_file=gs://$BUCKET/zonal/scenes.txt \
    --output_folder=gs://$BUCKET/zonal/output \
    --worker_machine_type=n1-highmem-16 \
    --job_name=zonal-ndvi \
    --save_main_session \
    --setup_file=./setup.py

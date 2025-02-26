#!/bin/bash
set -e

#
# DAB validate
#
cd ../kafka_dr_pipeline_dab
databricks bundle deploy --target default

#!/bin/bash
set -e

# This scripts generates a new DAB from an existing DLT pipeline created in Databricks UI
BUNDLE_NAME="sample_dab"
BUNDLE_DIR="../${BUNDLE_NAME}"

# Create a new directory for the DAB one level up if it does not already exist
if [ ! -d ${BUNDLE_DIR} ]; then
    echo -e "\nCreating directory for DAB..."
    mkdir ${BUNDLE_DIR}
else
    echo -e "\nWARN Directory for DAB already exists. Overwriting existing files..."
    rm -rf ${BUNDLE_DIR}/*
fi

cd ${BUNDLE_DIR}

# Create databricks.yml if it does not already exist
if [ ! -f databricks.yml ]; then
    echo -e "\nCreating databricks.yml..."
    cat <<EOL > "databricks.yml"
bundle:
  name: ${BUNDLE_NAME}

include:
  - resources/*.yml
EOL
fi

# Pipeline ID from the Delta Live Tables in Databricks UI
# Delta Live Tables > <pipeline name> > Settings > JSON > id
echo -e "\ndatabricks bundle generate..."
DLT_PIPELINE_ID="cd86ff3b-5a90-42d0-81d9-64e8522d7f1a"
databricks bundle generate pipeline --existing-pipeline-id ${DLT_PIPELINE_ID}

# get absolute path to ${BUNDLE_DIR}
BUNDLE_DIR_FULL=$(cd ${BUNDLE_DIR} && pwd)
echo -e "\nDAB generated successfully in folder ${BUNDLE_DIR_FULL}"
#!/bin/bash

export S3_BUCKET_URI=""
export CF_DISTRIBUTION_ID=""
export DEPLOY_FOLDER="./public/"

# Checks
[ -z "$S3_BUCKET_URI" ] && { echo "ERROR: S3_BUCKET_URI is NULL"; exit 10; } 
[ -z "$CF_DISTRIBUTION_ID" ] && echo "WARNING: CF_DISTRIBUTION_ID is NULL" || echo "INFO: CF distribution detected"

# Build
{
    hugo -D
} || { echo "ERROR: Build failed, check hugo configuration!"; exit 10; }

# Deploy
{
    aws s3 sync $DEPLOY_FOLDER $S3_BUCKET_URI
} || { echo "ERROR: Sync to S3 failed, check configuration"; exit 10; }

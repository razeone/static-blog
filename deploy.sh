#!/bin/bash

export S3_BUCKET_URI=""
export CF_DISTRIBUTION_ID=""
export DEPLOY_FOLDER="./public/"

# Check bucket
[ -z "$S3_BUCKET_URI" ] && { echo "ERROR: S3_BUCKET_URI is NULL"; exit 10; } 

# Build
{
    hugo -D
} || { echo "ERROR: Build failed, check hugo configuration!"; exit 10; }

# Deploy
{
    aws s3 sync $DEPLOY_FOLDER $S3_BUCKET_URI
} || { echo "ERROR: Sync to S3 failed, check configuration"; exit 10; }

# Invalidate cache
[ -z "$CF_DISTRIBUTION_ID" ] && echo "INFO: CF_DISTRIBUTION_ID is NULL, skipping." || { echo "INFO: CF distribution detected, creating invalidation..."; aws cloudfront create-invalidation --distribution-id $CF_DISTRIBUTION_ID --paths "/*"; }
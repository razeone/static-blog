#!/bin/bash

export S3_BUCKET_NAME="raze-website"
export CF_DISTRIBUTION_ID="ES52SN9381PAQ"
export DEPLOY_FOLDER="./public"

# Checks
[ -z "$S3_BUCKET_NAME" ] && { echo "ERROR: S3_BUCKET_NAME is NULL"; exit 10; } 
[ -z "$CF_DISTRIBUTION_ID" ] && echo "WARNING: CF_DISTRIBUTION_ID is NULL" || echo "INFO: CF distribution detected"

# Build
{
    hugo -D
} || { echo "ERROR: Build failed, check hugo configurarion!"; exit 10; }

# Deploy
{
    aws s3 sync ./public
} || { echo "ERROR: Build failed, check hugo configurarion!"; exit 10; }

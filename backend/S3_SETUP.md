# S3 Setup and Configuration Guide

This document describes the S3 setup for the Model Registry system.

## Overview

The Model Registry uses two S3 buckets:
1. **ece30816-model-registry**: Stores model files (model weights, configs, etc.)
2. **ece30816-model-evaluations**: Stores evaluation results and metrics

## Bucket Configuration

### Bucket Features
- **Versioning**: Enabled to track model file versions
- **CORS**: Configured to allow web uploads/downloads
- **Public Read Access**: Bucket policy allows public read access for model files
- **Lifecycle Policies**: (Optional) Can be configured to archive old versions

### Bucket Locations
- **Region**: us-east-2
- **Billing Mode**: PAY_PER_REQUEST (no reserved capacity needed)

## Setup Instructions

### 1. Using the Setup Script

Run the database setup script to create the buckets:

```bash
cd backend
python src/database/setup.py
```

This will:
- Check if buckets already exist
- Create buckets if they don't exist
- Configure versioning and CORS
- Set up bucket policies

### 2. Manual AWS CLI Setup

Alternatively, create buckets manually:

```bash
# Create model registry bucket
aws s3 mb s3://ece30816-model-registry --region us-east-1

# Create evaluations bucket
aws s3 mb s3://ece30816-model-evaluations --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket ece30816-model-registry \
  --versioning-configuration Status=Enabled

aws s3api put-bucket-versioning \
  --bucket ece30816-model-evaluations \
  --versioning-configuration Status=Enabled
```

## Usage

### Using S3Manager

```python
from src.utils.s3_utils import S3Manager

# Initialize manager
manager = S3Manager("ece30816-model-registry")

# Upload a file
manager.upload_file("local_model.bin", "models/my-model/v1/model.bin")

# Generate presigned URL for client upload
url = manager.generate_presigned_upload_url("models/my-model/v1/model.bin")

# Download a file
manager.download_file("models/my-model/v1/model.bin", "downloaded.bin")

# List objects
objects = manager.list_objects(prefix="models/")
```

### Presigned URLs

The system uses presigned URLs for secure client uploads/downloads:

```python
# Generate upload URL (expires in 1 hour)
upload_url = manager.generate_presigned_upload_url(
    s3_key="models/model-id/v1/weights.bin",
    expiration=3600
)

# Generate download URL (expires in 24 hours)
download_url = manager.generate_presigned_download_url(
    s3_key="models/model-id/v1/weights.bin",
    expiration=86400
)
```

## File Organization

### Model Files Structure
```
ece30816-model-registry/
├── models/
│   ├── {model_id}/
│   │   ├── v1/
│   │   │   ├── model.bin
│   │   │   ├── config.json
│   │   │   └── tokenizer.json
│   │   ├── v2/
│   │   │   └── ...
│   │   └── metadata.json
```

### Evaluation Results Structure
```
ece30816-model-evaluations/
├── {model_id}/
│   ├── evaluations/
│   │   ├── {timestamp}/
│   │   │   ├── metrics.json
│   │   │   ├── logs.txt
│   │   │   └── artifacts/
```

## Security Considerations

1. **Public Read**: Model files are publicly readable for easy sharing
2. **Presigned Uploads**: Only pre-authorized URLs can upload files
3. **Access Control**: Future implementation will use IAM roles for Lambda functions
4. **Encryption**: S3 default encryption at rest is enabled

## Cost Optimization

- Use lifecycle policies to move old files to Glacier
- Delete old evaluations periodically
- Monitor usage in AWS Cost Explorer

## Troubleshooting

### Bucket Already Exists
If you get "BucketAlreadyExists" error, check if the bucket exists in another region.

### CORS Errors
If experiencing CORS errors from the frontend, verify bucket CORS configuration:
```bash
aws s3api get-bucket-cors --bucket ece30816-model-registry
```

### Access Denied
Check IAM permissions for the Lambda execution role:
- `s3:GetObject`
- `s3:PutObject`
- `s3:ListBucket`
- `s3:DeleteObject`

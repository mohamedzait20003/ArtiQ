from fastapi import FastAPI
from mangum import Mangum
from typing import Optional

app = FastAPI(title="Serverless FastAPI", version="0.1.0")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/s3/generate-upload-url")
def generate_s3_upload_url(s3_key: str, expiration: int = 3600):
    """
    Generate a presigned S3 upload URL.
    
    Args:
        s3_key: S3 object key
        expiration: URL expiration time in seconds
        
    Returns:
        Presigned upload URL
    """
    from src.utils.s3_utils import S3Manager
    
    manager = S3Manager("ece30816-model-registry")
    url = manager.generate_presigned_upload_url(s3_key, expiration)
    
    return {
        "url": url,
        "expires_in": expiration,
        "s3_key": s3_key
    }


@app.get("/s3/generate-download-url")
def generate_s3_download_url(s3_key: str, expiration: int = 3600):
    """
    Generate a presigned S3 download URL.
    
    Args:
        s3_key: S3 object key
        expiration: URL expiration time in seconds
        
    Returns:
        Presigned download URL
    """
    from src.utils.s3_utils import S3Manager
    
    manager = S3Manager("ece30816-model-registry")
    url = manager.generate_presigned_download_url(s3_key, expiration)
    
    return {
        "url": url,
        "expires_in": expiration,
        "s3_key": s3_key
    }


@app.get("/s3/list")
def list_s3_objects(prefix: str = "", max_keys: int = 100):
    """
    List objects in S3 bucket.
    
    Args:
        prefix: Prefix to filter objects
        max_keys: Maximum number of keys to return
        
    Returns:
        List of object keys
    """
    from src.utils.s3_utils import S3Manager
    
    manager = S3Manager("ece30816-model-registry")
    objects = manager.list_objects(prefix=prefix, max_keys=max_keys)
    
    return {
        "objects": [
            {
                "key": obj["Key"],
                "size": obj.get("Size", 0),
                "last_modified": obj.get("LastModified").isoformat() if obj.get("LastModified") else None
            }
            for obj in objects
        ],
        "count": len(objects)
    }


# AWS Lambda handler
handler = Mangum(app)

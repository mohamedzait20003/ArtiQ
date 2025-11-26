import os
from mangum import Mangum
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.lib.aws import AWSServices
from app.bootstrap import bootstrap_services
from app.routes import register_api_routes

# Initialize AWS region
os.environ.setdefault("AWS_REGION", "us-east-2")
AWSServices.initialize(region=os.environ.get("AWS_REGION"))

app = FastAPI(title="Serverless FastAPI", version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Bootstrap application services
bootstrap_services()

# Register API routes
register_api_routes(app)

# AWS Lambda handler
handler = Mangum(app)

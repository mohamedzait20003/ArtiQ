import os
from fastapi import FastAPI
from mangum import Mangum
from src.controllers import AuthController

# Set AWS region from environment variable (fallback to us-east-2)
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-2")

app = FastAPI(title="Serverless FastAPI", version="0.1.0")

# Initializations of Controllers.
auth_controller = AuthController()


# Register routers
app.include_router(auth_controller.get_router(), prefix="/auth", tags=["auth"])


# AWS Lambda handler
handler = Mangum(app)

import os
from fastapi import FastAPI
from mangum import Mangum
from src.controllers import AuthController
from src.controllers.artifact_controller import ArtifactController

# Set AWS region from environment variable (fallback to us-east-2)
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-2")

app = FastAPI(title="Serverless FastAPI", version="0.1.0")

# Initializations of Controllers.
auth_controller = AuthController()
artifact_controller = ArtifactController()

# Register routers
app.include_router(auth_controller.get_router(), prefix="/auth", tags=["auth"])
app.include_router(artifact_controller.get_router(), prefix="/api",
                   tags=["artifacts"])


# AWS Lambda handler
handler = Mangum(app)

import os
import json
import boto3
from fastapi import FastAPI, Header, HTTPException, Depends
from mangum import Mangum
from src.controllers import AuthController
from src.controllers.artifact_controller import ArtifactController

os.environ.setdefault("AWS_REGION", "us-east-2")

app = FastAPI(title="Serverless FastAPI", version="0.1.0")

# Initializations of Controllers.
auth_controller = AuthController()
artifact_controller = ArtifactController()

# AWS Lambda client for invoking reset function
lambda_client = boto3.client('lambda')

# Health endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Reset endpoint
@app.delete("/reset")
async def reset_registry(x_authorization: str = Header(alias="X-Authorization")):
    """
    Reset the registry to a system default state
    """
    try:
        # Get the reset function name from environment
        reset_function_name = os.environ.get('REGISTRY_RESET_FUNCTION', 'ece461-registry-reset')
        
        # Prepare the event for the Lambda function
        event_payload = {
            'X-Authorization': x_authorization,
            'ARTIFACTS_BUCKET': os.environ.get('ARTIFACTS_BUCKET', 'artifacts-bucket')
        }
        
        # Invoke the reset Lambda function
        response = lambda_client.invoke(
            FunctionName=reset_function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(event_payload)
        )
        
        # Parse the response
        result = json.loads(response['Payload'].read())
        
        if response['StatusCode'] == 200 and result.get('statusCode') == 200:
            return {"message": "Registry is reset"}
        elif result.get('statusCode') == 403:
            raise HTTPException(status_code=403, detail="Authentication failed due to invalid or missing AuthenticationToken")
        elif result.get('statusCode') == 401:
            raise HTTPException(status_code=401, detail="You do not have permission to reset the registry")
        else:
            raise HTTPException(status_code=500, detail="Internal server error")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Register routers
app.include_router(auth_controller.get_router(), prefix="", tags=["auth"])
app.include_router(artifact_controller.get_router(), prefix="",
                   tags=["artifacts"])


# AWS Lambda handler
handler = Mangum(app)

import uuid
import json
import os
import boto3
from typing import Optional, List
from .controller import Controller
from src.models.Artifact_Model import Artifact_Model
from fastapi import HTTPException, status, Query, Path, Body
from pydantic import BaseModel


# Pydantic models for request/response schemas
class ArtifactQuery(BaseModel):
    name: str
    types: Optional[List[str]] = None

class ArtifactData(BaseModel):
    url: str

class ArtifactMetadata(BaseModel):
    name: str
    id: str
    type: str

class Artifact(BaseModel):
    metadata: ArtifactMetadata
    data: ArtifactData

class ArtifactRegEx(BaseModel):
    regex: str

class SimpleLicenseCheckRequest(BaseModel):
    github_url: str


class ArtifactController(Controller):
    """
    Artifact Controller
    Handles ML model artifact uploads, retrieval, and management
    """

    def __init__(self):
        super().__init__()
        self.lambda_client = boto3.client('lambda')

    def register_routes(self):
        """Register artifact routes"""


        @self.router.post("/artifacts", 
                         status_code=status.HTTP_200_OK,
                         response_model=List[ArtifactMetadata])
        async def artifacts_list(
            queries: List[ArtifactQuery],
            offset: Optional[str] = Query(None, description="Pagination offset")
        ):
            """Get the artifacts from the registry (BASELINE)"""
            # TODO: Implement logic
            raise HTTPException(status_code=501, detail="Not implemented")


        @self.router.post("/artifact/{artifact_type}",
                         status_code=status.HTTP_201_CREATED,
                         response_model=Artifact)
        async def artifact_create(
            artifact_type: str = Path(..., description="Type of artifact being ingested"),
            artifact_data: ArtifactData = Body(...)
        ):
            """Register a new artifact (BASELINE)"""
            try:
                # Get function name from environment variable
                function_name = os.getenv('ARTIFACT_CREATE_FUNCTION', 'ece461-artifact-create')
                
                # Prepare payload for Lambda function
                payload = {
                    'artifact_type': artifact_type,
                    'artifact_data': artifact_data.model_dump()
                }
                
                # Invoke the Lambda function
                response = self.lambda_client.invoke(
                    FunctionName=function_name,
                    InvocationType='RequestResponse',  # Synchronous
                    Payload=json.dumps(payload)
                )
                
                # Parse response
                result = json.loads(response['Payload'].read())
                
                if response['StatusCode'] == 200:
                    return result
                else:
                    raise HTTPException(
                        status_code=response.get('StatusCode', 500),
                        detail=result.get('errorMessage', 'Lambda function execution failed')
                    )
                    
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error invoking artifact_create: {str(e)}")


        @self.router.get("/artifacts/{artifact_type}/{id}",
                        status_code=status.HTTP_200_OK,
                        response_model=Artifact)
        async def artifact_retrieve(
            artifact_type: str = Path(..., description="Type of artifact to fetch"),
            id: str = Path(..., description="ID of artifact to fetch")
        ):
            """Interact with the artifact with this id (BASELINE)"""
            # TODO: Implement logic
            raise HTTPException(status_code=501, detail="Not implemented")


        @self.router.put("/artifacts/{artifact_type}/{id}",
                        status_code=status.HTTP_200_OK)
        async def artifact_update(
            artifact_type: str = Path(..., description="Type of artifact to update"),
            id: str = Path(..., description="Artifact ID"),
            artifact: Artifact = Body(...)
        ):
            """Update this content of the artifact (BASELINE)"""
            # TODO: Implement logic
            raise HTTPException(status_code=501, detail="Not implemented")


        @self.router.delete("/artifacts/{artifact_type}/{id}",
                           status_code=status.HTTP_200_OK)
        async def artifact_delete(
            artifact_type: str = Path(..., description="Type of artifact to delete"),
            id: str = Path(..., description="Artifact ID")
        ):
            """Delete this artifact (NON-BASELINE)"""
            # TODO: Implement logic
            raise HTTPException(status_code=501, detail="Not implemented")


        @self.router.get("/artifact/model/{id}/rate",
                        status_code=status.HTTP_200_OK)
        async def model_artifact_rate(
            id: str = Path(..., description="Artifact ID")
        ):
            """Get ratings for this model artifact (BASELINE)"""
            # TODO: Implement logic
            raise HTTPException(status_code=501, detail="Not implemented")


        @self.router.get("/artifact/{artifact_type}/{id}/cost",
                        status_code=status.HTTP_200_OK)
        async def artifact_cost(
            artifact_type: str = Path(..., description="Type of artifact"),
            id: str = Path(..., description="Artifact ID"),
            dependency: Optional[bool] = Query(False, description="Include dependencies")
        ):
            """Get the cost of an artifact (BASELINE)"""
            # TODO: Implement logic
            raise HTTPException(status_code=501, detail="Not implemented")


        @self.router.get("/artifact/byName/{name}",
                        status_code=status.HTTP_200_OK,
                        response_model=List[ArtifactMetadata])
        async def artifact_by_name_get(
            name: str = Path(..., description="Artifact name")
        ):
            """List artifact metadata for this name (NON-BASELINE)"""
            # TODO: Implement logic
            raise HTTPException(status_code=501, detail="Not implemented")


        @self.router.get("/artifact/{artifact_type}/{id}/audit",
                        status_code=status.HTTP_200_OK)
        async def artifact_audit_get(
            artifact_type: str = Path(..., description="Type of artifact to audit"),
            id: str = Path(..., description="Artifact ID")
        ):
            """Retrieve audit entries for this artifact (NON-BASELINE)"""
            # TODO: Implement logic
            raise HTTPException(status_code=501, detail="Not implemented")


        @self.router.get("/artifact/model/{id}/lineage",
                        status_code=status.HTTP_200_OK)
        async def artifact_lineage_get(
            id: str = Path(..., description="Artifact ID")
        ):
            """Retrieve the lineage graph for this artifact (BASELINE)"""
            # TODO: Implement logic
            raise HTTPException(status_code=501, detail="Not implemented")


        @self.router.post("/artifact/model/{id}/license-check",
                         status_code=status.HTTP_200_OK,
                         response_model=bool)
        async def artifact_license_check(
            id: str = Path(..., description="Artifact ID"),
            request: SimpleLicenseCheckRequest = Body(...)
        ):
            """Assess license compatibility for fine-tune and inference usage (BASELINE)"""
            # TODO: Implement logic
            raise HTTPException(status_code=501, detail="Not implemented")


        @self.router.post("/artifact/byRegEx",
                         status_code=status.HTTP_200_OK,
                         response_model=List[ArtifactMetadata])
        async def artifact_by_regex_get(
            regex_request: ArtifactRegEx = Body(...)
        ):
            """Get any artifacts fitting the regular expression (BASELINE)"""
            # TODO: Implement logic
            raise HTTPException(status_code=501, detail="Not implemented")

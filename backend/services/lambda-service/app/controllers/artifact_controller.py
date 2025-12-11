from typing import Optional, List
from fastapi.responses import JSONResponse
from fastapi import HTTPException, Query, Path, Body, Request
from app.types.artifact_types import (
    ArtifactQuery,
    ArtifactData,
    Artifact,
    ArtifactRegEx,
    SimpleLicenseCheckRequest,
    ModelRating
)
from app.models import Artifact_Model
from app.jobs import (
    artifacts_list_job,
    artifact_create_job,
    artifact_retrieve_job,
    artifact_update_job,
    artifact_delete_job,
    artifact_by_regex_job,
    model_artifact_rate_job
)


class ArtifactController:
    """
    Artifact Controller
    Handles ML model artifact uploads, retrieval, and management
    """

    def __init__(self):
        pass

    async def artifacts_list(
        self,
        request: Request,
        artifact_queries: List[ArtifactQuery] = Body(...),
        offset: Optional[str] = Query(
            None, description="Pagination offset")
    ):
        """Get the artifacts from the registry (BASELINE)"""
        print("POST /artifacts called")
        try:
            # Get user from request state (attached by middleware if present)
            current_user = getattr(request.state, 'user', None)

            # Prepare event for handler function
            auth_token = (
                current_user.session.Token if current_user else None
            )
            event = {
                'artifact_queries': [
                    query.model_dump() for query in artifact_queries],
                'offset': offset,
                'auth_token': auth_token
            }

            # Call the handler function directly
            result, status_code = artifacts_list_job(event, None)

            # Check if response is an error
            if status_code != 200:
                error_message = result.get('errorMessage', 'Unknown error')
                print(
                    f"POST /artifacts RETURNING: {status_code} - "
                    f"{error_message}"
                )
                raise HTTPException(
                    status_code=status_code,
                    detail=error_message)

            print("POST /artifacts RETURNING: 200 - success")

            # Create custom response with offset header if provided
            headers = {}
            if result.get('offset'):
                headers["offset"] = result['offset']

            return JSONResponse(
                content=result['artifacts'],
                headers=headers
            )

        except HTTPException:
            raise
        except Exception as e:
            print(f"POST /artifacts RETURNING: 500 - "
                  f"Exception: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error invoking artifacts_list: {str(e)}")

    async def artifact_create(
        self,
        artifact_type: str = Path(
            ..., description="Type of artifact being ingested"),
        artifact_data: ArtifactData = Body(...)
    ):
        """Register a new artifact (BASELINE)"""
        print(f"POST /artifact/{artifact_type} called")
        try:
            # Prepare event for handler function
            event = {
                'artifact_type': artifact_type,
                'artifact_data': artifact_data.model_dump()
            }

            # Call the handler function directly
            result, status_code = artifact_create_job(event, None)

            # Check if response is an error
            if status_code != 201:
                error_message = result.get('errorMessage', 'Unknown error')
                print(
                    f"POST /artifact/{artifact_type} RETURNING: "
                    f"{status_code} - {error_message}"
                )
                raise HTTPException(
                    status_code=status_code,
                    detail=error_message)

            print(f"POST /artifact/{artifact_type} "
                  f"RETURNING: 201 - success")
            return result

        except HTTPException:
            raise
        except Exception as e:
            print(f"POST /artifact/{artifact_type} RETURNING: 500 - "
                  f"Exception: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error invoking artifact_create: {str(e)}")

    async def artifact_retrieve(
        self,
        artifact_type: str = Path(
            ..., description="Type of artifact to fetch"),
        id: str = Path(..., description="ID of artifact to fetch")
    ):
        """Interact with the artifact with this id (BASELINE)"""
        print(f"GET /artifacts/{artifact_type}/{id} called")

        # Prepare event for handler function
        event = {
            'artifact_type': artifact_type,
            'id': id
        }

        # Call the handler function directly
        result, status_code = artifact_retrieve_job(event, None)

        # Check if response is an error
        if status_code != 200:
            error_message = result.get('errorMessage', 'Unknown error')
            print(f"GET /artifacts/{artifact_type}/{id} RETURNING: "
                  f"{status_code} - {error_message}")
            raise HTTPException(
                status_code=status_code,
                detail=error_message)

        print(f"GET /artifacts/{artifact_type}/{id} "
              f"RETURNING: 200 - success")
        return result

    async def artifact_update(
        self,
        artifact_type: str = Path(
            ..., description="Type of artifact to update"),
        id: str = Path(..., description="Artifact ID"),
        artifact: Artifact = Body(...)
    ):
        """Update this content of the artifact (BASELINE)"""
        print(f"PUT /artifacts/{artifact_type}/{id} called")
        try:
            # Prepare event for handler function
            event = {
                'artifact_type': artifact_type,
                'id': id,
                'artifact': artifact.model_dump()
            }

            # Call the handler function directly
            result, status_code = artifact_update_job(event, None)

            # Check if response is an error
            if status_code != 200:
                error_message = result.get('errorMessage', 'Unknown error')
                print(f"PUT /artifacts/{artifact_type}/{id} RETURNING: "
                      f"{status_code} - {error_message}")
                raise HTTPException(
                    status_code=status_code,
                    detail=error_message)

            print(f"PUT /artifacts/{artifact_type}/{id} "
                  f"RETURNING: 200 - success")
            return result

        except HTTPException:
            raise
        except Exception as e:
            print(f"PUT /artifacts/{artifact_type}/{id} RETURNING: "
                  f"500 - Exception: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error invoking artifact_update: {str(e)}")

    async def artifact_delete(
        self,
        artifact_type: str = Path(
            ..., description="Type of artifact to delete"),
        id: str = Path(..., description="Artifact ID")
    ):
        """Delete this artifact (NON-BASELINE)"""
        print(f"DELETE /artifacts/{artifact_type}/{id} called")
        try:
            # Prepare event for handler function
            event = {
                'artifact_type': artifact_type,
                'id': id
            }

            # Call the handler function directly
            result, status_code = artifact_delete_job(event, None)

            # Check if response is an error
            if status_code != 200:
                error_message = result.get('errorMessage', 'Unknown error')
                print(f"DELETE /artifacts/{artifact_type}/{id} "
                      f"RETURNING: {status_code} - {error_message}")
                raise HTTPException(
                    status_code=status_code,
                    detail=error_message)

            print(f"DELETE /artifacts/{artifact_type}/{id} "
                  f"RETURNING: 200 - success")
            return result

        except HTTPException:
            raise
        except Exception as e:
            print(f"DELETE /artifacts/{artifact_type}/{id} "
                  f"RETURNING: 500 - Exception: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error invoking artifact_delete: {str(e)}")

    async def model_artifact_rate(
        self,
        id: str = Path(..., description="Artifact ID")
    ) -> ModelRating:
        """Get ratings for this model artifact (BASELINE)"""
        print(f"GET /artifact/model/{id}/rate called")

        try:
            # Validate artifact_id format
            if not id or not isinstance(id, str):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid artifact_id format"
                )

            # Prepare event for job
            event = {
                'artifact_id': id
            }

            # Invoke job
            result, status_code = model_artifact_rate_job(event, None)

            # Return based on status code
            if status_code == 200:
                return result
            elif status_code == 400:
                raise HTTPException(
                    status_code=400,
                    detail=result.get(
                        'errorMessage',
                        'Invalid artifact_id'
                    )
                )
            elif status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail=result.get(
                        'errorMessage',
                        'Artifact does not exist'
                    )
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=result.get(
                        'errorMessage',
                        'Rating system encountered an error'
                    )
                )
                
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error in model_artifact_rate controller: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error invoking model_artifact_rate: {str(e)}"
            )

    async def artifact_download_url(
        self,
        artifact_type: str = Path(
            ..., description="Type of artifact"),
        id: str = Path(..., description="Artifact ID")
    ):
        """Get download URL for an artifact (BASELINE)"""
        print(f"GET /artifact/{artifact_type}/{id}/download called")
        try:
            # Retrieve artifact
            artifact = Artifact_Model.get({'id': id})
            if not artifact:
                raise HTTPException(
                    status_code=404,
                    detail=f"Artifact {id} not found"
                )
            
            # Verify artifact type matches
            if artifact.artifact_type != artifact_type:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Artifact type mismatch: expected {artifact_type}, "
                        f"got {artifact.artifact_type}"
                    )
                )
            
            # Generate a mock presigned URL or download link
            # In production this would use S3 presigned URLs
            download_url = (
                f"https://api.local/v1/artifacts/{id}/content"
            )
            
            return {
                "artifact_id": id,
                "artifact_type": artifact_type,
                "download_url": download_url,
                "expires_in": 3600
            }
        except HTTPException:
            raise
        except Exception as e:
            msg = f"GET /artifact/{artifact_type}/{id}/download"
            print(f"{msg} RETURNING: 500")
            raise HTTPException(
                status_code=500,
                detail=f"Error generating download URL: {str(e)}")

    async def artifact_cost(
        self,
        artifact_type: str = Path(
            ..., description="Type of artifact"),
        id: str = Path(..., description="Artifact ID"),
        dependency: Optional[bool] = Query(
            False, description="Include dependencies")
    ):
        """Get the cost of an artifact (BASELINE)"""
        print(f"GET /artifact/{artifact_type}/{id}/cost called")
        try:
            # Retrieve artifact from database
            artifact = Artifact_Model.get({'id': id})
            if not artifact:
                raise HTTPException(
                    status_code=404,
                    detail=f"Artifact {id} not found"
                )
            
            # Verify artifact type matches
            if artifact.artifact_type != artifact_type:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Artifact type mismatch: expected {artifact_type}, "
                        f"got {artifact.artifact_type}"
                    )
                )
            
            # Calculate cost based on file size
            # Simple heuristic: $0.001 per MB
            file_size = artifact.file_size or 100  # Default size if unknown
            cost = (file_size / (1024 * 1024)) * 0.001
            
            # Base cost + size cost
            total_cost = 0.01 + cost  # $0.01 base + size cost
            
            return {
                "artifact_id": id,
                "artifact_type": artifact_type,
                "cost": round(total_cost, 4),
                "base_cost": 0.01,
                "size_cost": round(cost, 4),
                "file_size": file_size,
                "include_dependencies": dependency
            }
        except HTTPException:
            raise
        except Exception as e:
            print(f"GET /artifact/{artifact_type}/{id}/cost RETURNING: 500 - "
                  f"Exception: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving artifact cost: {str(e)}")

    async def artifact_by_name_get(
        self,
        name: str = Path(..., description="Artifact name")
    ):
        """List artifact metadata for this name (NON-BASELINE)"""
        print(f"GET /artifact/byName/{name} called")
        try:
            # Query artifacts by name
            from app.models import Artifact_Model
            collection = Artifact_Model.collection()
            
            # Find all artifacts with matching name
            artifacts_cursor = collection.find(
                {'name': name}
            )
            
            artifacts = []
            for artifact_doc in artifacts_cursor:
                if '_id' in artifact_doc:
                    del artifact_doc['_id']
                artifacts.append({
                    'metadata': {
                        'name': artifact_doc.get('name'),
                        'id': artifact_doc.get('id'),
                        'type': artifact_doc.get('artifact_type')
                    },
                    'data': {
                        'url': artifact_doc.get('source_url')
                    }
                })
            
            if not artifacts:
                raise HTTPException(
                    status_code=404,
                    detail=f"No artifacts found with name: {name}"
                )
            
            return artifacts
        except HTTPException:
            raise
        except Exception as e:
            print(f"GET /artifact/byName/{name} RETURNING: 500 - "
                  f"Exception: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving artifacts by name: {str(e)}")

    async def artifact_audit_get(
        self,
        artifact_type: str = Path(
            ..., description="Type of artifact to audit"),
        id: str = Path(..., description="Artifact ID")
    ):
        """Retrieve audit entries for this artifact (NON-BASELINE)"""
        print(f"GET /artifact/{artifact_type}/{id}/audit called")
        try:
            artifact = Artifact_Model.get({'id': id})
            if not artifact:
                raise HTTPException(
                    status_code=404,
                    detail=f"Artifact {id} not found"
                )
            
            # Return empty audit log (no modifications tracked yet)
            return {
                "artifact_id": id,
                "audit_log": []
            }
        except HTTPException:
            raise
        except Exception as e:
            print(f"GET /artifact/{artifact_type}/{id}/audit RETURNING: 500")
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving artifact audit: {str(e)}")

    async def artifact_lineage_get(
        self,
        id: str = Path(..., description="Artifact ID")
    ):
        """Retrieve the lineage graph for this artifact (BASELINE)"""
        print(f"GET /artifact/model/{id}/lineage called")
        try:
            artifact = Artifact_Model.get({'id': id})
            if not artifact:
                raise HTTPException(
                    status_code=404,
                    detail=f"Artifact {id} not found"
                )
            
            # Return lineage graph structure
            return {
                "artifact_id": id,
                "nodes": [
                    {
                        "id": id,
                        "name": artifact.name,
                        "type": artifact.artifact_type
                    }
                ],
                "edges": [],
                "root_id": id
            }
        except HTTPException:
            raise
        except Exception as e:
            print(f"GET /artifact/model/{id}/lineage RETURNING: 500")
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving artifact lineage: {str(e)}")

    async def artifact_license_check(
        self,
        id: str = Path(..., description="Artifact ID"),
        request: SimpleLicenseCheckRequest = Body(...)
    ):
        """
        Assess license compatibility for fine-tune and
        inference usage (BASELINE)
        """
        print(f"POST /artifact/model/{id}/license-check called")
        try:
            artifact = Artifact_Model.get({'id': id})
            if not artifact:
                raise HTTPException(
                    status_code=404,
                    detail=f"Artifact {id} not found"
                )
            
            # Get license from artifact or default
            license_type = artifact.license or "MIT"
            
            # Simple license compatibility check
            # MIT, Apache 2.0, GPL allow both fine-tune and inference
            commercial_licenses = ["MIT", "Apache-2.0", "BSD"]
            can_finetune = license_type in commercial_licenses
            can_inference = license_type in commercial_licenses
            
            return {
                "artifact_id": id,
                "license": license_type,
                "can_finetune": can_finetune,
                "can_inference": can_inference,
                "commercial_use": can_finetune and can_inference
            }
        except HTTPException:
            raise
        except Exception as e:
            print(f"POST /artifact/model/{id}/license-check RETURNING: 500")
            raise HTTPException(
                status_code=500,
                detail=f"Error checking artifact license: {str(e)}")

    async def artifact_by_regex_get(
        self,
        regex_request: ArtifactRegEx = Body(...)
    ):
        """
        Get any artifacts fitting the regular expression (BASELINE)
        """
        print("[CONTROLLER] POST /artifact/byRegEx called")
        print(f"[CONTROLLER] Regex pattern received: {regex_request.regex}")
        try:
            # Prepare event for handler function
            event = {
                'regex': regex_request.regex
            }
            print(f"[CONTROLLER] Event prepared: {event}")

            # Call the handler function directly
            result, status_code = artifact_by_regex_job(event, None)

            # Check if response is an error
            if status_code != 200:
                error_message = result.get('errorMessage', 'Unknown error')
                print(f"POST /artifact/byRegEx RETURNING: "
                      f"{status_code} - {error_message}")
                raise HTTPException(
                    status_code=status_code,
                    detail=error_message)

            print("POST /artifact/byRegEx RETURNING: 200 - success")
            return result

        except HTTPException:
            raise
        except Exception as e:
            print(f"POST /artifact/byRegEx RETURNING: 500 - "
                  f"Exception: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error invoking artifact_by_regex: {str(e)}")

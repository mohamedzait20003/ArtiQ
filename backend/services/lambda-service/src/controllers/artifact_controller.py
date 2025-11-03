import uuid
import json
from typing import Optional
from .controller import Controller
from src.models.ML_Model import ML_Model
from fastapi import HTTPException, status, UploadFile, File, Form


class ArtifactController(Controller):
    """
    Artifact Controller
    Handles ML model artifact uploads, retrieval, and management
    """

    def register_routes(self):
        """Register artifact routes"""

        @self.router.post("/models/upload",
                          status_code=status.HTTP_201_CREATED)
        async def upload_model(
            title: str = Form(...),
            model_file: UploadFile = File(...),
            metadata: Optional[str] = Form(None)
        ):
            """
            Upload a new ML model with artifact

            Args:
                title: Model title
                model_file: Binary model file (pickle, h5, pt, etc.)
                metadata: JSON string of model metadata (optional)

            Returns:
                Success message with model ID

            Raises:
                HTTPException: If upload fails
            """
            # Read the uploaded file
            model_artifact = await model_file.read()

            # Parse JSON strings
            metadata_dict = json.loads(metadata) if metadata else {}

            # Create ML model
            model = ML_Model(
                ModelID=str(uuid.uuid4()),
                Title=title,
                Metadata=metadata_dict,
                ModelArtifact=model_artifact
            )

            if model.save():
                return {
                    "message": "Model uploaded successfully",
                    "model_id": model.ModelID,
                    "s3_key": model.ModelArtifact_s3_key
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to upload model"
                )

        @self.router.get("/models/{model_id}")
        async def get_model(model_id: str):
            """
            Get model metadata by ID

            Args:
                model_id: The model ID

            Returns:
                Model metadata (without binary artifact)

            Raises:
                HTTPException: If model not found
            """
            model = ML_Model.get({"ModelID": model_id})
            if not model:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Model not found"
                )

            return model.to_dict()

        @self.router.get("/models/{model_id}/download")
        async def get_model_download_url(model_id: str):
            """
            Get presigned URL to download model artifact

            Args:
                model_id: The model ID

            Returns:
                Presigned URL for downloading the model artifact

            Raises:
                HTTPException: If model not found
            """
            model = ML_Model.get({"ModelID": model_id})
            if not model:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Model not found"
                )

            url = model.get_file_url("ModelArtifact", expires_in=3600)
            if not url:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to generate download URL"
                )

            return {"download_url": url, "expires_in": 3600}

        @self.router.get("/models")
        async def list_models():
            """
            List all ML models

            Returns:
                List of model metadata
            """
            models = ML_Model.list_all()
            return [model.to_dict() for model in models]

        @self.router.put("/models/{model_id}/evaluation")
        async def update_evaluation(model_id: str, metrics: dict):
            """
            Update model evaluation metrics

            Args:
                model_id: The model ID
                metrics: Dictionary of evaluation metrics

            Returns:
                Success message

            Raises:
                HTTPException: If model not found or update fails
            """
            model = ML_Model.get({"ModelID": model_id})
            if not model:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Model not found"
                )

            if model.update_evaluation(metrics):
                return {"message": "Evaluation updated successfully"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update evaluation"
                )

        @self.router.put("/models/{model_id}/metadata")
        async def update_metadata(model_id: str, metadata: dict):
            """
            Update model metadata

            Args:
                model_id: The model ID
                metadata: Dictionary of metadata fields

            Returns:
                Success message

            Raises:
                HTTPException: If model not found or update fails
            """
            model = ML_Model.get({"ModelID": model_id})
            if not model:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Model not found"
                )

            if model.update_metadata(metadata):
                return {"message": "Metadata updated successfully"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update metadata"
                )

        @self.router.delete("/models/{model_id}")
        async def delete_model(model_id: str):
            """
            Delete a model and its artifact from S3

            Args:
                model_id: The model ID

            Returns:
                Success message

            Raises:
                HTTPException: If model not found or deletion fails
            """
            model = ML_Model.get({"ModelID": model_id})
            if not model:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Model not found"
                )

            if model.delete():
                return {"message": "Model deleted successfully"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete model"
                )

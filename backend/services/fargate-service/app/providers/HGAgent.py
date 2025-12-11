"""
HuggingFace Agent
Handles interactions with HuggingFace API for models and datasets
"""

import os
import logging
from typing import Dict, Any
from huggingface_hub import ModelInfo, DatasetInfo
from lib.huggingface import HuggingFaceAPIManager


class HGAgent:
    """
    HuggingFace Agent for retrieving model and dataset information
    """

    def __init__(self):
        """
        Initialize HuggingFace Agent
        Args:
            token: Optional HuggingFace API token. If not provided,
                   will use HF_TOKEN from environment variables
        """
        token = os.getenv("HF_TOKEN")
        self.hf_manager = HuggingFaceAPIManager(token=token)
        logging.info("[HGAgent] Initialized HuggingFace Agent")

    def get_model_data(self, model_url: str) -> Dict[str, Any]:
        """
        Get model data from HuggingFace

        Args:
            model_url: HuggingFace model URL

        Returns:
            Dictionary with model information
        """
        try:
            # Convert URL to model ID
            model_id = self.hf_manager.model_link_to_id(model_url)
            logging.info(f"[HGAgent] Fetching model data for: {model_id}")

            # Get model info
            model_info: ModelInfo = self.hf_manager.get_model_info(
                model_id
            )

            # Download README if available
            readme_path = self.hf_manager.download_model_readme(model_id)
            readme_content = None
            if readme_path:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    readme_content = f.read()

            # Extract relevant information
            return {
                "success": True,
                "model_id": model_info.id,
                "author": model_info.author,
                "tags": model_info.tags,
                "pipeline_tag": model_info.pipeline_tag,
                "library_name": model_info.library_name,
                "downloads": model_info.downloads,
                "likes": model_info.likes,
                "private": model_info.private,
                "gated": getattr(model_info, 'gated', None),
                "last_modified": str(model_info.last_modified)
                if model_info.last_modified else None,
                "readme": readme_content,
                "card_data": model_info.card_data,
                "siblings": [
                    {"filename": s.rfilename, "size": getattr(s, 'size', None)}
                    for s in (model_info.siblings or [])
                ]
            }

        except Exception as e:
            logging.error(f"[HGAgent] Error fetching model data: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "model_id": None
            }

    def get_dataset_data(self, dataset_url: str) -> Dict[str, Any]:
        """
        Get dataset data from HuggingFace

        Args:
            dataset_url: HuggingFace dataset URL

        Returns:
            Dictionary with dataset information
        """
        try:
            # Convert URL to dataset ID
            dataset_id = self.hf_manager.dataset_link_to_id(dataset_url)
            logging.info(
                f"[HGAgent] Fetching dataset data for: {dataset_id}"
            )

            # Get dataset info
            dataset_info: DatasetInfo = self.hf_manager.get_dataset_info(
                dataset_id
            )

            # Download README if available
            readme_path = self.hf_manager.download_dataset_readme(
                dataset_id
            )
            readme_content = None
            if readme_path:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    readme_content = f.read()

            # Extract relevant information
            return {
                "success": True,
                "dataset_id": dataset_info.id,
                "author": dataset_info.author,
                "tags": dataset_info.tags,
                "downloads": dataset_info.downloads,
                "likes": dataset_info.likes,
                "private": dataset_info.private,
                "gated": getattr(dataset_info, 'gated', None),
                "last_modified": str(dataset_info.last_modified)
                if dataset_info.last_modified else None,
                "readme": readme_content,
                "card_data": dataset_info.card_data,
                "siblings": [
                    {"filename": s.rfilename, "size": getattr(s, 'size', None)}
                    for s in (dataset_info.siblings or [])
                ]
            }

        except Exception as e:
            logging.error(f"[HGAgent] Error fetching dataset data: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "dataset_id": None
            }

    def extract_metadata(
        self,
        artifact_url: str,
        artifact_type: str
    ) -> Dict[str, Any]:
        """
        Extract metadata from HuggingFace artifact

        Args:
            artifact_url: HuggingFace artifact URL
            artifact_type: Type of artifact ('model' or 'dataset')

        Returns:
            Dictionary with extracted metadata
        """
        if artifact_type.lower() == 'model':
            return self.get_model_data(artifact_url)
        elif artifact_type.lower() == 'dataset':
            return self.get_dataset_data(artifact_url)
        else:
            return {
                "success": False,
                "error": f"Unknown artifact type: {artifact_type}"
            }

    # Delegation methods for direct manager access
    def model_link_to_id(self, model_link: str) -> str:
        """Delegate to HuggingFaceAPIManager.model_link_to_id"""
        return self.hf_manager.model_link_to_id(model_link)

    def dataset_link_to_id(self, dataset_link: str) -> str:
        """Delegate to HuggingFaceAPIManager.dataset_link_to_id"""
        return self.hf_manager.dataset_link_to_id(dataset_link)

    def get_model_info(self, model_id: str) -> ModelInfo:
        """Delegate to HuggingFaceAPIManager.get_model_info"""
        return self.hf_manager.get_model_info(model_id)

    def get_dataset_info(self, dataset_id: str) -> DatasetInfo:
        """Delegate to HuggingFaceAPIManager.get_dataset_info"""
        return self.hf_manager.get_dataset_info(dataset_id)

    def download_model_readme(self, model_id: str):
        """Delegate to HuggingFaceAPIManager.download_model_readme"""
        return self.hf_manager.download_model_readme(model_id)

    def download_dataset_readme(self, dataset_id: str):
        """Delegate to HuggingFaceAPIManager.download_dataset_readme"""
        return self.hf_manager.download_dataset_readme(dataset_id)

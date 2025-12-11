"""
HuggingFace Agent
Handles interactions with HuggingFace API for models and datasets with caching
"""

import os
import logging
from typing import Dict, Any, List, Optional
from huggingface_hub import ModelInfo, DatasetInfo
from lib.huggingface import HuggingFaceAPIManager
from lib.cache import Cache

logger = logging.getLogger(__name__)

# Cache TTL constants (in seconds)
MODEL_INFO_TTL = 600  # 10 minutes
DATASET_INFO_TTL = 600  # 10 minutes
MODEL_README_TTL = 900  # 15 minutes
DATASET_README_TTL = 900  # 15 minutes


class HGAgent:
    """
    HuggingFace Agent with caching and high-level operations
    Handles all HuggingFace API interactions with intelligent caching
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
        
        # Initialize Cache instances with appropriate TTLs
        self._model_info_cache = Cache(default_ttl=MODEL_INFO_TTL)
        self._dataset_info_cache = Cache(default_ttl=DATASET_INFO_TTL)
        self._model_readme_cache = Cache(default_ttl=MODEL_README_TTL)
        self._dataset_readme_cache = Cache(default_ttl=DATASET_README_TTL)
        
        logger.info("[HGAgent] Initialized with TTL-based caching enabled")

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

    # Delegation methods with caching
    def model_link_to_id(self, model_link: str) -> str:
        """Convert model link to ID (no caching needed)"""
        return self.hf_manager.model_link_to_id(model_link)

    def dataset_link_to_id(self, dataset_link: str) -> str:
        """Convert dataset link to ID (no caching needed)"""
        return self.hf_manager.dataset_link_to_id(dataset_link)

    def get_model_info(self, model_id: str) -> ModelInfo:
        """Get model info with caching"""
        def fetch_model_info():
            try:
                result = self.hf_manager.get_model_info(model_id)
                logger.debug(f"[HGAgent] Cached model info for {model_id}")
                return result
            except Exception as e:
                logger.error(
                    f"[HGAgent] Model info fetch failed for {model_id}: {e}"
                )
                raise
        
        return self._model_info_cache.remember(
            model_id,
            MODEL_INFO_TTL,
            fetch_model_info
        )

    def get_dataset_info(self, dataset_id: str) -> DatasetInfo:
        """Get dataset info with caching"""
        def fetch_dataset_info():
            try:
                result = self.hf_manager.get_dataset_info(dataset_id)
                logger.debug(
                    f"[HGAgent] Cached dataset info for {dataset_id}"
                )
                return result
            except Exception as e:
                logger.error(
                    f"[HGAgent] Dataset info fetch failed for "
                    f"{dataset_id}: {e}"
                )
                raise
        
        return self._dataset_info_cache.remember(
            dataset_id,
            DATASET_INFO_TTL,
            fetch_dataset_info
        )

    def download_model_readme(self, model_id: str) -> Optional[str]:
        """Download model README with caching"""
        def fetch_readme():
            readme_path = self.hf_manager.download_model_readme(model_id)
            if readme_path:
                logger.debug(
                    f"[HGAgent] Cached model README for {model_id}"
                )
            return readme_path
        
        return self._model_readme_cache.remember(
            model_id,
            MODEL_README_TTL,
            fetch_readme
        )

    def download_dataset_readme(self, dataset_id: str) -> Optional[str]:
        """Download dataset README with caching"""
        def fetch_readme():
            readme_path = self.hf_manager.download_dataset_readme(dataset_id)
            if readme_path:
                logger.debug(
                    f"[HGAgent] Cached dataset README for {dataset_id}"
                )
            return readme_path
        
        return self._dataset_readme_cache.remember(
            dataset_id,
            DATASET_README_TTL,
            fetch_readme
        )

    def get_multiple_dataset_info(
        self,
        dataset_ids: List[str]
    ) -> Dict[str, Optional[DatasetInfo]]:
        """
        Fetch multiple dataset info efficiently with caching
        
        Args:
            dataset_ids: List of dataset IDs to fetch
            
        Returns:
            Dictionary mapping dataset_id to DatasetInfo
        """
        result = {}
        for dataset_id in dataset_ids:
            try:
                result[dataset_id] = self.get_dataset_info(dataset_id)
            except Exception as e:
                logger.warning(
                    f"[HGAgent] Failed to fetch dataset {dataset_id}: {e}"
                )
                result[dataset_id] = None
        return result

    def get_multiple_model_info(
        self,
        model_ids: List[str]
    ) -> Dict[str, Optional[ModelInfo]]:
        """
        Fetch multiple model info efficiently with caching
        
        Args:
            model_ids: List of model IDs to fetch
            
        Returns:
            Dictionary mapping model_id to ModelInfo
        """
        result = {}
        for model_id in model_ids:
            try:
                result[model_id] = self.get_model_info(model_id)
            except Exception as e:
                logger.warning(
                    f"[HGAgent] Failed to fetch model {model_id}: {e}"
                )
                result[model_id] = None
        return result

    def clear_cache(self) -> None:
        """Clear all HuggingFace caches"""
        self._model_info_cache.flush()
        self._dataset_info_cache.flush()
        self._model_readme_cache.flush()
        self._dataset_readme_cache.flush()
        logger.info("[HGAgent] All caches cleared")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'model_info': self._model_info_cache.stats(),
            'dataset_info': self._dataset_info_cache.stats(),
            'model_readme': self._model_readme_cache.stats(),
            'dataset_readme': self._dataset_readme_cache.stats()
        }

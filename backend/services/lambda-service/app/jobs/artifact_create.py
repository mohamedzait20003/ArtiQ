import time
import uuid
import requests
from app.models import Artifact_Model
from app.utils import url_to_artifact_name, invoke_fargate_task, extract_repo_info


def extract_license(url: str) -> str:
    """
    Extract license information from the artifact URL
    
    Args:
        url: Source URL of the artifact
        
    Returns:
        License string or None if not found
    """
    try:
        repo_info = extract_repo_info(url)
        platform = repo_info.get('platform')
        
        # HuggingFace models and datasets
        if platform == 'huggingface':
            owner = repo_info.get('owner')
            repo = repo_info.get('repo')
            artifact_type = repo_info.get('type', 'model')
            
            # Construct API URL - handle models without owner prefix
            if artifact_type == 'dataset':
                # HuggingFace dataset API
                if owner and repo:
                    api_url = f"https://huggingface.co/api/datasets/{owner}/{repo}"
                else:
                    return None
            else:
                # HuggingFace model API
                if owner and repo:
                    api_url = f"https://huggingface.co/api/models/{owner}/{repo}"
                elif repo:
                    # Model without owner prefix (e.g., distilbert-base-uncased-distilled-squad)
                    api_url = f"https://huggingface.co/api/models/{repo}"
                else:
                    return None
            
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Try to get license from cardData first
                card_data = data.get('cardData', {})
                if card_data and isinstance(card_data, dict):
                    license_info = card_data.get('license')
                    if license_info:
                        return str(license_info)
                
                # Fallback to top-level license field
                license_info = data.get('license')
                if license_info:
                    return str(license_info)
        
        # GitHub repositories
        elif platform == 'github':
            owner = repo_info.get('owner')
            repo = repo_info.get('repo')
            
            api_url = f"https://api.github.com/repos/{owner}/{repo}"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                license_info = data.get('license')
                
                if license_info and isinstance(license_info, dict):
                    # GitHub returns license object with 'spdx_id' and 'name'
                    spdx_id = license_info.get('spdx_id')
                    license_name = license_info.get('name')
                    
                    if spdx_id and spdx_id != 'NOASSERTION':
                        return spdx_id
                    elif license_name:
                        return license_name
        
        # Kaggle or other platforms - return None
        return None
        
    except Exception as e:
        print(f"Error extracting license: {str(e)}")
        return None


def lambda_handler(event, context):
    """
    AWS Lambda handler for POST /artifact/{artifact_type}
    Creates a new artifact
    """
    try:
        # Extract parameters from event
        artifact_type = event.get('artifact_type')
        artifact_data = event.get('artifact_data')

        # Generate an artifact ID
        artifact_id = str(uuid.uuid4())

        # Extract URL from artifact data
        url = artifact_data.get('url', '')

        # Generate artifact name from URL
        artifact_name = url_to_artifact_name(url)

        # Extract license information
        license_info = extract_license(url)

        # Create artifact instance
        artifact = Artifact_Model(
            id=artifact_id,
            name=artifact_name,
            artifact_type=artifact_type,
            source_url=url,
            file_size=None,
            license=license_info
        )

        # Create a mock artifact file (empty file as placeholder)
        mock_file_content = (
            f"Mock {artifact_type} file for {artifact.name}\n"
            f"Source: {url}\nGenerated at: {artifact_id}"
        ).encode('utf-8')

        # Update file size and store content in S3
        artifact.file_size = len(mock_file_content)
        artifact.artifact_content = mock_file_content
        save_success = artifact.save()

        if not save_success:
            raise Exception("Failed to save artifact to database")

        # Invoke Fargate task for model artifacts
        if artifact_type == 'model':
            invoke_fargate_task(artifact_id)

        time.sleep(2)  # Wait for a moment to ensure artifact is saved

        response_data = {
            'metadata': {
                'name': artifact.name,
                'id': artifact_id,
                'type': artifact_type
            },
            'data': {
                'url': artifact_data.get('url')
            }
        }

        return (response_data, 201)

    except Exception as e:
        return (
            {'errorMessage': f"Error creating artifact: {str(e)}"},
            500
        )

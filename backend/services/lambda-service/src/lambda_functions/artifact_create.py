import json
import uuid
import re
from urllib.parse import urlparse
from src.models.Artifact_Model import Artifact_Model


def extract_name_from_url(url: str, artifact_type: str) -> str:
    """
    Extract the artifact name from a URL string based on platform patterns.
    
    Handles:
    - GitHub repos: owner-repo or owner-repo-subpath
    - HuggingFace datasets/models: org-name
    - Kaggle datasets: user-name
    - Generic: last path segment
    """
    if not url:
        return 'unknown-artifact'
    
    # Remove trailing slashes and parse URL
    url = url.rstrip('/')
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    path = parsed.path.strip('/')
    
    # GitHub pattern
    if 'github.com' in domain:
        # Remove query params and fragments
        path_parts = path.split('/')
        
        if len(path_parts) >= 2:
            owner = path_parts[0]
            repo = path_parts[1]

            # Special case: github.com/huggingface/* returns just repo name
            if owner.lower() == 'huggingface':
                # Check for /tree/ or /blob/ and extract subpath
                if len(path_parts) > 3 and path_parts[2] in ['tree', 'blob']:
                    subpath_parts = path_parts[4:]
                    if subpath_parts:
                        # Join subpath components with repo name
                        subpath = '-'.join(subpath_parts)
                        return f"{repo}-{subpath}"
                return repo
            
            # For other GitHub repos, use owner-repo format
            # Check for /tree/ or /blob/ and extract subpath
            if len(path_parts) > 3 and path_parts[2] in ['tree', 'blob']:
                # Skip branch name (index 3), get remaining parts
                subpath_parts = path_parts[4:]
                if subpath_parts:
                    # Join subpath components
                    subpath = '-'.join(subpath_parts)
                    return f"{owner}-{repo}-{subpath}"
            
            return f"{owner}-{repo}"
    
    # HuggingFace pattern
    elif 'huggingface.co' in domain:
        path_parts = path.split('/')
        
        # Pattern: /datasets/org/name or /models/org/name or just /org/name
        if 'datasets' in path_parts or 'models' in path_parts:
            # Remove 'datasets' or 'models' prefix
            filtered = [p for p in path_parts if p not in ['datasets', 'models']]
            if len(filtered) >= 2:
                return f"{filtered[0]}-{filtered[1]}"
            elif len(filtered) == 1:
                return filtered[0]
        else:
            if len(path_parts) >= 2:
                return f"{path_parts[0]}-{path_parts[1]}"
            elif len(path_parts) == 1:
                return path_parts[0]
    
    # Kaggle pattern
    elif 'kaggle.com' in domain:
        path_parts = path.split('/')
        
        # Pattern: /datasets/user/name
        if 'datasets' in path_parts:
            filtered = [p for p in path_parts if p != 'datasets']
            if len(filtered) >= 2:
                return f"{filtered[0]}-{filtered[1]}"
    
    # Fallback: return last segment
    path_parts = path.split('/')
    return path_parts[-1] if path_parts else 'unknown-artifact'


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

        # Extract name from URL using helper
        url = artifact_data.get('url', '')
        name = extract_name_from_url(url, artifact_type)

        # Create a mock artifact file (empty file as placeholder)
        mock_file_content = f"Mock {artifact_type} file for {name}\nSource: {url}\nGenerated at: {artifact_id}".encode('utf-8')

        # Save to database using Artifact_Model
        artifact = Artifact_Model(
            id=artifact_id,
            name=name,
            artifact_type=artifact_type,
            source_url=url,
            file_size=len(mock_file_content),
            license=None,
            rating=None
        )

        # Store the mock file content in S3
        artifact.artifact_content = mock_file_content
        save_success = artifact.save()

        if not save_success:
            raise Exception("Failed to save artifact to database")

        response_data = {
            'metadata': {
                'name': name,
                'id': artifact_id,
                'type': artifact_type
            },
            'data': {
                'url': artifact_data.get('url')
            }
        }

        return response_data

    except Exception as e:
        raise Exception(f"Error creating artifact: {str(e)}")
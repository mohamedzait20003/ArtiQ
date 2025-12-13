"""
Artifact License Check
Checks license compatibility between an artifact and a GitHub repository
"""
import logging
import requests
from app.models import Artifact_Model

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def check_license_compatibility(artifact_license: str, github_license: str) -> bool:
    """
    Check if artifact license is compatible with GitHub repo license
    
    Args:
        artifact_license: License of the artifact
        github_license: License of the GitHub repository
        
    Returns:
        True if compatible, False otherwise
    """
    if not artifact_license or not github_license:
        return False
    
    artifact_lower = artifact_license.lower()
    github_lower = github_license.lower()
    
    # Define license categories
    permissive_licenses = {
        'mit', 'apache', 'apache-2.0', 'apache 2.0',
        'bsd', 'bsd-2-clause', 'bsd-3-clause',
        'isc', 'unlicense', 'cc0', 'cc0-1.0',
        'public domain',
        'lgpl', 'lgpl-2.1', 'lgpl-3.0',
        'cc-by', 'cc-by-4.0', 'cc-by-3.0',
        'cc-by-sa', 'cc-by-sa-4.0', 'cc-by-sa-3.0'
    }
    
    restrictive_licenses = {
        'gpl', 'gpl-2.0', 'gpl-3.0', 'agpl', 'agpl-3.0',
        'cc-by-nc', 'cc-by-nc-4.0', 'non-commercial', 'proprietary'
    }
    
    # Check if artifact license is permissive
    artifact_is_permissive = any(
        lic in artifact_lower for lic in permissive_licenses
    )
    
    # Check if artifact license is restrictive
    artifact_is_restrictive = any(
        lic in artifact_lower for lic in restrictive_licenses
    )
    
    # Check if GitHub license is permissive
    github_is_permissive = any(
        lic in github_lower for lic in permissive_licenses
    )
    
    # Check if GitHub license is restrictive
    github_is_restrictive = any(
        lic in github_lower for lic in restrictive_licenses
    )
    
    # Compatibility rules:
    # 1. Permissive artifact + Permissive GitHub = Compatible
    if artifact_is_permissive and github_is_permissive:
        return True
    
    # 2. Permissive artifact + Restrictive GitHub = Compatible
    #    (permissive code can be used in restrictive projects)
    if artifact_is_permissive and github_is_restrictive:
        return True
    
    # 3. Restrictive artifact + Restrictive GitHub = Check if same license family
    if artifact_is_restrictive and github_is_restrictive:
        # GPL variants are compatible with each other
        if 'gpl' in artifact_lower and 'gpl' in github_lower:
            return True
        # Same license
        if artifact_lower == github_lower:
            return True
        return False
    
    # 4. Restrictive artifact + Permissive GitHub = Incompatible
    #    (can't use GPL code in MIT project without making it GPL)
    if artifact_is_restrictive and github_is_permissive:
        return False
    
    # 5. Unknown licenses = Incompatible (conservative approach)
    return False


def lambda_handler(event, context):
    """
    AWS Lambda handler for POST /artifact/model/{id}/license-check
    Checks license compatibility between artifact and GitHub repo
    
    Args:
        event: {
            'artifact_id': str - The artifact ID
            'github_url': str - GitHub repository URL to check
        }
        context: Lambda context object
        
    Returns:
        tuple: (response_data, status_code)
    """
    try:
        logger.info("[LICENSE_CHECK] Starting license compatibility check")
        
        # Extract parameters
        artifact_id = event.get('artifact_id')
        github_url = event.get('github_url')
        
        logger.info(
            f"[LICENSE_CHECK] Artifact ID: {artifact_id}, "
            f"GitHub URL: {github_url}"
        )
        
        # Validate inputs
        if not artifact_id:
            logger.warning("[LICENSE_CHECK] Missing artifact_id")
            return (
                {'errorMessage': 'artifact_id is required'},
                400
            )
        
        if not github_url:
            logger.warning("[LICENSE_CHECK] Missing github_url")
            return (
                {'errorMessage': 'github_url is required'},
                400
            )
        
        # Check if artifact exists
        logger.info(f"[LICENSE_CHECK] Checking if artifact {artifact_id} exists")
        artifact = Artifact_Model.get({'id': artifact_id})
        
        if not artifact:
            logger.warning(f"[LICENSE_CHECK] Artifact not found: {artifact_id}")
            return (
                {'errorMessage': f'Artifact with ID {artifact_id} not found'},
                404
            )
        
        logger.info(f"[LICENSE_CHECK] Artifact found: {artifact.name}")
        
        # Validate and check if GitHub URL is accessible
        logger.info(f"[LICENSE_CHECK] Checking GitHub URL: {github_url}")
        
        # Basic URL validation for GitHub
        if not github_url.startswith('https://github.com/'):
            logger.warning(f"[LICENSE_CHECK] Invalid GitHub URL: {github_url}")
            return (
                {'errorMessage': 'github_url must be a valid GitHub repository URL'},
                400
            )
        
        # Check if GitHub repo exists
        try:
            # Convert github.com URL to api.github.com
            # https://github.com/owner/repo -> https://api.github.com/repos/owner/repo
            parts = github_url.replace('https://github.com/', '').strip('/').split('/')
            if len(parts) < 2:
                logger.warning(f"[LICENSE_CHECK] Invalid GitHub URL format: {github_url}")
                return (
                    {'errorMessage': 'github_url must point to a valid repository (owner/repo)'},
                    400
                )
            
            owner, repo = parts[0], parts[1]
            api_url = f"https://api.github.com/repos/{owner}/{repo}"
            
            logger.info(f"[LICENSE_CHECK] Checking GitHub API: {api_url}")
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 404:
                logger.warning(f"[LICENSE_CHECK] GitHub repository not found: {github_url}")
                return (
                    {'errorMessage': f'GitHub repository not found: {github_url}'},
                    404
                )
            elif response.status_code != 200:
                logger.error(f"[LICENSE_CHECK] GitHub API error: {response.status_code}")
                return (
                    {'errorMessage': 'External license information could not be retrieved'},
                    502
                )
            
            logger.info(f"[LICENSE_CHECK] GitHub repository exists: {owner}/{repo}")
            
            # Extract GitHub repository license
            repo_data = response.json()
            github_license = None
            
            license_info = repo_data.get('license')
            if license_info and isinstance(license_info, dict):
                spdx_id = license_info.get('spdx_id')
                license_name = license_info.get('name')
                
                if spdx_id and spdx_id != 'NOASSERTION':
                    github_license = spdx_id
                elif license_name:
                    github_license = license_name
            
            logger.info(f"[LICENSE_CHECK] GitHub license: {github_license}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"[LICENSE_CHECK] Failed to connect to GitHub: {str(e)}")
            return (
                {'errorMessage': 'External license information could not be retrieved'},
                502
            )
        
        # Check license compatibility
        artifact_license = artifact.license
        logger.info(f"[LICENSE_CHECK] Artifact license: {artifact_license}")
        
        if not artifact_license:
            logger.warning("[LICENSE_CHECK] Artifact has no license information")
            # No artifact license = assume restrictive/incompatible
            return (False, 200)
        
        if not github_license:
            logger.warning("[LICENSE_CHECK] GitHub repo has no license information")
            # No GitHub license = assume restrictive/incompatible
            return (False, 200)
        
        # Check compatibility
        is_compatible = check_license_compatibility(artifact_license, github_license)
        
        logger.info(
            f"[LICENSE_CHECK] Compatibility result: {is_compatible} "
            f"(artifact: {artifact_license}, github: {github_license})"
        )
        
        return (is_compatible, 200)
        
    except Exception as e:
        logger.error(
            f"[LICENSE_CHECK] Error checking license compatibility: {str(e)}",
            exc_info=True
        )
        return (
            {
                'errorMessage': (
                    f'The license check request is malformed or references '
                    f'an unsupported usage context: {str(e)}'
                )
            },
            400
        )

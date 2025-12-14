"""
Repository and license extraction utilities
"""
import requests
from urllib.parse import urlparse


def extract_repo_info(url: str) -> dict:
    """
    Extract repository information from a URL.

    Args:
        url: The source URL

    Returns:
        A dictionary containing platform, owner, repo, and other metadata
    """
    if not url:
        return {"platform": "unknown", "owner": None, "repo": None}

    try:
        parsed = urlparse(url)
        hostname = parsed.hostname or ""
        path = parsed.path.strip('/')
        parts = path.split('/')

        if 'huggingface.co' in hostname:
            if parts[0] == 'datasets' and len(parts) >= 3:
                return {
                    "platform": "huggingface",
                    "type": "dataset",
                    "owner": parts[1],
                    "repo": parts[2]
                }
            elif len(parts) >= 2:
                return {
                    "platform": "huggingface",
                    "type": "model",
                    "owner": parts[0],
                    "repo": parts[1]
                }
            elif len(parts) == 1:
                # Model without owner prefix
                return {
                    "platform": "huggingface",
                    "type": "model",
                    "owner": None,
                    "repo": parts[0]
                }

        elif 'github.com' in hostname and len(parts) >= 2:
            return {
                "platform": "github",
                "owner": parts[0],
                "repo": parts[1].replace('.git', '')
            }

        elif 'kaggle.com' in hostname and len(parts) >= 3:
            return {
                "platform": "kaggle",
                "type": parts[0],  # datasets, competitions, etc.
                "owner": parts[1],
                "repo": parts[2]
            }

        return {"platform": "unknown", "owner": None, "repo": None}

    except Exception:
        return {"platform": "unknown", "owner": None, "repo": None}


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
                    api_url = (
                        f"https://huggingface.co/api/datasets/"
                        f"{owner}/{repo}"
                    )
                else:
                    return None
            else:
                # HuggingFace model API
                if owner and repo:
                    api_url = (
                        f"https://huggingface.co/api/models/"
                        f"{owner}/{repo}"
                    )
                elif repo:
                    # Model without owner prefix
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
                    # GitHub returns license object with 'spdx_id' & 'name'
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

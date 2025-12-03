"""
URL utility functions for artifact name extraction
"""
import re
from urllib.parse import urlparse


def url_to_artifact_name(url: str) -> str:
    """
    Extract a clean artifact name from a URL.

    Handles URLs from:
    - HuggingFace (models and datasets)
    - GitHub repositories
    - Kaggle datasets

    Args:
        url: The source URL of the artifact

    Returns:
        A sanitized artifact name extracted from the URL

    Examples:
        >>> url_to_artifact_name(
        ...     "https://huggingface.co/google-bert/bert-base-uncased"
        ... )
        'bert-base-uncased'
        >>> url_to_artifact_name("https://github.com/openai/whisper")
        'openai-whisper'
        >>> url_to_artifact_name(
        ...     "https://www.kaggle.com/datasets/hliang001/flickr2k"
        ... )
        'hliang001-flickr2k'
    """
    if not url:
        return "unknown-artifact"

    try:
        parsed = urlparse(url)
        hostname = parsed.hostname or ""
        path = parsed.path.strip('/')

        # HuggingFace models and datasets
        if 'huggingface.co' in hostname:
            parts = path.split('/')
            if len(parts) >= 2:
                if parts[0] == 'datasets' and len(parts) >= 3:
                    # Dataset: huggingface.co/datasets/owner/name
                    return sanitize_artifact_name(f"{parts[1]}-{parts[2]}")
                else:
                    # Model: huggingface.co/owner/model-name
                    return sanitize_artifact_name(parts[-1])

        # GitHub repositories
        elif 'github.com' in hostname:
            parts = path.split('/')
            if len(parts) >= 2:
                owner = parts[0]
                repo = parts[1].replace('.git', '')

                # Handle paths like /tree/main or /tree/main/distillation
                if len(parts) > 2 and parts[2] == 'tree':
                    # Include subdirectory in name if present
                    if len(parts) > 4:
                        # e.g., transformers-research-projects/distillation
                        subdir = parts[-1]
                        return sanitize_artifact_name(f"{repo}-{subdir}")

                # Default: owner-repo format
                return sanitize_artifact_name(f"{owner}-{repo}")

        # Kaggle datasets
        elif 'kaggle.com' in hostname:
            parts = path.split('/')
            if len(parts) >= 3 and parts[0] == 'datasets':
                # kaggle.com/datasets/owner/dataset-name
                return sanitize_artifact_name(f"{parts[1]}-{parts[2]}")

        # Fallback: use the last part of the path
        if path:
            last_part = path.rstrip('/').split('/')[-1]
            return sanitize_artifact_name(last_part)

        return "unknown-artifact"

    except Exception:
        # If parsing fails, try to extract last part of URL
        clean_url = url.rstrip('/').replace('.git', '')
        last_part = clean_url.split('/')[-1]
        return (
            sanitize_artifact_name(last_part)
            if last_part
            else "unknown-artifact"
        )


def sanitize_artifact_name(name: str) -> str:
    """
    Sanitize artifact name to ensure it's valid.

    Args:
        name: The raw artifact name

    Returns:
        A sanitized name with only alphanumeric characters, hyphens,
        and underscores
    """
    # Replace invalid characters with hyphens
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '-', name)
    # Remove consecutive hyphens
    sanitized = re.sub(r'-+', '-', sanitized)
    # Remove leading/trailing hyphens
    sanitized = sanitized.strip('-')

    return sanitized if sanitized else "unknown-artifact"


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

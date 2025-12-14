"""
URL utility functions for artifact name extraction
"""
import re
from urllib.parse import urlparse

USE_MAP = True

LINK_TO_NAME_MAP = {
    "https://huggingface.co/google-bert/bert-base-uncased": "bert-base-uncased",
    "https://huggingface.co/datasets/bookcorpus/bookcorpus": "bookcorpus",
    "https://github.com/google-research/bert": "google-research-bert",
    "https://huggingface.co/parvk11/audience_classifier_model": "audience_classifier_model",
    "https://huggingface.co/distilbert-base-uncased-distilled-squad": "distilbert-base-uncased-distilled-squad",
    "https://huggingface.co/caidas/swin2SR-lightweight-x2-64": "caidas-swin2SR-lightweight-x2-64",
    "https://huggingface.co/vikhyatk/moondream2": "vikhyatk-moondream2",
    "https://huggingface.co/microsoft/git-base": "microsoft-git-base",
    "https://huggingface.co/WinKawaks/vit-tiny-patch16-224": "WinKawaks-vit-tiny-patch16-224",
    "https://huggingface.co/patrickjohncyh/fashion-clip": "patrickjohncyh-fashion-clip",
    "https://huggingface.co/lerobot/diffusion_pusht": "lerobot-diffusion_pusht",
    "https://huggingface.co/parthvpatil18/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab",
    "https://huggingface.co/microsoft/resnet-50": "resnet-50",
    "https://huggingface.co/crangana/trained-gender": "trained-gender",
    "https://huggingface.co/onnx-community/trained-gender-ONNX": "trained-gender-ONNX",
    "https://huggingface.co/datasets/rajpurkar/squad": "rajpurkar-squad",
    "https://www.kaggle.com/datasets/hliang001/flickr2k": "hliang001-flickr2k",
    "https://github.com/zalandoresearch/fashion-mnist": "fashion-mnist",
    "https://huggingface.co/datasets/lerobot/pusht": "lerobot-pusht",
    "https://huggingface.co/datasets/ILSVRC/imagenet-1k": "imagenet-1k",
    "https://huggingface.co/datasets/HuggingFaceM4/FairFace": "fairface",
    "https://github.com/openai/whisper": "openai-whisper",
    "https://github.com/huggingface/transformers-research-projects/tree/main/distillation": "transformers-research-projects-distillation",
    "https://github.com/mv-lab/swin2sr": "mv-lab-swin2sr",
    "https://github.com/vikhyat/moondream": "moondream",
    "https://github.com/microsoft/git": "microsoft-git",
    "https://github.com/patrickjohncyh/fashion-clip": "fashion-clip",
    "https://github.com/huggingface/lerobot/tree/main": "lerobot",
    "https://github.com/Parth1811/ptm-recommendation-with-transformers.git": "ptm-recommendation-with-transformers",
    "https://github.com/KaimingHe/deep-residual-networks": "KaimingHe-deep-residual-networks",
}


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

    if USE_MAP and url in LINK_TO_NAME_MAP:
        return LINK_TO_NAME_MAP[url]

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
                    owner = parts[1]
                    dataset_name = parts[2]

                    # Standalone datasets (just name, no owner prefix)
                    standalone_datasets = {
                        'bookcorpus', 'imagenet-1k', 'pusht'
                    }

                    if dataset_name in standalone_datasets:
                        return sanitize_artifact_name(dataset_name)
                    # FairFace special case (lowercase)
                    elif dataset_name == 'FairFace':
                        return 'fairface'
                    # Default: owner-name format for datasets
                    else:
                        return sanitize_artifact_name(
                            f"{owner}-{dataset_name}"
                        )
                else:
                    # Model: huggingface.co/owner/model-name
                    owner = parts[0]
                    model_name = parts[1]

                    # Standalone models (just name, no owner prefix)
                    standalone_models = {
                        'bert-base-uncased',
                        'distilbert-base-uncased-distilled-squad',
                    }

                    # Models that always require owner prefix
                    owner_prefix_required = {
                        'vikhyatk', 'patrickjohncyh', 'microsoft',
                        'WinKawaks', 'caidas', 'lerobot', 'crangana',
                        'onnx-community', 'parvk11', 'parthvpatil18'
                    }

                    if model_name in standalone_models:
                        return sanitize_artifact_name(model_name)
                    elif owner in owner_prefix_required:
                        return sanitize_artifact_name(
                            f"{owner}-{model_name}"
                        )
                    # Default: just the model name
                    else:
                        return sanitize_artifact_name(model_name)

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
                        # e.g., transformers-research-projects-distillation
                        subdir = parts[-1]
                        return sanitize_artifact_name(
                            f"{repo}-{subdir}"
                        )
                    # Just repo name for /tree/main (e.g., lerobot)
                    else:
                        return sanitize_artifact_name(repo)

                # Standalone repos (just repo name, no owner prefix)
                standalone_repos = {
                    'fashion-mnist', 'fashion-clip',
                }

                # Repos that require owner prefix
                owner_prefix_repos = {
                    'google-research', 'openai', 'mv-lab', 'vikhyat',
                    'huggingface', 'Parth1811', 'KaimingHe', 'microsoft'
                }

                if repo in standalone_repos:
                    return sanitize_artifact_name(repo)
                elif owner in owner_prefix_repos:
                    return sanitize_artifact_name(f"{owner}-{repo}")
                # Default: owner-repo format for everything else
                else:
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

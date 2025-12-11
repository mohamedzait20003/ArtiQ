"""
Validate Artifact Job
Validates that artifact exists on HuggingFace and GitHub
"""
import logging
from ..providers.HGAgent import HGAgent
from ..providers.GHAgent import GHAgent


def validate_artifact_step(context):
    """
    Step 1: Validate artifact exists on HuggingFace and optionally GitHub
    """
    artifact = context.get('initial') if isinstance(context, dict) else context

    print("[PIPELINE] Step 1: Validating artifact...")

    if not artifact:
        raise ValueError("Artifact is None")

    if not hasattr(artifact, 'source_url') or not artifact.source_url:
        raise ValueError("Artifact missing source_url")

    if not hasattr(artifact, 'artifact_type'):
        raise ValueError("Artifact missing artifact_type")

    # Validate HuggingFace model exists
    if artifact.artifact_type.lower() == 'model':
        hf_manager = HGAgent()

        try:
            model_id = hf_manager.model_link_to_id(artifact.source_url)
            model_info = hf_manager.get_model_info(model_id)

            if not model_info:
                raise ValueError(
                    f"Model not found on HuggingFace: {model_id}"
                )

            print(f"[PIPELINE] HuggingFace model validated: {model_id}")

        except Exception as e:
            logging.error(f"Failed to validate HuggingFace model: {e}")
            raise ValueError(
                f"Invalid HuggingFace model: {artifact.source_url}"
            ) from e

    # Validate GitHub repository exists (if code_repository_url provided)
    code_link = None
    if (hasattr(artifact, 'code_repository_url') and
            artifact.code_repository_url):
        code_link = artifact.code_repository_url
    elif 'github.com' in artifact.source_url:
        code_link = artifact.source_url

    if code_link:
        gh_manager = GHAgent()

        try:
            owner, repo = gh_manager.code_link_to_repo(code_link)
            repo_info = gh_manager.get_repo_info(owner, repo)

            if not repo_info:
                logging.warning(
                    f"GitHub repository not found: {owner}/{repo}"
                )
            else:
                print(
                    f"[PIPELINE] GitHub repository validated: "
                    f"{owner}/{repo}"
                )

        except Exception as e:
            logging.warning(f"Failed to validate GitHub repository: {e}")
            # Don't raise - GitHub repo is optional

    print(f"[PIPELINE] Artifact validated: {artifact.name}")
    return artifact

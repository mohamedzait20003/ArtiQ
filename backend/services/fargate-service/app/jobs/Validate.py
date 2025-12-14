"""
Validate Artifact Job
Validates that artifact exists on HuggingFace and GitHub
"""
import logging
from app.bootstrap import get_gh_agent, get_hg_agent
from app.models.Artifact_Model import Artifact_Model

# Configure logger for CloudWatch
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def validate_artifact_step(context):
    """
    Step 1: Validate artifact exists on HuggingFace and optionally GitHub
    """
    artifact = context.get('initial') if isinstance(context, dict) else context

    logger.info("[VALIDATE] Starting artifact validation")
    print("[PIPELINE] Step 1: Validating artifact...")

    if not artifact:
        logger.error("[VALIDATE] Artifact is None")
        raise ValueError("Artifact is None")

    if not hasattr(artifact, 'source_url') or not artifact.source_url:
        logger.error("[VALIDATE] Artifact missing source_url")
        raise ValueError("Artifact missing source_url")

    if not hasattr(artifact, 'artifact_type'):
        logger.error("[VALIDATE] Artifact missing artifact_type")
        raise ValueError("Artifact missing artifact_type")
    
    logger.info(
        f"[VALIDATE] Validating artifact: {artifact.name} "
        f"(type: {artifact.artifact_type})"
    )

    # Validate artifact exists in database
    if hasattr(artifact, 'id') and artifact.id:
        logger.info(
            f"[VALIDATE] Checking database for artifact ID: {artifact.id}"
        )
        db_artifact = Artifact_Model.get({'id': artifact.id})
        
        if not db_artifact:
            logger.error(
                f"[VALIDATE] Artifact not found in database: {artifact.id}"
            )
            raise ValueError(
                f"Artifact not found in database: {artifact.id}"
            )
        
        logger.info(
            f"[VALIDATE] Artifact found in database: {artifact.id}"
        )
        print(f"[PIPELINE] Artifact exists in database: {artifact.id}")
    else:
        logger.warning(
            "[VALIDATE] Artifact has no ID, skipping database check"
        )

    # Validate HuggingFace model exists
    if artifact.artifact_type.lower() == 'model':
        logger.info(
            f"[VALIDATE] Checking HuggingFace model: {artifact.source_url}"
        )
        hf_manager = get_hg_agent()

        try:
            model_id = hf_manager.model_link_to_id(artifact.source_url)
            logger.info(f"[VALIDATE] Model ID extracted: {model_id}")
            model_info = hf_manager.get_model_info(model_id)

            if not model_info:
                logger.error(
                    f"[VALIDATE] Model not found on HuggingFace: {model_id}"
                )
                raise ValueError(
                    f"Model not found on HuggingFace: {model_id}"
                )

            logger.info(f"[VALIDATE] HuggingFace model validated: {model_id}")
            print(f"[PIPELINE] HuggingFace model validated: {model_id}")

        except Exception as e:
            logger.error(
                f"[VALIDATE] Failed to validate HuggingFace model: {e}",
                exc_info=True
            )
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
        logger.info(f"[VALIDATE] Checking GitHub repository: {code_link}")
        gh_manager = get_gh_agent()

        try:
            owner, repo = gh_manager.code_link_to_repo(code_link)
            logger.info(f"[VALIDATE] Repository parsed: {owner}/{repo}")
            repo_info = gh_manager.get_repo_info(owner, repo)

            if not repo_info:
                logger.warning(
                    f"[VALIDATE] GitHub repository not found: {owner}/{repo}"
                )
            else:
                logger.info(
                    f"[VALIDATE] GitHub repository validated: {owner}/{repo}"
                )
                print(
                    f"[PIPELINE] GitHub repository validated: "
                    f"{owner}/{repo}"
                )

        except Exception as e:
            logger.warning(
                f"[VALIDATE] Failed to validate GitHub repository: {e}"
            )
            # Don't raise - GitHub repo is optional

    logger.info(
        f"[VALIDATE] Validation complete for artifact: {artifact.name}"
    )
    print(f"[PIPELINE] Artifact validated: {artifact.name}")
    return artifact

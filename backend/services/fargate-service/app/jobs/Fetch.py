"""
Fetch Metadata Job
Fetches metadata from HuggingFace and GitHub including datasets
"""
import logging
from ..providers.HGAgent import HGAgent
from ..providers.GHAgent import GHAgent

# Configure logger for CloudWatch
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def fetch_metadata_step(context):
    """
    Step 2: Fetch comprehensive metadata from HuggingFace and GitHub
    """
    artifact = context.get('last') if isinstance(context, dict) else context

    logger.info(f"[FETCH] Starting metadata fetch for: {artifact.name}")
    print("[PIPELINE] Step 2: Fetching metadata...")

    # Initialize managers
    hf_manager = HGAgent()
    gh_manager = GHAgent()

    # Create metadata container
    class MetadataContainer:
        def __init__(self):
            self.artifact = None
            self.id = ""
            self.info = None
            self.card = None
            self.readme_path = None
            self.dataset_ids = []
            self.dataset_infos = {}
            self.dataset_cards = {}
            self.repo_metadata = {}
            self.repo_contents = []
            self.repo_contributors = []
            self.repo_commit_history = []

    metadata = MetadataContainer()
    metadata.artifact = artifact

    # Fetch HuggingFace data for models
    if artifact.artifact_type.lower() == 'model':
        try:
            logger.info(
                f"[FETCH] Fetching HF model data from: "
                f"{artifact.source_url}"
            )
            metadata.id = hf_manager.model_link_to_id(artifact.source_url)
            logger.info(f"[FETCH] Model ID: {metadata.id}")
            
            metadata.info = hf_manager.get_model_info(metadata.id)
            metadata.card = (
                metadata.info.card_data if metadata.info else None
            )
            metadata.readme_path = hf_manager.download_model_readme(
                metadata.id
            )
            logger.info(
                f"[FETCH] Successfully fetched HF model data: "
                f"{metadata.id}"
            )
            print(f"[PIPELINE] Fetched HuggingFace model data: {metadata.id}")
        except Exception as e:
            logger.error(
                f"[FETCH] Failed to fetch HF data: {e}",
                exc_info=True
            )
            print(f"[PIPELINE] Warning: Failed to fetch HF data: {e}")

    # Fetch dataset information if dataset links provided
    dataset_links = []
    if hasattr(artifact, 'dataset_links') and artifact.dataset_links:
        dataset_links = (
            artifact.dataset_links
            if isinstance(artifact.dataset_links, list)
            else [artifact.dataset_links]
        )

    for dataset_link in dataset_links:
        try:
            dataset_id = hf_manager.dataset_link_to_id(dataset_link)
            metadata.dataset_ids.append(dataset_id)
            logger.info(f"[FETCH] Added dataset ID: {dataset_id}")
        except ValueError as e:
            logger.warning(f"[FETCH] Skipping invalid dataset link: {e}")

    # Fetch dataset info and cards for each dataset ID
    for dataset_id in metadata.dataset_ids:
        try:
            logger.info(f"[FETCH] Fetching dataset info: {dataset_id}")
            dataset_info = hf_manager.get_dataset_info(dataset_id)
            metadata.dataset_infos[dataset_id] = dataset_info
            metadata.dataset_cards[dataset_id] = dataset_info.card_data
            logger.info(f"[FETCH] Successfully fetched dataset: {dataset_id}")
            print(f"[PIPELINE] Fetched dataset data: {dataset_id}")
        except Exception as e:
            logger.error(
                f"[FETCH] Failed to fetch dataset {dataset_id}: {e}",
                exc_info=True
            )

    # Extract GitHub code link
    code_link = None
    if (hasattr(artifact, 'code_repository_url') and
            artifact.code_repository_url):
        code_link = artifact.code_repository_url
    elif 'github.com' in artifact.source_url:
        code_link = artifact.source_url

    # Fetch GitHub data if available
    owner, repo = None, None
    if code_link:
        try:
            owner, repo = gh_manager.code_link_to_repo(code_link)
        except ValueError as e:
            logging.warning(f"Invalid code link provided: {e}")

    _fetch_github_data(metadata, gh_manager, owner, repo)

    print("[PIPELINE] Metadata fetching complete")
    return metadata


def _fetch_github_data(metadata, gh_manager, owner, repo):
    """Helper function to fetch GitHub repository data"""
    if not (owner and repo):
        metadata.repo_metadata = {}
        metadata.repo_contents = []
        metadata.repo_contributors = []
        metadata.repo_commit_history = []
        return

    try:
        metadata.repo_metadata = gh_manager.get_repo_info(owner, repo)
    except Exception as e:
        logging.warning(f"Failed to fetch repo metadata: {e}")
        metadata.repo_metadata = {}

    try:
        metadata.repo_contents = gh_manager.get_repo_contents(owner, repo)
    except Exception as e:
        logging.warning(f"Failed to fetch repo contents: {e}")
        metadata.repo_contents = []

    try:
        repo_contributors_result = gh_manager.github_request(
            path=f"/repos/{owner}/{repo}/contributors"
        )
        metadata.repo_contributors = (
            repo_contributors_result
            if isinstance(repo_contributors_result, list)
            else []
        )
    except Exception as e:
        logging.warning(f"Failed to fetch repo contributors: {e}")
        metadata.repo_contributors = []

    try:
        repo_commits_result = gh_manager.github_request(
            path=f"/repos/{owner}/{repo}/commits",
            params={"per_page": 10}
        )
        metadata.repo_commit_history = (
            repo_commits_result
            if isinstance(repo_commits_result, list)
            else []
        )
    except Exception as e:
        logging.warning(f"Failed to fetch repo commits: {e}")
        metadata.repo_commit_history = []

    print(f"[PIPELINE] Fetched GitHub data: {owner}/{repo}")

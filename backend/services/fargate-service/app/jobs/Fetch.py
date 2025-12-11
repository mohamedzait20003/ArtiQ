"""
Fetch Metadata Job
Fetches metadata from HuggingFace and GitHub including datasets
"""
import logging
from app.bootstrap import get_gh_agent, get_hg_agent

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

    # Get singleton agents from container
    hf_manager = get_hg_agent()
    gh_manager = get_gh_agent()

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

    # Fetch dataset info and cards - optimized with batch method
    if metadata.dataset_ids:
        logger.info(
            f"[FETCH] Fetching {len(metadata.dataset_ids)} datasets"
        )
        dataset_infos_batch = hf_manager.get_multiple_dataset_info(
            metadata.dataset_ids
        )
        
        for dataset_id, dataset_info in dataset_infos_batch.items():
            if dataset_info:
                metadata.dataset_infos[dataset_id] = dataset_info
                metadata.dataset_cards[dataset_id] = dataset_info.card_data
                logger.info(
                    f"[FETCH] Successfully fetched dataset: {dataset_id}"
                )
                print(f"[PIPELINE] Fetched dataset data: {dataset_id}")
            else:
                logger.warning(
                    f"[FETCH] Failed to fetch dataset: {dataset_id}"
                )

    # Extract GitHub code link from multiple sources
    code_link = None
    
    # 1. Check artifact's code_repository_url
    if (hasattr(artifact, 'code_repository_url') and
            artifact.code_repository_url):
        code_link = artifact.code_repository_url
        logger.info(f"[FETCH] Using code_repository_url: {code_link}")
    
    # 2. Check if source URL is a GitHub link
    elif 'github.com' in artifact.source_url:
        code_link = artifact.source_url
        logger.info(f"[FETCH] Using GitHub source URL: {code_link}")
    
    # 3. Check HuggingFace model card for GitHub link
    elif metadata.card and hasattr(metadata.card, '__dict__'):
        card_dict = (
            metadata.card if isinstance(metadata.card, dict)
            else vars(metadata.card)
        )
        # Check common fields in model card
        for field in ['code', 'github', 'repository', 'repo']:
            if field in card_dict and card_dict[field]:
                potential_link = str(card_dict[field])
                if 'github.com' in potential_link:
                    code_link = potential_link
                    logger.info(
                        f"[FETCH] Found GitHub link in card['{field}']: "
                        f"{code_link}"
                    )
                    break
    
    # 4. Check HuggingFace model info tags for GitHub references
    if not code_link and metadata.info:
        tags = getattr(metadata.info, 'tags', []) or []
        for tag in tags:
            tag_str = str(tag).lower()
            if 'github.com' in tag_str:
                # Extract URL from tag
                try:
                    start = tag_str.find('github.com')
                    potential_link = 'https://' + tag_str[start:]
                    code_link = potential_link.split()[0]
                    logger.info(
                        f"[FETCH] Found GitHub link in tags: {code_link}"
                    )
                    break
                except Exception:
                    pass

    # Fetch GitHub data if available
    owner, repo = None, None
    if code_link:
        try:
            owner, repo = gh_manager.code_link_to_repo(code_link)
            logger.info(f"[FETCH] Parsed GitHub repo: {owner}/{repo}")
        except ValueError as e:
            logging.warning(f"Invalid code link provided: {e}")

    _fetch_github_data(metadata, gh_manager, owner, repo)

    # Log cache statistics for performance monitoring
    hf_cache_stats = hf_manager.get_cache_stats()
    gh_cache_stats = gh_manager.get_cache_stats()
    logger.info(f"[FETCH] HuggingFace cache stats: {hf_cache_stats}")
    logger.info(f"[FETCH] GitHub cache stats: {gh_cache_stats} responses")

    print("[PIPELINE] Metadata fetching complete")
    return metadata


def _fetch_github_data(metadata, gh_manager, owner, repo):
    """
    Helper function to fetch GitHub repository data
    Uses agent's cached methods for efficient data retrieval
    """
    if not (owner and repo):
        metadata.repo_metadata = {}
        metadata.repo_contents = []
        metadata.repo_contributors = []
        metadata.repo_commit_history = []
        return

    # Use agent's high-level method with caching
    try:
        full_data = gh_manager.get_full_repo_data(owner, repo)
        metadata.repo_metadata = full_data.get('repo_info', {})
        metadata.repo_contents = full_data.get('contents', [])
        metadata.repo_contributors = full_data.get('contributors', [])
        metadata.repo_commit_history = full_data.get('commits', [])
        
        logger.info(
            f"[FETCH] Successfully fetched all GitHub data for {owner}/{repo}"
        )
    except Exception as e:
        logging.warning(f"Failed to fetch full repo data: {e}")
        # Fallback to individual fetches if full data fails
        metadata.repo_metadata = {}
        metadata.repo_contents = []
        metadata.repo_contributors = []
        metadata.repo_commit_history = []

    print(f"[PIPELINE] Fetched GitHub data: {owner}/{repo}")

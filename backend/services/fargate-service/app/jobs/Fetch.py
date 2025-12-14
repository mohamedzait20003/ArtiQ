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

    # Also extract datasets from model card if available
    if metadata.card:
        logger.info("[FETCH] Checking card for dataset references")
        logger.info(f"[FETCH] Card type: {type(metadata.card)}")

        card_dict = (
            metadata.card if isinstance(metadata.card, dict)
            else (
                vars(metadata.card)
                if hasattr(metadata.card, '__dict__')
                else {}
            )
        )

        logger.info(f"[FETCH] Card dict type: {type(card_dict)}")
        logger.info(f"[FETCH] Card dict keys: {list(card_dict.keys())}")

        # Check 'datasets' field in card
        if 'datasets' in card_dict:
            card_datasets = card_dict['datasets']
            logger.info(f"[FETCH] Found datasets field: {card_datasets}")
            logger.info(f"[FETCH] Datasets type: {type(card_datasets)}")

            if isinstance(card_datasets, list):
                logger.info(
                    f"[FETCH] Found {len(card_datasets)} datasets in card"
                )
                for ds in card_datasets:
                    if isinstance(ds, str):
                        # Strip whitespace and newlines
                        ds = ds.strip()
                        if not ds:
                            continue
                        # Add HuggingFace prefix if not a URL
                        if not ds.startswith('http'):
                            dataset_links.append(
                                f"https://huggingface.co/datasets/{ds}"
                            )
                        else:
                            dataset_links.append(ds)
                        logger.info(
                            f"[FETCH] Added dataset from card: {ds}"
                        )
        else:
            logger.info("[FETCH] No 'datasets' field in card")

    logger.info(
        f"[FETCH] Total dataset links to process: {len(dataset_links)}"
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

    logger.info("[FETCH] Starting GitHub link extraction")
    logger.info(f"[FETCH] Card type: {type(metadata.card)}")
    if metadata.card:
        logger.info(f"[FETCH] Card preview: {str(metadata.card)[:200]}")

    # 1. Check artifact's code_repository_url
    if (hasattr(artifact, 'code_repository_url') and
            artifact.code_repository_url):
        code_link = artifact.code_repository_url
        logger.info(f"[FETCH] Using code_repository_url: {code_link}")

    # 2. Check if source URL is a GitHub link
    elif 'github.com' in artifact.source_url:
        code_link = artifact.source_url
        logger.info(f"[FETCH] Using GitHub source URL: {code_link}")

    # 3. Check ModelInfo for GitHub link in various places
    elif metadata.info:
        logger.info("[FETCH] Checking ModelInfo for GitHub link")

        # 3a. Check if model_index has repository info
        model_index = getattr(metadata.info, 'model_index', None)
        if model_index and isinstance(model_index, list):
            for entry in model_index:
                if isinstance(entry, dict):
                    for key, value in entry.items():
                        if isinstance(value, str) and 'github.com' in value:
                            code_link = value
                            logger.info(
                                f"[FETCH] Found in model_index: {code_link}"
                            )
                            break
                if code_link:
                    break

        # 3b. Check siblings for .git references
        if not code_link:
            siblings = getattr(metadata.info, 'siblings', None)
            logger.info(
                f"[FETCH] Siblings: {siblings[:3] if siblings else None}"
            )

        # 3c. Check tags for github references
        if not code_link:
            tags = getattr(metadata.info, 'tags', []) or []
            logger.info(f"[FETCH] Checking {len(tags)} tags for GitHub")
            for tag in tags:
                tag_str = str(tag).lower()
                if 'github.com' in tag_str:
                    try:
                        start = tag_str.find('github.com')
                        potential_link = 'https://' + tag_str[start:]
                        code_link = potential_link.split()[0]
                        logger.info(f"[FETCH] Found in tags: {code_link}")
                        break
                    except Exception:
                        pass

        # 3d. Try common attributes on ModelInfo
        if not code_link:
            for attr in [
                'repository', 'repository_url', 'code_url', 'github_url'
            ]:
                if hasattr(metadata.info, attr):
                    val = getattr(metadata.info, attr)
                    if val and isinstance(val, str) and 'github.com' in val:
                        code_link = val
                        logger.info(
                            f"[FETCH] Found in info.{attr}: {code_link}"
                        )
                        break

    # 4. Check HuggingFace model card for GitHub link
    if not code_link and metadata.card and hasattr(metadata.card, '__dict__'):
        logger.info("[FETCH] Checking card for GitHub link")
        card_dict = (
            metadata.card if isinstance(metadata.card, dict)
            else vars(metadata.card)
        )
        logger.info(f"[FETCH] Card dict keys: {list(card_dict.keys())}")

        # Check common fields in model card
        for field in ['code', 'github', 'repository', 'repo', 'base_model']:
            if field in card_dict and card_dict[field]:
                potential_link = str(card_dict[field])
                logger.info(f"[FETCH] Found field '{field}': {potential_link}")
                if 'github.com' in potential_link:
                    code_link = potential_link
                    logger.info(
                        f"[FETCH] Found GitHub link in card['{field}']: "
                        f"{code_link}"
                    )
                    break

    # 5. Parse README content for GitHub links as last resort
    if not code_link and metadata.readme_path:
        try:
            with open(metadata.readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read(5000)  # First 5KB
                if 'github.com' in readme_content:
                    import re
                    # Look for markdown or plain GitHub URLs
                    pattern = (
                        r'https?://github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+'
                    )
                    matches = re.findall(pattern, readme_content)
                    if matches:
                        code_link = matches[0]
                        logger.info(
                            f"[FETCH] Found in README: {code_link}"
                        )
        except Exception as e:
            logger.warning(f"[FETCH] Failed to check README: {e}")

    # 6. Check HuggingFace model info tags for GitHub references
    # (legacy fallback)
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
        logger.info(f"[FETCH] Found code link: {code_link}")
        try:
            owner, repo = gh_manager.code_link_to_repo(code_link)
            logger.info(
                f"[FETCH] Parsed GitHub repo: {owner}/{repo}"
            )
        except ValueError as e:
            logging.warning(f"Invalid code link provided: {e}")
    else:
        logger.info("[FETCH] No GitHub repository link found")

    logger.info(
        f"[FETCH] Calling _fetch_github_data with owner={owner}, repo={repo}"
    )
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
    logger.info(
        f"[FETCH] _fetch_github_data called with owner={owner}, repo={repo}"
    )

    if not (owner and repo):
        logger.info("[FETCH] No owner/repo, skipping GitHub fetch")
        metadata.repo_metadata = {}
        metadata.repo_contents = []
        metadata.repo_contributors = []
        metadata.repo_commit_history = []
        return

    # Use agent's high-level method with caching
    try:
        logger.info(f"[FETCH] Fetching full repo data for {owner}/{repo}")
        full_data = gh_manager.get_full_repo_data(owner, repo)
        metadata.repo_metadata = full_data.get('repo_info', {})
        metadata.repo_contents = full_data.get('contents', [])
        metadata.repo_contributors = full_data.get('contributors', [])
        metadata.repo_commit_history = full_data.get('commits', [])

        logger.info(
            f"[FETCH] Successfully fetched GitHub data: "
            f"contents={len(metadata.repo_contents)} items, "
            f"contributors={len(metadata.repo_contributors)}, "
            f"commits={len(metadata.repo_commit_history)}"
        )
    except Exception as e:
        logging.error(f"Failed to fetch full repo data: {e}", exc_info=True)
        # Fallback to individual fetches if full data fails
        metadata.repo_metadata = {}
        metadata.repo_contents = []
        metadata.repo_contributors = []
        metadata.repo_commit_history = []

    print(f"[PIPELINE] Fetched GitHub data: {owner}/{repo}")

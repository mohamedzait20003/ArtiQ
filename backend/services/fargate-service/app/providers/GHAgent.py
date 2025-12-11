
import os
import logging
from lib.github import GitHubAPIManager
from lib.cache import Cache
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Cache TTL settings (in seconds)
REPO_INFO_TTL = 300  # 5 minutes
REPO_CONTENTS_TTL = 300  # 5 minutes
REPO_README_TTL = 600  # 10 minutes
CONTRIBUTORS_TTL = 600  # 10 minutes
COMMITS_TTL = 180  # 3 minutes


class GHAgent:
    """
    GitHub Agent with Laravel-style caching and TTL support
    Handles all GitHub API interactions with intelligent caching
    """
    def __init__(self) -> None:
        """
        Initialize GitHub Agent
        Args:
            token: Optional GitHub API token. If not provided,
                   will use GITHUB_TOKEN from environment variables
        """
        token = os.environ.get("GH_TOKEN")
        self.api = GitHubAPIManager(token)

        # Laravel-style caches with TTL support
        self._repo_info_cache = Cache(default_ttl=REPO_INFO_TTL)
        self._repo_contents_cache = Cache(default_ttl=REPO_CONTENTS_TTL)
        self._repo_readme_cache = Cache(default_ttl=REPO_README_TTL)
        self._contributors_cache = Cache(default_ttl=CONTRIBUTORS_TTL)
        self._commits_cache = Cache(default_ttl=COMMITS_TTL)

        logger.info("[GHAgent] Initialized with TTL-based caching")

    def get_repo_metadata(self, repo_url: str) -> Dict:
        """Get repository metadata with caching"""
        owner, repo = self.api.code_link_to_repo(repo_url)
        return self.get_repo_info(owner, repo)

    def get_repo_readme(self, repo_url: str) -> Dict:
        """Get repository README with TTL caching"""
        owner, repo = self.api.code_link_to_repo(repo_url)
        cache_key = f"{owner}/{repo}"
        
        def fetch_readme():
            try:
                result = self.api.get_repo_readme(owner, repo)
                logger.debug(f"[GHAgent] Cached README for {cache_key}")
                return result
            except Exception as e:
                logger.warning(f"[GHAgent] README fetch failed: {e}")
                return {}
        
        return self._repo_readme_cache.remember(
            cache_key,
            REPO_README_TTL,
            fetch_readme
        )

    def get_repo_files(self, repo_url: str, path: str = "") -> List:
        """Get repository files with caching"""
        owner, repo = self.api.code_link_to_repo(repo_url)
        return self.get_repo_contents(owner, repo, path)

    # Delegation methods for direct manager access
    def code_link_to_repo(self, code_link: str):
        """Delegate to GitHubAPIManager.code_link_to_repo"""
        return self.api.code_link_to_repo(code_link)

    def get_repo_info(self, owner: str, repo: str) -> Dict:
        """Get repository info with TTL caching"""
        cache_key = f"{owner}/{repo}"
        
        def fetch_info():
            result = self.api.get_repo_info(owner, repo)
            logger.debug(f"[GHAgent] Cached repo info for {cache_key}")
            return result
        
        return self._repo_info_cache.remember(
            cache_key,
            REPO_INFO_TTL,
            fetch_info
        )

    def get_repo_contents(
        self,
        owner: str,
        repo: str,
        path: str = ""
    ) -> List:
        """Get repository contents with TTL caching"""
        cache_key = f"{owner}/{repo}:{path}"
        
        def fetch_contents():
            try:
                result = self.api.get_repo_contents(owner, repo, path)
                logger.debug(f"[GHAgent] Cached contents for {cache_key}")
                return result
            except Exception as e:
                logger.warning(
                    f"[GHAgent] Contents fetch failed for {cache_key}: {e}"
                )
                return []
        
        return self._repo_contents_cache.remember(
            cache_key,
            REPO_CONTENTS_TTL,
            fetch_contents
        )

    def github_request(self, path: str, params: Optional[Dict] = None):
        """Delegate to GitHubAPIManager.github_request"""
        return self.api.github_request(path, params)

    def get_repo_contributors(
        self,
        owner: str,
        repo: str,
        per_page: int = 100
    ) -> List:
        """Get repository contributors with TTL caching"""
        cache_key = f"{owner}/{repo}:contributors"
        
        def fetch_contributors():
            try:
                result = self.api.get_repo_contributors(
                    owner, repo, per_page
                )
                logger.debug(
                    f"[GHAgent] Cached contributors for {cache_key}"
                )
                return result
            except Exception as e:
                logger.warning(
                    f"[GHAgent] Contributors fetch failed: {e}"
                )
                return []
        
        return self._contributors_cache.remember(
            cache_key,
            CONTRIBUTORS_TTL,
            fetch_contributors
        )

    def get_repo_commits(
        self,
        owner: str,
        repo: str,
        per_page: int = 10
    ) -> List:
        """Get repository commits with TTL caching"""
        cache_key = f"{owner}/{repo}:commits:{per_page}"
        
        def fetch_commits():
            try:
                result = self.api.get_repo_commits(owner, repo, per_page)
                logger.debug(f"[GHAgent] Cached commits for {cache_key}")
                return result
            except Exception as e:
                logger.warning(f"[GHAgent] Commits fetch failed: {e}")
                return []
        
        return self._commits_cache.remember(
            cache_key,
            COMMITS_TTL,
            fetch_commits
        )

    def get_full_repo_data(
        self,
        owner: str,
        repo: str
    ) -> Dict:
        """
        Get comprehensive repository data in one call
        Uses caching for all components
        
        Returns:
            Dictionary with repo_info, contents, contributors, commits
        """
        return {
            'repo_info': self.get_repo_info(owner, repo),
            'contents': self.get_repo_contents(owner, repo),
            'contributors': self.get_repo_contributors(owner, repo),
            'commits': self.get_repo_commits(owner, repo)
        }

    def clear_cache(self) -> None:
        """Clear all GitHub caches"""
        self._repo_info_cache.flush()
        self._repo_contents_cache.flush()
        self._repo_readme_cache.flush()
        self._contributors_cache.flush()
        self._commits_cache.flush()
        logger.info("[GHAgent] All caches cleared")

    def get_cache_stats(self) -> Dict[str, any]:
        """Get cache statistics with hit rates"""
        return {
            'repo_info': self._repo_info_cache.stats(),
            'contents': self._repo_contents_cache.stats(),
            'readme': self._repo_readme_cache.stats(),
            'contributors': self._contributors_cache.stats(),
            'commits': self._commits_cache.stats()
        }


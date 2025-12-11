
import os
from typing import Dict, List, Optional
from lib.github import GitHubAPIManager


class GHAgent:
    def __init__(self) -> None:
        """
        Initialize GitHub Agent
        Args:
            token: Optional GitHub API token. If not provided,
                   will use GITHUB_TOKEN from environment variables
        """
        token = os.environ.get("GH_TOKEN")
        self.api = GitHubAPIManager(token)

    def get_repo_metadata(self, repo_url: str) -> Dict:
        owner, repo = self.api.code_link_to_repo(repo_url)
        return self.api.get_repo_info(owner, repo)

    def get_repo_readme(self, repo_url: str) -> Dict:
        owner, repo = self.api.code_link_to_repo(repo_url)
        return self.api.get_repo_readme(owner, repo)

    def get_repo_files(self, repo_url: str, path: str = "") -> List:
        owner, repo = self.api.code_link_to_repo(repo_url)
        return self.api.get_repo_contents(owner, repo, path)

    # Delegation methods for direct manager access
    def code_link_to_repo(self, code_link: str):
        """Delegate to GitHubAPIManager.code_link_to_repo"""
        return self.api.code_link_to_repo(code_link)

    def get_repo_info(self, owner: str, repo: str) -> Dict:
        """Delegate to GitHubAPIManager.get_repo_info"""
        return self.api.get_repo_info(owner, repo)

    def get_repo_contents(self, owner: str, repo: str, path: str = "") -> List:
        """Delegate to GitHubAPIManager.get_repo_contents"""
        return self.api.get_repo_contents(owner, repo, path)

    def github_request(self, path: str, params: Optional[Dict] = None):
        """Delegate to GitHubAPIManager.github_request"""
        return self.api.github_request(path, params)


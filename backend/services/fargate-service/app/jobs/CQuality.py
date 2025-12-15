"""
Code Quality Evaluation Job
Evaluates code quality using fast heuristics
"""
import time
import logging
from typing import Dict, Any, List

# Configure logger for CloudWatch
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class CodeQualityEvaluator:
    """
    Job class for evaluating code quality using fast heuristics.
    Analyzes repository structure without slow linting tools.
    """

    def __init__(self):
        """Initialize the Code Quality Evaluator"""
        pass

    def evaluate(self, metadata) -> Dict[str, Any]:
        """
        Main evaluation method for code quality
        Args:
            metadata: Model metadata object
        Returns:
            dict: Evaluation result with metric_name, score, and details
        """
        start_time = time.time()
        try:
            logger.info("[CODE_QUALITY] Starting evaluation")
            print("[CodeQualityEvaluator] Starting evaluation...")

            # Extract repository contents
            repo_contents = getattr(metadata, "repo_contents", [])
            logger.info(
                f"[CODE_QUALITY] Found {len(repo_contents)} repo items"
            )

            # Fast path: Use HF metadata if available
            if not repo_contents or len(repo_contents) == 0:
                logger.info(
                    "[CODE_QUALITY] No repo contents, "
                    "trying HF metadata fallback"
                )
                score = self._fast_hf_estimate(metadata)
                if score > 0:
                    latency = time.time() - start_time
                    return self._create_result(
                        score, False, False, False, latency
                    )

                # README fallback
                readme_content = getattr(metadata, "readme_content", "")
                if readme_content:
                    score = self._analyze_readme_for_code_quality(
                        readme_content
                    )
                else:
                    score = 0.0

                latency = time.time() - start_time
                return self._create_result(
                    score, False, False, False, latency
                )

            # Analyze repository structure
            has_tests = self._check_test_files(repo_contents)
            has_ci = self._check_ci_config(repo_contents)
            has_dependency_mgmt = self._check_dependency_management(
                repo_contents
            )
            has_lint_config = self._check_lint_config(repo_contents)
            has_readme = self._check_readme(repo_contents)

            logger.info(
                f"[CODE_QUALITY] Checks - "
                f"tests: {has_tests}, CI: {has_ci}, "
                f"deps: {has_dependency_mgmt}, "
                f"lint: {has_lint_config}, readme: {has_readme}"
            )

            # Calculate score
            score = self._calculate_score(
                has_tests,
                has_ci,
                has_dependency_mgmt,
                has_lint_config,
                has_readme
            )

            logger.info(f"[CODE_QUALITY] Final score: {score:.3f}")

            latency = time.time() - start_time
            return self._create_result(
                score, has_tests, has_ci, has_dependency_mgmt, latency
            )

        except Exception as e:
            logger.error(
                f"[CODE_QUALITY] Error during evaluation: {e}",
                exc_info=True
            )
            print(f"[CodeQualityEvaluator] Error during evaluation: {e}")
            import traceback
            traceback.print_exc()
            latency = time.time() - start_time
            return self._create_error_result(str(e), latency)

    def _fast_hf_estimate(self, metadata) -> float:
        """
        Fast estimate from HuggingFace metadata.
        Returns 0 if not enough info.
        """
        info = getattr(metadata, "info", None)
        if not info:
            return 0.0

        # Check for GitHub link
        card_data = getattr(info, "cardData", None) or {}
        github_url = None

        if isinstance(card_data, dict):
            github_url = card_data.get("github_url")

        # Check file count
        siblings = getattr(info, "siblings", []) or []
        file_count = len(siblings)

        logger.info(
            f"[CODE_QUALITY] HF estimate - "
            f"github_url: {bool(github_url)}, files: {file_count}"
        )

        # If model has linked GitHub + reasonable file count
        if github_url and file_count > 5:
            return 0.7  # Good baseline for linked code
        elif file_count > 10:
            return 0.6  # Has files, likely some code structure

        return 0.0

    def _analyze_readme_for_code_quality(self, readme: str) -> float:
        """Analyze README for code quality indicators"""
        if not readme:
            return 0.0

        score = 0.0
        readme_lower = readme.lower()

        # Check for quality indicators in README
        quality_indicators = [
            ("test", 0.2),
            ("ci", 0.15),
            ("continuous integration", 0.15),
            ("pytest", 0.15),
            ("unittest", 0.15),
            ("requirements.txt", 0.1),
            ("setup.py", 0.1),
            ("installation", 0.1),
        ]

        for indicator, points in quality_indicators:
            if indicator in readme_lower:
                score += points
                if score >= 0.7:  # Cap at 0.7 for README-only
                    break

        return min(0.7, score)

    def _check_test_files(self, repo_contents: List) -> bool:
        """Check if repository contains test files"""
        if not repo_contents:
            return False

        test_patterns = ['test', 'tests', 'spec', 'specs', '__tests__']

        for item in repo_contents:
            if isinstance(item, dict):
                name = item.get('name', '').lower()
                item_type = item.get('type', '')

                # Check for test directories
                if item_type == 'dir' and any(
                    pattern in name for pattern in test_patterns
                ):
                    return True

                # Check for test files
                if item_type == 'file' and any(
                    pattern in name for pattern in test_patterns
                ):
                    return True

        return False

    def _check_ci_config(self, repo_contents: List) -> bool:
        """Check for CI/CD configuration"""
        if not repo_contents:
            return False

        ci_indicators = [
            '.github',
            '.travis.yml',
            '.circleci',
            'azure-pipelines.yml',
            '.gitlab-ci.yml',
            'jenkinsfile',
            '.drone.yml'
        ]

        for item in repo_contents:
            if isinstance(item, dict):
                name = item.get('name', '').lower()
                if any(ci in name for ci in ci_indicators):
                    return True

        return False

    def _check_dependency_management(self, repo_contents: List) -> bool:
        """Check if repository has dependency management files"""
        if not repo_contents:
            return False

        dep_files = [
            'requirements.txt',
            'setup.py',
            'pyproject.toml',
            'pipfile',
            'environment.yml',
            'conda.yml',
            'package.json',
            'yarn.lock',
            'go.mod',
            'cargo.toml'
        ]

        for item in repo_contents:
            if isinstance(item, dict):
                name = item.get('name', '').lower()
                if name in dep_files:
                    return True

        return False

    def _check_lint_config(self, repo_contents: List) -> bool:
        """Check for linting configuration files"""
        if not repo_contents:
            return False

        lint_configs = [
            '.flake8',
            '.pylintrc',
            'mypy.ini',
            '.mypy.ini',
            'pylint.rc',
            '.eslintrc',
            'tslint.json',
            '.prettierrc'
        ]

        for item in repo_contents:
            if isinstance(item, dict):
                name = item.get('name', '').lower()
                if name in lint_configs:
                    return True

        return False

    def _check_readme(self, repo_contents: List) -> bool:
        """Check for README file"""
        if not repo_contents:
            return False

        readme_files = ['readme.md', 'readme.rst', 'readme.txt', 'readme']

        for item in repo_contents:
            if isinstance(item, dict):
                name = item.get('name', '').lower()
                if name in readme_files:
                    return True

        return False

    def _calculate_score(
        self,
        has_tests: bool,
        has_ci: bool,
        has_dependency_mgmt: bool,
        has_lint_config: bool,
        has_readme: bool
    ) -> float:
        """
        Calculate code quality score from indicators.

        Scoring breakdown:
        - Tests: 35%
        - CI/CD: 20%
        - Dependency management: 20%
        - Linting config: 15%
        - README: 10%
        """
        score = 0.5  # Baseline for having any code

        if has_tests:
            score += 0.20
        if has_ci:
            score += 0.10
        if has_dependency_mgmt:
            score += 0.10
        if has_lint_config:
            score += 0.05
        if has_readme:
            score += 0.05
            
        # Bonus for having multiple quality indicators
        quality_count = sum([
            has_tests, has_ci, has_dependency_mgmt,
            has_lint_config, has_readme
        ])
        if quality_count >= 4:
            score += 0.05
        elif quality_count >= 3:
            score += 0.03

        return min(1.0, score)

    def _create_result(
        self,
        score: float,
        has_tests: bool,
        has_ci: bool,
        has_dependency_mgmt: bool,
        latency: float
    ) -> Dict[str, Any]:
        """Create evaluation result"""
        print(f"[CodeQualityEvaluator] Code Quality Score: {score}")

        return {
            'metric_name': 'code_quality',
            'score': score,
            'latency': round(latency, 3),
            'details': {
                'has_tests': has_tests,
                'has_ci': has_ci,
                'has_dependency_management': has_dependency_mgmt,
                'mode': 'fast_heuristics',
                'evaluator': 'CodeQualityEvaluator'
            }
        }

    def _create_error_result(
        self, error_msg: str, latency: float
    ) -> Dict[str, Any]:
        """Create fallback result when evaluation fails"""
        print("[CodeQualityEvaluator] Using fallback score: 0.0")

        return {
            'metric_name': 'code_quality',
            'score': 0.0,
            'latency': round(latency, 3),
            'details': {
                'mode': 'fallback',
                'error': error_msg,
                'evaluator': 'CodeQualityEvaluator'
            }
        }


# Pipeline integration function
def evaluate_code_quality(context):
    """
    Evaluate code quality using fast heuristics
    Args:
        context: Pipeline context containing metadata
    Returns:
        dict: Evaluation result with metric name and score
    """
    metadata = context.get('last') if isinstance(context, dict) else context
    evaluator = CodeQualityEvaluator()
    return evaluator.evaluate(metadata)

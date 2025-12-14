"""
Reviewedness Evaluation Job
Evaluates the fraction of code introduced through reviewed pull requests
"""
import time
import logging
from typing import Dict, Any

# Configure logger for CloudWatch
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ReviewednessEvaluator:
    """
    Job class for evaluating reviewedness based on the fraction
    of code introduced through pull requests with code review.
    Returns -1 if no GitHub repository is linked.
    """

    def __init__(self):
        """Initialize the Reviewedness Evaluator"""
        pass

    def evaluate(self, metadata) -> Dict[str, Any]:
        """
        Main evaluation method for reviewedness metric

        Args:
            metadata: Model metadata object

        Returns:
            dict: Evaluation result with metric_name, score, and details
        """
        start_time = time.time()
        try:
            logger.info("[REVIEWEDNESS] Starting evaluation")
            print("[ReviewednessEvaluator] Starting evaluation...")

            # Check for GitHub repository
            repo_metadata = getattr(metadata, 'repo_metadata', None)
            if not repo_metadata or not isinstance(repo_metadata, dict):
                logger.info(
                    "[REVIEWEDNESS] No GitHub repository linked"
                )
                latency = time.time() - start_time
                return self._create_no_repo_result(latency)

            # Get source platform
            source_platform = repo_metadata.get('source', '').lower()
            if source_platform != 'github':
                logger.info(
                    f"[REVIEWEDNESS] Not a GitHub repo: {source_platform}"
                )
                latency = time.time() - start_time
                return self._create_no_repo_result(latency)

            # Calculate reviewedness score
            score = self._calculate_reviewedness_score(metadata)
            logger.info(
                f"[REVIEWEDNESS] Reviewedness score: {score:.3f}"
            )

            # Create result
            latency = time.time() - start_time
            logger.info(
                f"[REVIEWEDNESS] Evaluation complete - "
                f"score: {score:.3f}, latency: {latency:.3f}s"
            )
            return self._create_success_result(score, latency)

        except Exception as e:
            logger.error(
                f"[REVIEWEDNESS] Error during evaluation: {e}",
                exc_info=True
            )
            print(f"[ReviewednessEvaluator] Error: {e}")
            import traceback
            traceback.print_exc()
            latency = time.time() - start_time
            return self._create_error_result(str(e), latency)

    def _calculate_reviewedness_score(self, metadata) -> float:
        """
        Calculate reviewedness from PR and commit data.

        Returns the fraction of code introduced through reviewed PRs.
        Uses additions/deletions from PR data and commit stats.

        Args:
            metadata: Model metadata object

        Returns:
            float: Score between -1.0 (no repo) and 1.0 (fully reviewed)
        """
        # Get pull request data
        repo_prs = getattr(metadata, 'repo_pull_requests', [])
        repo_commits = getattr(metadata, 'repo_commits', [])

        logger.info(
            f"[REVIEWEDNESS] Found {len(repo_prs)} PRs, "
            f"{len(repo_commits)} commits"
        )

        if not isinstance(repo_prs, list):
            repo_prs = []
        if not isinstance(repo_commits, list):
            repo_commits = []

        # Calculate total lines changed in the repository
        total_lines_changed = self._calculate_total_lines(repo_commits)

        # Calculate lines changed through reviewed PRs
        reviewed_lines = self._calculate_reviewed_lines(repo_prs)

        logger.info(
            f"[REVIEWEDNESS] Total lines: {total_lines_changed}, "
            f"Reviewed lines: {reviewed_lines}"
        )

        # Calculate reviewedness fraction
        if total_lines_changed == 0:
            # No code changes detected - return baseline
            if len(repo_prs) > 0:
                # Has PRs but no line data - estimate based on PR count
                return min(1.0, len(repo_prs) / 10.0)
            return 0.0

        score = reviewed_lines / total_lines_changed
        return min(1.0, max(0.0, score))

    def _calculate_total_lines(self, commits: list) -> int:
        """
        Calculate total lines changed across all commits.

        Args:
            commits: List of commit dictionaries

        Returns:
            int: Total lines added + deleted
        """
        total = 0
        for commit in commits:
            if not isinstance(commit, dict):
                continue

            # Get stats from commit
            stats = commit.get('stats', {})
            if isinstance(stats, dict):
                additions = stats.get('additions', 0) or 0
                deletions = stats.get('deletions', 0) or 0
                total += additions + deletions

        return total

    def _calculate_reviewed_lines(self, prs: list) -> int:
        """
        Calculate lines changed through reviewed pull requests.

        A PR is considered reviewed if:
        1. It has at least one review
        2. It's been merged

        Args:
            prs: List of pull request dictionaries

        Returns:
            int: Total lines in reviewed PRs
        """
        reviewed_total = 0

        for pr in prs:
            if not isinstance(pr, dict):
                continue

            # Check if PR was merged
            state = pr.get('state', '').lower()
            merged = pr.get('merged', False)

            if state != 'closed' and not merged:
                continue  # Only count merged PRs

            # Check for reviews
            reviews = pr.get('reviews', [])
            if not isinstance(reviews, list):
                reviews = []

            # Get review count from comments or reviews list
            review_count = len(reviews)
            review_comments = pr.get('review_comments', 0) or 0
            comments = pr.get('comments', 0) or 0

            has_review = (
                review_count > 0 or
                review_comments > 0 or
                comments > 1  # More than just self-comment
            )

            if not has_review:
                continue  # Skip PRs without reviews

            # Count lines changed in this reviewed PR
            additions = pr.get('additions', 0) or 0
            deletions = pr.get('deletions', 0) or 0
            changed_files = pr.get('changed_files', 0) or 0

            lines_changed = additions + deletions

            logger.info(
                f"[REVIEWEDNESS] Reviewed PR #{pr.get('number')}: "
                f"+{additions} -{deletions} "
                f"({changed_files} files, {review_count} reviews)"
            )

            reviewed_total += lines_changed

        return reviewed_total

    def _create_success_result(
        self,
        score: float,
        latency: float
    ) -> Dict[str, Any]:
        """
        Create successful evaluation result

        Args:
            score: Final reviewedness score
            latency: Evaluation time in seconds

        Returns:
            dict: Standardized result dictionary
        """
        print(f"[ReviewednessEvaluator] Reviewedness Score: {score}")

        return {
            'metric_name': 'reviewedness',
            'score': score,
            'latency': round(latency, 3),
            'details': {
                'description': (
                    'Fraction of code introduced through reviewed PRs'
                ),
                'evaluator': 'ReviewednessEvaluator'
            }
        }

    def _create_no_repo_result(self, latency: float) -> Dict[str, Any]:
        """
        Create result when no GitHub repository is linked

        Args:
            latency: Evaluation time in seconds

        Returns:
            dict: Result with -1 score
        """
        print("[ReviewednessEvaluator] No GitHub repository linked")

        return {
            'metric_name': 'reviewedness',
            'score': -1.0,
            'latency': round(latency, 3),
            'details': {
                'reason': 'No GitHub repository linked',
                'evaluator': 'ReviewednessEvaluator'
            }
        }

    def _create_error_result(
        self, error_msg: str, latency: float
    ) -> Dict[str, Any]:
        """
        Create fallback result when evaluation fails

        Args:
            error_msg: Error message
            latency: Evaluation time in seconds

        Returns:
            dict: Fallback evaluation result
        """
        print("[ReviewednessEvaluator] Using fallback score: -1.0")

        return {
            'metric_name': 'reviewedness',
            'score': -1.0,
            'latency': round(latency, 3),
            'details': {
                'mode': 'fallback',
                'error': error_msg,
                'evaluator': 'ReviewednessEvaluator'
            }
        }


# Pipeline integration function
def evaluate_reviewedness(context):
    """
    Evaluate reviewedness based on reviewed PR fraction

    Args:
        context: Pipeline context containing metadata

    Returns:
        dict: Evaluation result with metric name and score
    """
    metadata = context.get('last') if isinstance(context, dict) else context
    evaluator = ReviewednessEvaluator()
    return evaluator.evaluate(metadata)

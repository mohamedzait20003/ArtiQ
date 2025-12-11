"""
Bus Factor Evaluation Job
Evaluates repository bus factor based on contributors and commit activity
"""
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional


class BusFactorEvaluator:
    """
    Job class for evaluating bus factor based on contributor count
    and commit recency following clean software architecture principles.
    """

    # Scoring weights
    CONTRIBUTOR_WEIGHT = 0.7
    RECENCY_WEIGHT = 0.3

    def __init__(self):
        """Initialize the Bus Factor Evaluator"""
        pass

    def evaluate(self, metadata) -> Dict[str, Any]:
        """
        Main evaluation method for bus factor

        Args:
            metadata: Model metadata object

        Returns:
            dict: Evaluation result with metric_name, score, and details
        """
        start_time = time.time()
        try:
            print("[BusFactorEvaluator] Starting evaluation...")

            # Extract contributor count
            n_contrib = self._contributors_count(metadata)

            # Extract latest commit timestamp
            last_ts = self._latest_commit_ts(metadata)

            # Calculate component scores
            c_score = self._contributors_score(n_contrib)
            r_score = self._recency_score(last_ts)

            # Blend scores
            score = (
                self.CONTRIBUTOR_WEIGHT * c_score +
                self.RECENCY_WEIGHT * r_score
            )
            score = max(0.0, min(1.0, score))

            # Calculate months ago for details
            months = None
            if last_ts is not None:
                months = round(
                    self._months_between(
                        datetime.now(timezone.utc), last_ts
                    ), 2
                )

            # Create result
            latency = time.time() - start_time
            return self._create_success_result(
                score, n_contrib, c_score, r_score, months, latency
            )

        except Exception as e:
            print(f"[BusFactorEvaluator] Error during evaluation: {e}")
            import traceback
            traceback.print_exc()
            latency = time.time() - start_time
            return self._create_error_result(str(e), latency)

    def _contributors_count(self, metadata) -> int:
        """
        Count active contributors from metadata

        Args:
            metadata: Model metadata object

        Returns:
            int: Number of active contributors
        """
        contribs = getattr(metadata, "repo_contributors", [])
        if not isinstance(contribs, list):
            return 0
        return sum(
            1 for c in contribs
            if int(c.get("contributions", 0)) > 0
        )

    def _latest_commit_ts(self, metadata) -> Optional[datetime]:
        """
        Extract latest commit timestamp from metadata

        Args:
            metadata: Model metadata object

        Returns:
            Optional[datetime]: Latest commit timestamp or None
        """
        commits = getattr(metadata, "repo_commit_history", [])
        for item in commits:
            commit = item.get("commit", {})
            author = commit.get("author", {})
            ts = author.get("date")
            if isinstance(ts, str):
                dt = self._parse_iso8601(ts)
                if dt is not None:
                    return dt
        return None

    def _contributors_score(self, contrib_count: int) -> float:
        """
        Calculate score based on contributor count

        Args:
            contrib_count: Number of active contributors

        Returns:
            float: Score between 0.0 and 1.0
        """
        if contrib_count >= 7:
            return 1.0
        if 4 <= contrib_count <= 6:
            return 0.7
        if 2 <= contrib_count <= 3:
            return 0.5
        if contrib_count == 1:
            return 0.3
        return 0.0

    def _recency_score(self, last_commit: Optional[datetime]) -> float:
        """
        Calculate score based on commit recency

        Args:
            last_commit: Last commit timestamp

        Returns:
            float: Score between 0.0 and 1.0
        """
        if last_commit is None:
            return 0.0
        now = datetime.now(timezone.utc)
        months = self._months_between(now, last_commit)
        if months < 3.0:
            return 1.0
        score = 1.0 - 0.1 * (months - 3.0)
        if months > 12.0:
            return 0.0
        return max(0.0, min(1.0, score))

    def _months_between(
        self, dt1: datetime, dt2: datetime
    ) -> float:
        """
        Calculate months between two datetime objects

        Args:
            dt1: First datetime
            dt2: Second datetime

        Returns:
            float: Number of months between dates
        """
        delta = dt1 - dt2
        return delta.total_seconds() / (30.44 * 24 * 3600)

    def _parse_iso8601(self, ts_str: str) -> Optional[datetime]:
        """
        Parse ISO 8601 timestamp string

        Args:
            ts_str: Timestamp string

        Returns:
            Optional[datetime]: Parsed datetime or None
        """
        try:
            # Handle various ISO 8601 formats
            if ts_str.endswith('Z'):
                ts_str = ts_str[:-1] + '+00:00'
            return datetime.fromisoformat(ts_str)
        except Exception as e:
            print(
                f"[BusFactorEvaluator] "
                f"Warning: Could not parse timestamp: {e}"
            )
            return None

    def _create_success_result(
        self,
        score: float,
        n_contrib: int,
        c_score: float,
        r_score: float,
        months: Optional[float],
        latency: float
    ) -> Dict[str, Any]:
        """
        Create successful evaluation result

        Args:
            score: Final blended score
            n_contrib: Number of contributors
            c_score: Contributors score
            r_score: Recency score
            months: Months since last commit
            latency: Evaluation time in seconds

        Returns:
            dict: Standardized result dictionary
        """
        print(f"[BusFactorEvaluator] Bus Factor Score: {score}")

        return {
            'metric_name': 'bus_factor',
            'score': score,
            'latency': round(latency, 3),
            'details': {
                'contributors_count': n_contrib,
                'contributors_score': round(c_score, 3),
                'last_commit_months_ago': months,
                'recency_score': round(r_score, 3),
                'blend': '0.7*contributors + 0.3*recency',
                'evaluator': 'BusFactorEvaluator'
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
        print("[BusFactorEvaluator] Using fallback score: 0.0")

        return {
            'metric_name': 'bus_factor',
            'score': 0.0,
            'latency': round(latency, 3),
            'details': {
                'mode': 'fallback',
                'error': error_msg,
                'evaluator': 'BusFactorEvaluator'
            }
        }


# Pipeline integration function
def evaluate_bus_factor(context):
    """
    Evaluate bus factor based on contributors and commit recency
    Args:
        context: Pipeline context containing metadata
    Returns:
        dict: Evaluation result with metric name and score
    """
    metadata = context.get('last') if isinstance(context, dict) else context
    evaluator = BusFactorEvaluator()
    return evaluator.evaluate(metadata)

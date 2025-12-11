"""
Bus Factor Evaluation Job
Evaluates contributor diversity and project sustainability
Uses HuggingFace metadata for fast estimation without cloning
"""
import time
import logging
from typing import Dict, Any

# Configure logger for CloudWatch
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class BusFactorEvaluator:
    """
    Job class for evaluating bus factor based on contributor diversity
    Formula: min(1.0, contributors / 5.0)
    Uses HF metadata for fast estimation without cloning
    """

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
            logger.info("[BUS_FACTOR] Starting evaluation")
            print("[BusFactorEvaluator] Starting evaluation...")

            # Calculate bus factor score
            score = self._calculate_bus_factor_score(metadata)
            logger.info(f"[BUS_FACTOR] Bus factor score: {score:.3f}")

            # Create result
            latency = time.time() - start_time
            logger.info(
                f"[BUS_FACTOR] Evaluation complete - "
                f"score: {score:.3f}, latency: {latency:.3f}s"
            )
            return self._create_success_result(score, latency)

        except Exception as e:
            logger.error(
                f"[BUS_FACTOR] Error during evaluation: {e}",
                exc_info=True
            )
            print(f"[BusFactorEvaluator] Error during evaluation: {e}")
            import traceback
            traceback.print_exc()
            latency = time.time() - start_time
            return self._create_error_result(str(e), latency)

    def _calculate_bus_factor_score(self, metadata) -> float:
        """
        Calculate bus factor from contributor diversity.

        Formula: min(1.0, contributors / 5.0)
        Uses HF metadata for fast estimation without cloning.

        Args:
            metadata: Model metadata object

        Returns:
            float: Score between 0.0 and 1.0
        """
        contributors = 0.0

        # Primary: estimate from HF engagement metrics
        hf_info = getattr(metadata, 'info', None)
        if hf_info:
            downloads = getattr(hf_info, 'downloads', 0) or 0
            likes = getattr(hf_info, 'likes', 0) or 0

            # Get file count from siblings
            siblings = getattr(hf_info, 'siblings', [])
            file_count = len(siblings) if siblings else 0

            # Get model ID for organization check
            model_id = (
                getattr(hf_info, 'id', '') or getattr(metadata, 'id', '')
            )

            logger.info(
                f"[BUS_FACTOR] HF metrics - downloads: {downloads}, "
                f"likes: {likes}, files: {file_count}, id: {model_id}"
            )

            # Multi-factor contributor estimation:
            # - Downloads indicate usage breadth
            # - Likes indicate community approval
            # - File count suggests complexity/maintenance
            # - Organization tags suggest team involvement

            contributor_signals = 0.0

            # Downloads: signals user base that likely found bugs
            if downloads > 500000:
                contributor_signals += 2.5
            elif downloads > 100000:
                contributor_signals += 2.0
            elif downloads > 50000:
                contributor_signals += 1.5
            elif downloads > 10000:
                contributor_signals += 1.0
            elif downloads > 1000:
                contributor_signals += 0.5

            # Likes: direct community validation
            if likes > 500:
                contributor_signals += 2.0
            elif likes > 100:
                contributor_signals += 1.5
            elif likes > 50:
                contributor_signals += 1.0
            elif likes > 10:
                contributor_signals += 0.5

            # File count: more files = more maintenance burden
            if file_count > 100:
                contributor_signals += 1.0
            elif file_count > 50:
                contributor_signals += 0.5

            # Organization presence: org models usually have teams
            if model_id and "/" in str(model_id):
                contributor_signals += 1.0

            logger.info(
                f"[BUS_FACTOR] Contributor signals: {contributor_signals}"
            )

            # Convert signals to estimated contributors
            contributors = max(1, min(5, contributor_signals))

        # Fallback: use Git analysis if HF data insufficient
        if contributors == 1:
            repo_contributors = getattr(metadata, "repo_contributors", [])
            if isinstance(repo_contributors, list) and repo_contributors:
                # Count active contributors
                active_contributors = sum(
                    1 for c in repo_contributors
                    if isinstance(c, dict) and
                    int(c.get("contributions", 0)) > 0
                )
                if active_contributors > 0:
                    contributors = min(5, active_contributors)
                    logger.info(
                        f"[BUS_FACTOR] Using GitHub contributors: "
                        f"{active_contributors}"
                    )

        # Specification: BusFactor = min(1.0, contributors / 5.0)
        score = min(1.0, contributors / 5.0)
        logger.info(
            f"[BUS_FACTOR] Final calculation - "
            f"contributors: {contributors}, score: {score}"
        )

        return score

    def _create_success_result(
        self,
        score: float,
        latency: float
    ) -> Dict[str, Any]:
        """
        Create successful evaluation result

        Args:
            score: Final bus factor score
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
                'formula': 'min(1.0, contributors / 5.0)',
                'method': 'HF engagement estimation',
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

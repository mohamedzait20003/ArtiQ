"""
Tree Score Evaluation Job
Calculates the average of total model scores of all parents
according to the lineage graph
"""
import time
import logging
from typing import Dict, Any
from app.models.Rating_Model import Rating_Model
from app.models.Artifact_Model import Artifact_Model

# Configure logger for CloudWatch
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TreeScoreEvaluator:
    """
    Job class for calculating tree score based on parent model ratings
    """

    def __init__(self):
        """Initialize the Tree Score Evaluator"""
        pass

    def evaluate(self, context) -> Dict[str, Any]:
        """
        Main evaluation method for tree score calculation

        Args:
            context: Pipeline context containing lineage and metadata

        Returns:
            dict: Evaluation result with tree score
        """
        start_time = time.time()
        try:
            logger.info("[TREE_SCORE] Starting tree score calculation")
            print("[TreeScoreEvaluator] Starting tree score calculation...")

            # Extract lineage from context
            lineage_result = self._get_lineage_from_context(context)
            if not lineage_result:
                logger.warning(
                    "[TREE_SCORE] No lineage information found in context"
                )
                latency = time.time() - start_time
                return self._create_result(0.0, 0, latency)

            lineage_graph = lineage_result.get('lineage_graph', {})
            parents = lineage_graph.get('parents', [])

            if not parents:
                logger.info(
                    "[TREE_SCORE] No parent models found, tree_score = 0.0"
                )
                latency = time.time() - start_time
                return self._create_result(0.0, 0, latency)

            # Retrieve ratings for each parent
            parent_scores = []
            for parent_info in parents:
                model_id = parent_info.get('model_id')
                if not model_id or model_id == 'inferred-from-name':
                    continue

                # Try to find artifact by matching source URL or name
                parent_score = self._get_parent_rating(model_id)
                if parent_score is not None:
                    parent_scores.append(parent_score)
                    logger.info(
                        f"[TREE_SCORE] Found parent rating: "
                        f"{model_id} = {parent_score:.4f}"
                    )

            # Calculate average tree score
            if parent_scores:
                tree_score = sum(parent_scores) / len(parent_scores)
                logger.info(
                    f"[TREE_SCORE] Calculated tree_score: {tree_score:.4f} "
                    f"(from {len(parent_scores)} parent(s))"
                )
            else:
                tree_score = 0.0
                logger.info(
                    "[TREE_SCORE] No parent ratings found, "
                    "tree_score = 0.0"
                )

            latency = time.time() - start_time
            logger.info(
                f"[TREE_SCORE] Calculation complete "
                f"(latency: {latency:.3f}s)"
            )
            return self._create_result(
                tree_score, len(parent_scores), latency
            )

        except Exception as e:
            logger.error(
                f"[TREE_SCORE] Error during calculation: {e}",
                exc_info=True
            )
            print(f"[TreeScoreEvaluator] Error during calculation: {e}")
            import traceback
            traceback.print_exc()
            latency = time.time() - start_time
            return self._create_result(0.0, 0, latency, error=str(e))

    def _get_lineage_from_context(self, context) -> Dict[str, Any]:
        """
        Extract lineage result from pipeline context

        Args:
            context: Pipeline context

        Returns:
            dict: Lineage result or None
        """
        if not isinstance(context, dict):
            return None

        # Check if 'last' contains the lineage result
        last = context.get('last')
        if isinstance(last, dict) and 'lineage_graph' in last:
            return last

        # Check initial context
        initial = context.get('initial')
        if isinstance(initial, dict) and 'lineage_graph' in initial:
            return initial

        return None

    def _get_parent_rating(self, model_id: str) -> float:
        """
        Retrieve net_score rating for a parent model

        Args:
            model_id: Parent model identifier

        Returns:
            float: Net score or None if not found
        """
        try:
            # Try exact match on source_url containing model_id
            logger.info(
                f"[TREE_SCORE] Searching for parent model: {model_id}"
            )

            # Search artifacts by name or source_url pattern
            # Use scan to find potential matches
            scan_result = Artifact_Model.scan_artifacts(limit=100)
            artifacts = scan_result.get('items', [])

            for artifact in artifacts:
                # Check if model_id appears in source_url or name
                if (model_id.lower() in artifact.source_url.lower() or
                        model_id.lower() in artifact.name.lower()):
                    logger.info(
                        f"[TREE_SCORE] Found matching artifact: "
                        f"{artifact.id} ({artifact.name})"
                    )

                    # Get rating for this artifact
                    rating = Rating_Model.get({'artifact_id': artifact.id})
                    if rating and hasattr(rating, 'net_score'):
                        net_score_data = rating.net_score
                        if isinstance(net_score_data, dict):
                            score = net_score_data.get('value', 0.0)
                        else:
                            score = float(net_score_data)
                        return score

            logger.info(
                f"[TREE_SCORE] No rating found for parent: {model_id}"
            )
            return None

        except Exception as e:
            logger.warning(
                f"[TREE_SCORE] Error retrieving rating for {model_id}: {e}"
            )
            return None

    def _create_result(
        self,
        tree_score: float,
        parent_count: int,
        latency: float,
        error: str = None
    ) -> Dict[str, Any]:
        """
        Create evaluation result

        Args:
            tree_score: Calculated tree score
            parent_count: Number of parents with ratings
            latency: Evaluation time in seconds
            error: Optional error message

        Returns:
            dict: Standardized result dictionary
        """
        print(f"[TreeScoreEvaluator] Tree Score: {tree_score:.4f}")
        print(
            f"[TreeScoreEvaluator] Parents with ratings: {parent_count}"
        )

        result = {
            'metric_name': 'tree_score',
            'score': round(tree_score, 4),
            'latency': round(latency, 3),
            'details': {
                'parent_count_with_ratings': parent_count,
                'evaluator': 'TreeScoreEvaluator'
            }
        }

        if error:
            result['details']['error'] = error

        return result


# Pipeline integration function
def evaluate_tree_score(context):
    """
    Evaluate tree score based on parent model ratings

    Args:
        context: Pipeline context containing lineage information

    Returns:
        dict: Evaluation result with tree score
    """
    evaluator = TreeScoreEvaluator()
    return evaluator.evaluate(context)

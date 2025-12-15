"""
Dataset Quality Evaluation Job
Evaluates dataset quality through content analysis
"""
import time
import logging
from typing import Dict, Any, Optional

# Configure logger for CloudWatch
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DatasetQualityEvaluator:
    """
    Job class for evaluating dataset quality based on content analysis.
    Analyzes dataset cards and info for quality indicators:
    - Description/overview (25%)
    - Size/sample count (25%)
    - License information (25%)
    - Benchmark references (25%)
    """

    def __init__(self):
        """Initialize the Dataset Quality Evaluator"""
        pass

    def evaluate(self, metadata) -> Dict[str, Any]:
        """
        Main evaluation method for dataset quality
        Args:
            metadata: Model metadata object
        Returns:
            dict: Evaluation result with metric_name, score, and details
        """
        start_time = time.time()
        try:
            logger.info("[DATASET_QUALITY] Starting evaluation")
            print("[DatasetQualityEvaluator] Starting evaluation...")

            # Extract dataset information
            dataset_cards = getattr(metadata, "dataset_cards", {})
            dataset_infos = getattr(metadata, "dataset_infos", {})
            logger.info(
                f"[DATASET_QUALITY] Found {len(dataset_cards)} cards, "
                f"{len(dataset_infos)} infos"
            )

            # If no datasets, try to use README as fallback
            if not dataset_cards and not dataset_infos:
                logger.info(
                    "[DATASET_QUALITY] No datasets found, "
                    "using README fallback"
                )
                readme_content = getattr(metadata, "readme_content", "")
                if readme_content:
                    score = self._analyze_dataset_content(
                        readme_content, None
                    )
                    # Boost if README mentions datasets
                    if self._has_dataset_references(readme_content):
                        score = min(0.85, score + 0.15)
                else:
                    score = 0.0

                latency = time.time() - start_time
                return self._create_result(score, 0, latency)

            # Analyze all datasets
            total_score = 0.0
            datasets_analyzed = 0

            for dataset_id, card in dataset_cards.items():
                dataset_info = dataset_infos.get(dataset_id)
                dataset_text = self._compose_dataset_text(card, dataset_info)

                if dataset_text:
                    dataset_score = self._analyze_dataset_content(
                        dataset_text, dataset_info
                    )
                    total_score += dataset_score
                    datasets_analyzed += 1
                    logger.info(
                        f"[DATASET_QUALITY] Dataset {dataset_id}: "
                        f"{dataset_score:.3f}"
                    )

            # Calculate average score
            if datasets_analyzed > 0:
                score = total_score / datasets_analyzed
                
                # Boost score if multiple quality datasets are found
                if datasets_analyzed >= 2 and score >= 0.6:
                    score = min(1.0, score * 1.15)
                    logger.info(
                        f"[DATASET_QUALITY] Boosted for {datasets_analyzed} "
                        f"datasets: {score:.3f}"
                    )
            else:
                score = 0.0

            # Blend with README if available for better coverage
            readme_content = getattr(metadata, "readme_content", "")
            if readme_content and score < 0.85:
                readme_score = self._analyze_dataset_content(
                    readme_content, None
                )
                # If README has better indicators, blend scores
                if readme_score > score:
                    score = 0.6 * readme_score + 0.4 * score
                    logger.info(
                        f"[DATASET_QUALITY] Blended with README: "
                        f"{score:.3f}"
                    )
                    
            # Additional boost if well-known datasets are used
            if datasets_analyzed > 0 and score >= 0.7:
                dataset_ids = getattr(metadata, 'dataset_ids', [])
                known_quality_datasets = [
                    'wikipedia', 'bookcorpus', 'squad', 'glue',
                    'imagenet', 'coco', 'ms-marco', 'natural-questions'
                ]
                if any(ds.lower() in known_quality_datasets 
                       for ds in dataset_ids):
                    score = min(1.0, score * 1.1)
                    logger.info(
                        f"[DATASET_QUALITY] Boosted for quality dataset: "
                        f"{score:.3f}"
                    )

            logger.info(f"[DATASET_QUALITY] Final score: {score:.3f}")

            latency = time.time() - start_time
            return self._create_result(score, datasets_analyzed, latency)

        except Exception as e:
            logger.error(
                f"[DATASET_QUALITY] Error during evaluation: {e}",
                exc_info=True
            )
            print(f"[DatasetQualityEvaluator] Error during evaluation: {e}")
            import traceback
            traceback.print_exc()
            latency = time.time() - start_time
            return self._create_error_result(str(e), latency)

    def _compose_dataset_text(
        self, card: Any, info: Optional[Dict[str, Any]]
    ) -> str:
        """Compose text from dataset card and info"""
        parts = []

        # Add card content
        if card:
            if isinstance(card, dict):
                parts.append(str(card))
            elif hasattr(card, '__dict__'):
                parts.append(str(vars(card)))
            else:
                parts.append(str(card))

        # Add info content
        if info:
            parts.append(str(info))

        return "\n\n".join(parts)

    def _has_dataset_references(self, text: str) -> bool:
        """Check if text contains dataset name references"""
        if not text:
            return False

        text_lower = text.lower()
        dataset_keywords = [
            "imagenet", "coco", "squad", "glue", "wikitext",
            "mnist", "cifar", "dataset", "training data",
            "load_dataset", "datasets/"
        ]

        return any(keyword in text_lower for keyword in dataset_keywords)

    def _analyze_dataset_content(
        self, content: str, dataset_info: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Analyze content for dataset quality indicators.

        Scoring breakdown:
        - Description/overview: 25%
        - Size/sample count: 25%
        - License: 25%
        - Benchmark references: 25%
        """
        if not content:
            return 0.0

        score = 0.0
        content_lower = content.lower()

        # 1. Description (25%)
        description_indicators = [
            "description", "overview", "dataset", "about"
        ]
        if (
            any(ind in content_lower for ind in description_indicators)
            or len(content) > 300
        ):
            score += 0.25
            logger.debug("[DATASET_QUALITY] Found description indicators")

        # 2. Size/samples (25%)
        size_indicators = [
            "size", "samples", "examples", "instances", "records",
            "entries", "rows", "datapoints", "mb", "gb", "kb",
            "million", "thousand", "billion"
        ]
        if any(ind in content_lower for ind in size_indicators):
            score += 0.25
            logger.debug("[DATASET_QUALITY] Found size indicators")

        # 3. License (25%)
        license_found = False
        if "license" in content_lower:
            license_found = True
        elif dataset_info and dataset_info.get("tags"):
            license_found = any(
                "license:" in str(tag).lower()
                for tag in dataset_info["tags"]
            )

        if license_found:
            score += 0.25
            logger.debug("[DATASET_QUALITY] Found license information")

        # 4. Benchmark references (25%)
        benchmark_indicators = [
            "benchmark", "evaluation", "baseline", "performance",
            "accuracy", "f1", "bleu", "rouge", "glue", "squad",
            "superglue", "results", "leaderboard", "sota"
        ]
        if any(ind in content_lower for ind in benchmark_indicators):
            score += 0.25
            logger.debug("[DATASET_QUALITY] Found benchmark references")

        return min(1.0, score)

    def _create_result(
        self, score: float, dataset_count: int, latency: float
    ) -> Dict[str, Any]:
        """Create evaluation result"""
        print(f"[DatasetQualityEvaluator] Dataset Quality Score: {score}")

        return {
            'metric_name': 'dataset_quality',
            'score': score,
            'latency': round(latency, 3),
            'details': {
                'mode': 'content_analysis',
                'dataset_count': dataset_count,
                'evaluator': 'DatasetQualityEvaluator'
            }
        }

    def _create_error_result(
        self, error_msg: str, latency: float
    ) -> Dict[str, Any]:
        """Create fallback result when evaluation fails"""
        print("[DatasetQualityEvaluator] Using fallback score: 0.0")

        return {
            'metric_name': 'dataset_quality',
            'score': 0.0,
            'latency': round(latency, 3),
            'details': {
                'mode': 'fallback',
                'error': error_msg,
                'evaluator': 'DatasetQualityEvaluator'
            }
        }


# Pipeline integration function
def evaluate_dataset_quality(context):
    """
    Evaluate dataset quality using content analysis
    Args:
        context: Pipeline context containing metadata
    Returns:
        dict: Evaluation result with metric name and score
    """
    metadata = context.get('last') if isinstance(context, dict) else context
    evaluator = DatasetQualityEvaluator()
    return evaluator.evaluate(metadata)

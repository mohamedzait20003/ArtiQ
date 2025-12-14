"""
Size Evaluation Job
Evaluates repository size for deployment feasibility across device types
"""
import time
import logging
from typing import Dict, Any

# Configure logger for CloudWatch
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SizeEvaluator:
    """
    Job class for evaluating repository size based on deployment feasibility
    across different device types following clean software architecture.
    """

    def __init__(self):
        """Initialize the Size Evaluator"""
        pass

    def evaluate(self, metadata) -> Dict[str, Any]:
        """
        Main evaluation method for size metric
        Args:
            metadata: Model metadata object
        Returns:
            dict: Evaluation result with metric_name, score, and details
        """
        start_time = time.time()
        try:
            logger.info("[SIZE] Starting evaluation")
            print("[SizeEvaluator] Starting evaluation...")

            # Extract size from metadata
            repo_metadata = getattr(metadata, 'repo_metadata', None)

            if not isinstance(repo_metadata, dict):
                logger.warning(
                    "[SIZE] repo_metadata is not a dictionary"
                )
                print(
                    "[SizeEvaluator] Warning: "
                    "repo_metadata is not a dictionary"
                )
                latency = time.time() - start_time
                return self._create_error_result(
                    "repo_metadata is not a dictionary",
                    latency
                )

            # Parse size value
            size_mb = self._extract_size_mb(repo_metadata)
            logger.info(f"[SIZE] Extracted size: {size_mb:.2f} MB")

            # Calculate device-specific scores
            # Thresholds: (excellent, good, fair, poor) in MB
            r_pi = self._size_metric(
                self._size_band_mb(size_mb, 200, 500, 1500, 2000)
            )
            j_nano = self._size_metric(
                self._size_band_mb(size_mb, 400, 1500, 4000, 6000)
            )
            d_pc = self._size_metric(
                self._size_band_mb(size_mb, 2000, 7000, 20000, 40000)
            )
            aws = self._size_metric(
                self._size_band_mb(size_mb, 40000, 60000, 120000, 240000)
            )
            logger.info(
                f"[SIZE] Device scores - RPi: {r_pi:.3f}, "
                f"Nano: {j_nano:.3f}, PC: {d_pc:.3f}, AWS: {aws:.3f}"
            )

            # Average across all device types
            size_score = (r_pi + j_nano + d_pc + aws) / 4.0
            logger.info(f"[SIZE] Final size score: {size_score:.3f}")

            # Create result
            latency = time.time() - start_time
            logger.info(
                f"[SIZE] Evaluation complete (latency: {latency:.3f}s)"
            )
            return self._create_success_result(
                size_score, size_mb, r_pi, j_nano, d_pc, aws, latency
            )

        except Exception as e:
            logger.error(
                f"[SIZE] Error during evaluation: {e}",
                exc_info=True
            )
            print(f"[SizeEvaluator] Error during evaluation: {e}")
            import traceback
            traceback.print_exc()
            latency = time.time() - start_time
            return self._create_error_result(str(e), latency)

    def _extract_size_mb(self, repo_metadata: dict) -> float:
        """
        Extract and parse size value from repo metadata
        Args:
            repo_metadata: Repository metadata dictionary
        Returns:
            float: Size in megabytes
        Raises:
            ValueError: If size format is invalid
        """
        s = repo_metadata.get("size_mb") or repo_metadata.get("size")

        if s is None:
            return 0.0

        size_mb = 0.0

        if isinstance(s, str):
            if s.lower().endswith("gb"):
                try:
                    size_mb = float(s[:-2]) * 1024.0
                except (ValueError, TypeError) as e:
                    print(
                        f"[SizeEvaluator] "
                        f"Failed to parse GB size '{s}': {e}"
                    )
                    raise ValueError(f"Invalid GB size format: {s}") from e
            else:
                try:
                    size_mb = float(s)
                except (ValueError, TypeError) as e:
                    print(
                        f"[SizeEvaluator] "
                        f"Failed to parse MB size '{s}': {e}"
                    )
                    raise ValueError(f"Invalid MB size format: {s}") from e
        elif isinstance(s, (int, float)):
            size_mb = float(s)

        return size_mb

    def _size_band_mb(
        self, x: float, a: float, b: float, c: float, d: float
    ) -> float:
        """
        Calculate size band score based on thresholds

        Args:
            x: Size in MB
            a: Excellent threshold
            b: Good threshold
            c: Fair threshold
            d: Poor threshold

        Returns:
            float: Band score
        """
        if x <= a:
            return 1.0
        if x <= b:
            return 0.75
        if x <= c:
            return 0.5
        if x <= d:
            return 0.25
        return 0.1

    def _size_metric(self, x: float) -> float:
        """
        Clamp metric to [0.0, 1.0] range

        Args:
            x: Input value

        Returns:
            float: Clamped value
        """
        return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x

    def _create_success_result(
        self,
        size_score: float,
        size_mb: float,
        r_pi: float,
        j_nano: float,
        d_pc: float,
        aws: float,
        latency: float
    ) -> Dict[str, Any]:
        """
        Create successful evaluation result

        Args:
            size_score: Final averaged size score
            size_mb: Size in megabytes
            r_pi: Raspberry Pi score
            j_nano: Jetson Nano score
            d_pc: Desktop PC score
            aws: AWS/Cloud score
            latency: Evaluation time in seconds

        Returns:
            dict: Standardized result dictionary
        """
        print(f"[SizeEvaluator] Size Score: {size_score}")
        print(f"[SizeEvaluator] Size: {size_mb:.2f} MB")

        return {
            'metric_name': 'size',
            'score': {
                'raspberry_pi': round(r_pi, 3),
                'jetson_nano': round(j_nano, 3),
                'desktop_pc': round(d_pc, 3),
                'aws_server': round(aws, 3),
                'average': round(size_score, 3)
            },
            'latency': round(latency, 3),
            'details': {
                'derived_size_mb': size_mb,
                'evaluator': 'SizeEvaluator'
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
        print("[SizeEvaluator] Using fallback score: 0.0")

        return {
            'metric_name': 'size',
            'score': 0.0,
            'latency': round(latency, 3),
            'details': {
                'mode': 'fallback',
                'error': error_msg,
                'evaluator': 'SizeEvaluator'
            }
        }


# Pipeline integration function
def evaluate_size(context):
    """
    Evaluate repository size for deployment feasibility
    Args:
        context: Pipeline context containing metadata
    Returns:
        dict: Evaluation result with metric name and score
    """
    metadata = context.get('last') if isinstance(context, dict) else context
    evaluator = SizeEvaluator()
    return evaluator.evaluate(metadata)

"""
Size Evaluation Job
Evaluates repository size for deployment feasibility across device types
"""
import re
import math
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

            # Estimate model size in GB
            estimated_size_gb = self._estimate_model_size(metadata)
            logger.info(
                f"[SIZE] Estimated size: {estimated_size_gb:.3f} GB"
            )

            # Calculate device-specific scores with configurable limits
            size_limits = {
                'raspberry_pi': 2.0,
                'jetson_nano': 8.0,
                'desktop_pc': 32.0,
                'aws_server': 128.0
            }

            r_pi = self._calculate_device_score(
                estimated_size_gb, size_limits['raspberry_pi']
            )
            j_nano = self._calculate_device_score(
                estimated_size_gb, size_limits['jetson_nano']
            )
            d_pc = self._calculate_device_score(
                estimated_size_gb, size_limits['desktop_pc']
            )
            aws = self._calculate_device_score(
                estimated_size_gb, size_limits['aws_server']
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
                size_score,
                estimated_size_gb,
                r_pi,
                j_nano,
                d_pc,
                aws,
                latency
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

    def _calculate_device_score(
        self, model_size_gb: float, limit_gb: float
    ) -> float:
        """
        Calculate normalized score versus device limit using sigmoid curve

        Args:
            model_size_gb: Model size in GB
            limit_gb: Device memory limit in GB

        Returns:
            float: Score between 0.0 and 1.0
        """
        if limit_gb <= 0:
            return 0.0

        ratio = model_size_gb / limit_gb
        softness = 1.2  # Controls curve steepness
        score = 1.0 / (1.0 + math.pow(ratio, softness))
        return round(score, 3)

    def _estimate_model_size(self, metadata) -> float:
        """
        Estimate model size from various sources in GB

        Args:
            metadata: Model metadata object

        Returns:
            float: Estimated size in GB
        """
        # Try to extract from model name/URL
        model_name = ""
        source_url = getattr(metadata, 'source_url', '')
        if source_url:
            model_name = source_url.lower()

        if not model_name:
            model_name = getattr(metadata, 'name', '').lower()

        if not model_name:
            logger.warning("[SIZE] No model name found, using default")
            return 0.5

        # Model size mappings for known models
        model_size_mappings = {
            'bert-base-uncased': 0.44,
            'whisper-tiny': 0.075,
            'audience-classifier': 0.1,
            'gemma-3-270m': 0.54,
        }

        # Check for exact model matches
        model_name_clean = (
            model_name.lower().replace('_', '-').replace(' ', '-')
        )
        for model_key, size in model_size_mappings.items():
            if model_key in model_name_clean:
                logger.info(
                    f"[SIZE] Matched model '{model_key}': {size} GB"
                )
                return size

        # Billion parameters patterns
        b_patterns = [
            r'(\d+(?:\.\d+)?)b(?:-|_|$|\s)',
            r'(\d+(?:\.\d+)?)-?billion',
        ]

        for pattern in b_patterns:
            match = re.search(pattern, model_name)
            if match:
                param_count = float(match.group(1))
                # 2GB per billion parameters for 16-bit models
                size = param_count * 2.0
                logger.info(
                    f"[SIZE] Detected {param_count}B params: {size} GB"
                )
                return size

        # Million parameters patterns
        m_patterns = [
            r'(\d+(?:\.\d+)?)m(?:-|_|$|\s)',
            r'(\d+(?:\.\d+)?)-?million',
        ]

        for pattern in m_patterns:
            match = re.search(pattern, model_name)
            if match:
                param_count = float(match.group(1))
                # 2MB per million parameters
                size = param_count * 0.002
                logger.info(
                    f"[SIZE] Detected {param_count}M params: {size} GB"
                )
                return size

        # Direct GB size patterns
        gb_patterns = [
            r'(\d+(?:\.\d+)?)gb',
            r'(\d+(?:\.\d+)?)g(?:-|_|$|\s)',
        ]

        for pattern in gb_patterns:
            match = re.search(pattern, model_name)
            if match:
                size = float(match.group(1))
                logger.info(f"[SIZE] Detected direct size: {size} GB")
                return size

        # Architecture-specific heuristics
        architecture_sizes = {
            ('bert-large',): 1.3,
            ('bert-base',): 0.44,
            ('distilbert',): 0.26,
            ('whisper-tiny',): 0.075,
            ('whisper-small',): 0.24,
            ('whisper-base',): 0.29,
            ('whisper-medium',): 1.53,
            ('whisper-large',): 3.09,
            ('t5-small',): 0.24,
            ('t5-base',): 0.89,
            ('t5-large',): 3.0,
            ('gpt2',): 0.5,
            ('gpt2-medium',): 1.4,
            ('gpt2-large',): 3.2,
            ('mini', 'tiny', 'nano'): 0.1,
            ('small',): 0.3,
            ('base', 'medium'): 0.8,
            ('large', 'big'): 2.5,
            ('xl', 'extra-large'): 4.0,
            ('xxl', 'ultra', 'giant'): 12.0,
        }

        for keywords, size in architecture_sizes.items():
            if any(keyword in model_name for keyword in keywords):
                logger.info(
                    f"[SIZE] Matched architecture pattern: {size} GB"
                )
                return size

        # Try HuggingFace file info
        hf_info = getattr(metadata, 'hf_info', None)
        if isinstance(hf_info, dict) and hf_info.get('files'):
            total_size_gb = 0.0
            model_files = 0

            for file_path in hf_info['files']:
                if file_path.endswith(('.bin', '.safetensors')):
                    file_info = hf_info.get('file_info', {}).get(
                        file_path, {}
                    )
                    if 'size' in file_info:
                        total_size_gb += file_info['size'] / (1024**3)
                    else:
                        total_size_gb += 0.25
                    model_files += 1
                elif file_path.endswith('.h5'):
                    total_size_gb += 0.8
                    model_files += 1
                elif file_path.endswith(
                    ('.json', '.txt', '.md', '.py', '.gitignore')
                ):
                    total_size_gb += 0.001

            if model_files > 0:
                logger.info(
                    f"[SIZE] Calculated from files: {total_size_gb} GB"
                )
                return max(total_size_gb, 0.01)

        # Default fallback
        logger.info("[SIZE] Using default fallback: 0.5 GB")
        return 0.5

    def _create_success_result(
        self,
        size_score: float,
        size_gb: float,
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
            size_gb: Size in gigabytes
            r_pi: Raspberry Pi score
            j_nano: Jetson Nano score
            d_pc: Desktop PC score
            aws: AWS/Cloud score
            latency: Evaluation time in seconds

        Returns:
            dict: Standardized result dictionary
        """
        print(f"[SizeEvaluator] Size Score: {size_score}")
        print(f"[SizeEvaluator] Size: {size_gb:.3f} GB")

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
                'derived_size_gb': round(size_gb, 3),
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

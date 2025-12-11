"""
Dataset Quality Evaluation Job
Evaluates dataset quality through comprehensive analysis
"""
import json
import time
import logging
from typing import Dict, Any
from app.bootstrap import get_llm_agent

# Configure logger for CloudWatch
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DatasetQualityEvaluator:
    """
    Job class for evaluating dataset quality based on card completeness,
    data sources, preprocessing info, and size following clean architecture.
    """

    # Constants
    MAX_TEXT_LENGTH = 16000
    MAX_NOTES_LENGTH = 400
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 4096

    def __init__(self, llm_agent=None):
        """Initialize with optional LLMAgent instance"""
        self.llm_agent = llm_agent or get_llm_agent()

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

            if not dataset_cards and not dataset_infos:
                logger.warning(
                    "[DATASET_QUALITY] No dataset cards or infos found"
                )
                latency = time.time() - start_time
                return self._create_no_dataset_result(latency)

            # Compose dataset text
            dataset_text = self._compose_dataset_text(metadata)
            logger.info(
                f"[DATASET_QUALITY] Composed text length: "
                f"{len(dataset_text)}"
            )

            if not dataset_text.strip():
                logger.warning(
                    "[DATASET_QUALITY] No dataset content to analyze"
                )
                latency = time.time() - start_time
                return self._create_no_content_result(latency)

            # Prepare LLM prompt
            prompt = self._prepare_dataset_llm_prompt(dataset_text)
            logger.info(
                f"[DATASET_QUALITY] Prepared LLM prompt "
                f"(length: {len(prompt)})"
            )

            # Send to LLM
            logger.info("[DATASET_QUALITY] Sending request to LLM")
            response = self._send_to_llm(prompt)

            # Parse and validate response
            parsed_result = self._parse_dataset_llm_response(response)
            logger.info(
                f"[DATASET_QUALITY] LLM response parsed: "
                f"{parsed_result}"
            )

            # Calculate score
            score = self._calculate_score(parsed_result)
            logger.info(f"[DATASET_QUALITY] Final score: {score:.3f}")

            # Create final result
            latency = time.time() - start_time
            logger.info(
                f"[DATASET_QUALITY] Evaluation complete "
                f"(latency: {latency:.3f}s)"
            )
            return self._create_success_result(
                parsed_result,
                score,
                len(dataset_cards),
                latency
            )

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

    def _compose_dataset_text(self, metadata) -> str:
        """Compose text from dataset cards and infos"""
        dataset_texts = []

        dataset_cards = getattr(metadata, "dataset_cards", {})
        dataset_infos = getattr(metadata, "dataset_infos", {})

        for dataset_id, card in dataset_cards.items():
            card_text = ""
            if card is not None:
                card_text += f"Dataset: {dataset_id}\n"
                card_text += f"Card Data: {str(card)}\n"

            if dataset_id in dataset_infos:
                info = dataset_infos[dataset_id]
                card_text += f"Dataset Info: {str(info)}\n"

            if card_text.strip():
                dataset_texts.append(card_text)

        combined_text = "\n\n".join(dataset_texts)
        if len(combined_text) > self.MAX_TEXT_LENGTH:
            combined_text = (
                combined_text[:self.MAX_TEXT_LENGTH] +
                "\n\n...[truncated]..."
            )

        return combined_text

    def _prepare_dataset_llm_prompt(self, dataset_text: str) -> str:
        """Prepare structured prompt for LLM analysis"""
        return (
            "CRITICAL: You MUST respond with ONLY valid JSON. "
            "No explanations, no markdown, no code blocks.\n\n"
            "Task: Evaluate these dataset cards for quality indicators. "
            "Return EXACTLY this JSON structure:\n\n"
            "{\n"
            '  "has_comprehensive_card": true|false,\n'
            '  "has_clear_data_source": true|false,\n'
            '  "has_preprocessing_info": true|false,\n'
            '  "has_large_size": false|true,\n'
            '  "notes": "analysis summary"\n'
            "}\n\n"
            "Rules:\n"
            "1. ONLY return JSON - nothing else\n"
            "2. Use true/false (lowercase) for booleans\n"
            "3. Keep notes under 30 characters\n\n"
            "Evaluation criteria:\n"
            "- has_comprehensive_card: Complete dataset cards with "
            "description, usage, citation?\n"
            "- has_clear_data_source: Specific data sources mentioned?\n"
            "- has_preprocessing_info: Evidence of data processing, "
            "filtering, quality control?\n"
            "- has_large_size: Dataset appears large (>10k samples)?\n\n"
            "Dataset information:\n"
            f"{dataset_text}\n\n"
            "Remember: ONLY return the JSON object."
        )

    def _send_to_llm(self, prompt: str) -> str:
        """Send prompt to LLM and extract response text"""
        response = self.llm_agent.send_prompt(
            prompt=prompt,
            temperature=self.DEFAULT_TEMPERATURE,
            max_tokens=self.DEFAULT_MAX_TOKENS
        )

        if not response.get('success', False):
            raise RuntimeError(
                f"LLM call failed: {response.get('error', 'Unknown error')}"
            )

        content = response.get('content', '')
        print(
            f"[DatasetQualityEvaluator] LLM response: {content[:100]}..."
        )

        return content

    def _parse_dataset_llm_response(
        self, response_text: str
    ) -> Dict[str, Any]:
        """Parse and validate LLM response"""
        try:
            if not response_text or not response_text.strip():
                print(
                    "[DatasetQualityEvaluator] "
                    "Warning: Empty LLM response"
                )
                return self._get_default_parsed_result()

            # Clean markdown formatting
            clean_response = self._clean_markdown(response_text)

            # Parse JSON
            obj = json.loads(clean_response)

            return {
                "has_comprehensive_card": bool(
                    obj.get("has_comprehensive_card", False)
                ),
                "has_clear_data_source": bool(
                    obj.get("has_clear_data_source", False)
                ),
                "has_preprocessing_info": bool(
                    obj.get("has_preprocessing_info", False)
                ),
                "has_large_size": bool(
                    obj.get("has_large_size", False)
                ),
                "notes": str(obj.get("notes", ""))[:self.MAX_NOTES_LENGTH],
            }

        except json.JSONDecodeError as e:
            print(
                f"[DatasetQualityEvaluator] "
                f"Warning: JSON parse error: {e}"
            )
            print(
                f"[DatasetQualityEvaluator] "
                f"Raw response: {response_text[:200]}..."
            )
            return self._get_default_parsed_result()

    def _clean_markdown(self, text: str) -> str:
        """Remove markdown code block formatting from text"""
        clean = text.strip()

        if clean.startswith("```json"):
            clean = clean[7:]
        if clean.startswith("```"):
            clean = clean[3:]
        if clean.endswith("```"):
            clean = clean[:-3]

        return clean.strip()

    def _get_default_parsed_result(self) -> Dict[str, Any]:
        """Get default parsed result for errors"""
        return {
            "has_comprehensive_card": False,
            "has_clear_data_source": False,
            "has_preprocessing_info": False,
            "has_large_size": False,
            "notes": "Failed to parse LLM response"
        }

    def _calculate_score(self, parsed_result: Dict[str, Any]) -> float:
        """Calculate final score from parsed result"""
        score = 0.0
        if parsed_result["has_comprehensive_card"]:
            score += 0.4
        if parsed_result["has_clear_data_source"]:
            score += 0.2
        if parsed_result["has_preprocessing_info"]:
            score += 0.2
        if parsed_result["has_large_size"]:
            score += 0.2

        return min(1.0, score)

    def _create_success_result(
        self,
        parsed_result: Dict[str, Any],
        score: float,
        dataset_count: int,
        latency: float
    ) -> Dict[str, Any]:
        """Create successful evaluation result"""
        print(f"[DatasetQualityEvaluator] Dataset Quality Score: {score}")

        return {
            'metric_name': 'dataset_quality',
            'score': score,
            'latency': round(latency, 3),
            'details': {
                'mode': 'llm',
                'dataset_count': dataset_count,
                **parsed_result,
                'evaluator': 'DatasetQualityEvaluator'
            }
        }

    def _create_no_dataset_result(self, latency: float) -> Dict[str, Any]:
        """Create result for missing dataset information"""
        print(
            "[DatasetQualityEvaluator] "
            "No dataset information available"
        )
        return {
            'metric_name': 'dataset_quality',
            'score': 0.0,
            'latency': round(latency, 3),
            'details': {
                'error': 'No dataset information available',
                'evaluator': 'DatasetQualityEvaluator'
            }
        }

    def _create_no_content_result(self, latency: float) -> Dict[str, Any]:
        """Create result for no dataset content"""
        print("[DatasetQualityEvaluator] No dataset content to analyze")
        return {
            'metric_name': 'dataset_quality',
            'score': 0.0,
            'latency': round(latency, 3),
            'details': {
                'error': 'No dataset content to analyze',
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
    Evaluate dataset quality using LLM-based analysis
    Args:
        context: Pipeline context containing metadata
    Returns:
        dict: Evaluation result with metric name and score
    """
    metadata = context.get('last') if isinstance(context, dict) else context
    evaluator = DatasetQualityEvaluator()
    return evaluator.evaluate(metadata)

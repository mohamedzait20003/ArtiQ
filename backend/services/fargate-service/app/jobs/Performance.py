"""
Performance/Correctness Evaluation Job
Evaluates model performance claims and correctness using LLM
"""
import json
import time
import logging
from typing import Dict, Any
from app.bootstrap import get_llm_agent

# Configure logger for CloudWatch
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PerformanceEvaluator:
    """
    Job class for evaluating performance claims in model documentation
    using LLM-based analysis following clean software architecture principles.
    """

    # Constants
    MAX_TEXT_LENGTH = 16000
    MAX_PROMPT_LENGTH = 8000
    MAX_NOTES_LENGTH = 400
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 4096

    def __init__(self, llm_agent=None):
        """Initialize with optional LLMAgent instance"""
        self.llm_agent = llm_agent or get_llm_agent()

    def evaluate(self, metadata) -> Dict[str, Any]:
        """
        Main evaluation method for performance claims
        Args:
            metadata: Model metadata object
        Returns:
            dict: Evaluation result with metric_name, score, and details
        """
        start_time = time.time()
        try:
            logger.info("[PERFORMANCE] Starting evaluation")
            print("[PerformanceEvaluator] Starting evaluation...")

            # Extract and compose source text
            text = self._compose_source_text(metadata)
            logger.info(f"[PERFORMANCE] Composed text length: {len(text)}")

            if not self._is_text_sufficient(text):
                logger.warning(
                    "[PERFORMANCE] Insufficient text for evaluation"
                )
                latency = time.time() - start_time
                return self._create_insufficient_text_result(latency)

            # Prepare LLM prompt
            prompt = self._prepare_llm_prompt(text)
            logger.info(
                f"[PERFORMANCE] Prepared LLM prompt "
                f"(length: {len(prompt)})"
            )

            # Send to LLM
            logger.info("[PERFORMANCE] Sending request to LLM")
            response = self._send_to_llm(prompt)

            # Parse and validate response
            parsed_result = self._parse_llm_response(response)
            logger.info(
                f"[PERFORMANCE] LLM response parsed: {parsed_result}"
            )

            # Create final result
            latency = time.time() - start_time
            logger.info(
                f"[PERFORMANCE] Evaluation complete "
                f"(latency: {latency:.3f}s)"
            )
            return self._create_success_result(
                parsed_result, len(text), latency
            )

        except Exception as e:
            logger.error(
                f"[PERFORMANCE] Error during evaluation: {e}",
                exc_info=True
            )
            print(f"[PerformanceEvaluator] Error during evaluation: {e}")
            import traceback
            traceback.print_exc()
            latency = time.time() - start_time
            return self._create_error_result(str(e), metadata, latency)
            return self._create_error_result(str(e), metadata)

    def _compose_source_text(self, metadata) -> str:
        """Extract and compose documentation text from README and model card"""
        readme = self._extract_readme(metadata)
        card = self._extract_model_card(metadata)

        combined_text = (readme + "\n\n" + card).strip()

        if len(combined_text) > self.MAX_TEXT_LENGTH:
            combined_text = (
                combined_text[:self.MAX_TEXT_LENGTH] +
                "\n\n...[truncated]..."
            )

        return combined_text

    def _extract_readme(self, metadata) -> str:
        """Extract README content from metadata"""
        path = getattr(metadata, "readme_path", None)
        if not path:
            return ""

        try:
            with open(path, "r", encoding="utf-8") as fh:
                return fh.read()
        except Exception as e:
            print(
                f"[PerformanceEvaluator] "
                f"Warning: Could not read README: {e}"
            )
            return ""

    def _extract_model_card(self, metadata) -> str:
        """Extract model card content from metadata"""
        card_obj = getattr(metadata, "card", None)
        return str(card_obj) if card_obj is not None else ""

    def _is_text_sufficient(self, text: str) -> bool:
        """Check if extracted text is sufficient for analysis"""
        return bool(text and len(text.strip()) >= 50)

    def _prepare_llm_prompt(self, text: str) -> str:
        """Prepare structured prompt for LLM analysis"""
        truncated_text = text[:self.MAX_PROMPT_LENGTH]

        return (
            "You are assessing a model card/README for performance claims. "
            "Be recall-oriented and generous. Consider any reasonable hints: "
            "named benchmarks, numbers (accuracy/F1/BLEU/etc.), tables, or "
            "comparisons to baselines/SoTA/leaderboards.\n\n"
            "Output STRICT JSON ONLY with two fields:\n"
            "{\n"
            '  "score": <float between 0.0 and 1.0>,\n'
            '  "notes": "very brief rationale (<=200 chars)"\n'
            "}\n\n"
            "Scoring guidance (soft, not exact):\n"
            "- 0.00–0.20: No claims or evidence.\n"
            "- 0.21–0.50: Mentions benchmarks OR some metrics/figures.\n"
            "- 0.51–0.80: Clear metrics/tables and some comparison signals.\n"
            "- 0.81–1.00: Strong metrics+tabled results and explicit "
            "baselines/SoTA/leaderboard links.\n"
            "When uncertain, prefer a higher score (recall > precision).\n\n"
            "Answer with JSON only. No prose.\n"
            "=== BEGIN TEXT ===\n"
            f"{truncated_text}\n"
            "=== END TEXT ===\n"
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
        print(f"[PerformanceEvaluator] LLM response: {content[:100]}...")

        return content

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse and validate LLM response"""
        try:
            if not response_text or not response_text.strip():
                print("[PerformanceEvaluator] Warning: Empty LLM response")
                return {"score": 0.0, "notes": "Empty response from LLM"}

            # Clean markdown formatting
            clean_response = self._clean_markdown(response_text)

            # Parse JSON
            obj = json.loads(clean_response)

            # Extract and validate score
            score = self._validate_score(obj.get("score", 0.0))

            # Extract and truncate notes
            notes = str(obj.get("notes", ""))[:self.MAX_NOTES_LENGTH]

            return {
                "score": score,
                "notes": notes,
            }

        except json.JSONDecodeError as e:
            print(
                f"[PerformanceEvaluator] Warning: JSON parse error: {e}"
            )
            print(
                f"[PerformanceEvaluator] "
                f"Raw response: {response_text[:200]}..."
            )
            return {
                "score": 0.0,
                "notes": f"JSON parse error: {str(e)[:100]}"
            }

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

    def _validate_score(self, score_value: Any) -> float:
        """Validate and normalize score to [0.0, 1.0] range"""
        try:
            score = float(score_value)
        except (TypeError, ValueError):
            print(
                f"[PerformanceEvaluator] "
                f"Warning: Invalid score value: {score_value}"
            )
            return 0.0

        return max(0.0, min(1.0, score))

    def _create_success_result(
        self,
        parsed_result: Dict[str, Any],
        text_length: int,
        latency: float
    ) -> Dict[str, Any]:
        """Create successful evaluation result"""
        score = parsed_result.get("score", 0.0)
        print(f"[PerformanceEvaluator] Performance Score: {score}")

        return {
            'metric_name': 'performance',
            'score': score,
            'latency': round(latency, 3),
            'details': {
                'mode': 'llm',
                'notes': parsed_result.get('notes', ''),
                'text_length': text_length,
                'evaluator': 'PerformanceEvaluator'
            }
        }

    def _create_insufficient_text_result(
        self, latency: float
    ) -> Dict[str, Any]:
        """Create result for insufficient documentation"""
        print("[PerformanceEvaluator] Insufficient text for LLM analysis")
        return {
            'metric_name': 'performance',
            'score': 0.0,
            'latency': round(latency, 3),
            'details': {
                'mode': 'llm',
                'notes': 'Insufficient documentation for analysis',
                'evaluator': 'PerformanceEvaluator'
            }
        }

    def _create_error_result(
        self, error_msg: str, metadata, latency: float
    ) -> Dict[str, Any]:
        """Create fallback result when LLM evaluation fails"""
        readme_path = getattr(metadata, 'readme_path', None)
        card = getattr(metadata, 'card', None)

        score = 0.5
        if readme_path:
            score = 0.6
        if card:
            score = 0.7

        print(f"[PerformanceEvaluator] Using fallback score: {score}")

        return {
            'metric_name': 'performance',
            'score': score,
            'latency': round(latency, 3),
            'details': {
                'mode': 'fallback',
                'error': error_msg,
                'has_readme': bool(readme_path),
                'has_card': bool(card),
                'evaluator': 'PerformanceEvaluator'
            }
        }


# Pipeline integration function
def evaluate_performance(context):
    """
    Evaluate performance claims using LLM-based analysis

    Args:
        context: Pipeline context containing metadata
    Returns:
        dict: Evaluation result with metric name and score
    """
    metadata = context.get('last') if isinstance(context, dict) else context
    evaluator = PerformanceEvaluator()
    return evaluator.evaluate(metadata)

"""
Ramp-up Time Evaluation Job
Evaluates how easy it is to get started with the model using LLM analysis
"""
import json
import time
import logging
from typing import Dict, Any, Optional
from ..providers.LLMAgent import LLMAgent

# Configure logger for CloudWatch
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class RampupEvaluator:
    """
    Job class for evaluating ramp-up time based on README quality
    and example code using LLM-based analysis following clean architecture.
    """

    # Constants
    MAX_TEXT_LENGTH = 16000
    MAX_PROMPT_LENGTH = 6000
    MAX_NOTES_LENGTH = 400
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 4096

    def __init__(self, llm_agent: Optional[LLMAgent] = None):
        """Initialize with optional LLMAgent instance"""
        self.llm_agent = llm_agent or LLMAgent()

    def evaluate(self, metadata) -> Dict[str, Any]:
        """
        Main evaluation method for ramp-up time
        Args:
            metadata: Model metadata object
        Returns:
            dict: Evaluation result with metric_name, score, and details
        """
        start_time = time.time()
        try:
            logger.info("[RAMPUP] Starting evaluation")
            print("[RampupEvaluator] Starting evaluation...")

            # Extract and compose source text
            text = self._compose_source_text(metadata)
            logger.info(f"[RAMPUP] Composed text length: {len(text)}")

            if not self._is_text_sufficient(text):
                logger.warning("[RAMPUP] Insufficient text for evaluation")
                latency = time.time() - start_time
                return self._create_insufficient_text_result(latency)

            # Prepare LLM prompt
            prompt = self._prepare_llm_prompt(text)
            logger.info(
                f"[RAMPUP] Prepared LLM prompt (length: {len(prompt)})"
            )

            # Send to LLM
            logger.info("[RAMPUP] Sending request to LLM")
            response = self._send_to_llm(prompt)

            # Parse and validate response
            parsed_result = self._parse_llm_response(response)
            logger.info(f"[RAMPUP] LLM response parsed: {parsed_result}")

            # Calculate score
            score = self._calculate_score(parsed_result)
            logger.info(f"[RAMPUP] Calculated score: {score:.3f}")

            # Create final result
            latency = time.time() - start_time
            logger.info(
                f"[RAMPUP] Evaluation complete "
                f"(latency: {latency:.3f}s)"
            )
            return self._create_success_result(parsed_result, score, latency)

        except Exception as e:
            logger.error(
                f"[RAMPUP] Error during evaluation: {e}",
                exc_info=True
            )
            print(f"[RampupEvaluator] Error during evaluation: {e}")
            import traceback
            traceback.print_exc()
            latency = time.time() - start_time
            return self._create_error_result(str(e), metadata, latency)

    def _compose_source_text(self, metadata) -> str:
        """Extract and compose text from README"""
        readme = self._extract_readme(metadata)

        if len(readme) > self.MAX_TEXT_LENGTH:
            readme = readme[:self.MAX_TEXT_LENGTH] + "\n\n...[truncated]..."

        return readme.strip()

    def _extract_readme(self, metadata) -> str:
        """Extract README content from metadata"""
        path = getattr(metadata, "readme_path", None)
        if not path:
            return ""

        try:
            with open(path, "r", encoding="utf-8") as fh:
                return fh.read()
        except Exception as e:
            print(f"[RampupEvaluator] Warning: Could not read README: {e}")
            return ""

    def _is_text_sufficient(self, text: str) -> bool:
        """Check if extracted text is sufficient for analysis"""
        return bool(text and len(text.strip()) >= 50)

    def _prepare_llm_prompt(self, text: str) -> str:
        """Prepare structured prompt for LLM analysis"""
        truncated_text = text[:self.MAX_PROMPT_LENGTH]

        return (
            "OUTPUT FORMAT: JSON ONLY\n\n"
            "Rate the README quality and return this JSON format:\n\n"
            "{\n"
            '  "quality_of_example_code": (0.0 - 1.0),\n'
            '  "readme_coverage": (0.0 - 1.0),\n'
            '  "notes": "Good examples, clear docs"\n'
            "}\n\n"
            "Scoring Guidelines (0.0 to 1.0 for each metric):\n\n"
            "quality_of_example_code:\n"
            "- 0.9-1.0: Comprehensive runnable examples with explanations\n"
            "- 0.7-0.9: Multiple working examples with clear usage\n"
            "- 0.5-0.7: Basic usage examples present\n"
            "- 0.3-0.5: Minimal examples or code snippets\n"
            "- 0.0-0.3: No examples or very unclear\n\n"
            "readme_coverage:\n"
            "- 0.9-1.0: Installation, usage, API docs, troubleshooting\n"
            "- 0.7-0.9: Installation, usage, basic API documentation\n"
            "- 0.5-0.7: Installation and basic usage instructions\n"
            "- 0.3-0.5: Minimal documentation\n"
            "- 0.0-0.3: Very sparse or missing key sections\n\n"
            "IMPORTANT: Be generous - if documentation exists and is "
            "reasonably clear, score should be >= 0.5 for each metric. "
            "Well-documented projects should receive 0.7+ scores.\n\n"
            f"ANALYZE THIS README:\n{truncated_text}\n\n"
            "RESPOND WITH JSON ONLY:"
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
        print(f"[RampupEvaluator] LLM response: {content[:100]}...")

        return content

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse and validate LLM response"""
        try:
            if not response_text or not response_text.strip():
                print("[RampupEvaluator] Warning: Empty LLM response")
                raise ValueError("Empty response from LLM")

            # Clean markdown formatting
            clean_response = self._clean_markdown(response_text)

            # Parse JSON
            obj = json.loads(clean_response)

            # Handle array values - take first if array
            quality_val = obj.get("quality_of_example_code", 0.0)
            if isinstance(quality_val, list) and quality_val:
                quality_val = quality_val[0]

            readme_val = obj.get("readme_coverage", 0.0)
            if isinstance(readme_val, list) and readme_val:
                readme_val = readme_val[0]

            return {
                "quality_of_example_code": float(quality_val),
                "readme_coverage": float(readme_val),
                "notes": str(obj.get("notes", ""))[:self.MAX_NOTES_LENGTH],
            }

        except (json.JSONDecodeError, ValueError) as e:
            print(f"[RampupEvaluator] Warning: Parse error: {e}")
            print(f"[RampupEvaluator] Raw response: {response_text[:200]}...")
            raise

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

    def _calculate_score(self, parsed_result: Dict[str, Any]) -> float:
        """Calculate final score from parsed result"""
        score = 0.0
        score += parsed_result["quality_of_example_code"]
        score += parsed_result["readme_coverage"]

        # Normalize to 0-1 range (sum of two 0-1.0 scores = 0-2.0)
        normalized_score = score / 2.0

        return max(0.0, min(1.0, normalized_score))

    def _create_success_result(
        self,
        parsed_result: Dict[str, Any],
        score: float,
        latency: float
    ) -> Dict[str, Any]:
        """Create successful evaluation result"""
        print(f"[RampupEvaluator] Ramp-up Score: {score}")

        return {
            'metric_name': 'ramp_up',
            'score': score,
            'latency': round(latency, 3),
            'details': {
                'mode': 'llm',
                **parsed_result,
                'evaluator': 'RampupEvaluator'
            }
        }

    def _create_insufficient_text_result(
        self, latency: float
    ) -> Dict[str, Any]:
        """Create result for insufficient documentation"""
        print("[RampupEvaluator] Insufficient text for LLM analysis")
        return {
            'metric_name': 'ramp_up',
            'score': 0.0,
            'latency': round(latency, 3),
            'details': {
                'mode': 'llm',
                'notes': 'Insufficient documentation for analysis',
                'evaluator': 'RampupEvaluator'
            }
        }

    def _create_error_result(
        self, error_msg: str, metadata, latency: float
    ) -> Dict[str, Any]:
        """Create fallback result when LLM evaluation fails"""
        # Simple heuristic fallback with more generous scoring
        readme_path = getattr(metadata, 'readme_path', None)
        repo_contents = getattr(metadata, 'repo_contents', [])

        score = 0.0

        # More generous base score for having a README
        if readme_path:
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    readme_content = f.read()
                    readme_len = len(readme_content)

                    # Score based on README length and content
                    if readme_len > 2000:
                        score += 0.6  # Substantial README
                    elif readme_len > 500:
                        score += 0.5  # Decent README
                    elif readme_len > 100:
                        score += 0.3  # Minimal README
                    else:
                        score += 0.1  # Very minimal

                    # Bonus for common documentation keywords
                    content_lower = readme_content.lower()
                    if any(keyword in content_lower for keyword in
                           ['install', 'usage', 'example', 'getting started']):
                        score += 0.2

            except Exception:
                score += 0.4  # Default if can't read

        # Check for examples or docs folder
        if isinstance(repo_contents, list):
            for item in repo_contents:
                if isinstance(item, dict):
                    name = item.get('name', '').lower()
                    if 'example' in name or 'demo' in name:
                        score += 0.15
                    if 'docs' in name or 'documentation' in name:
                        score += 0.1

        score = min(score, 1.0)

        print(f"[RampupEvaluator] Using fallback score: {score}")

        return {
            'metric_name': 'ramp_up',
            'score': score,
            'latency': round(latency, 3),
            'details': {
                'mode': 'fallback',
                'error': error_msg,
                'has_readme': bool(readme_path),
                'has_examples': score > 0.5,
                'evaluator': 'RampupEvaluator'
            }
        }


# Pipeline integration function
def evaluate_rampup(context):
    """
    Evaluate ramp-up time using LLM-based analysis
    Args:
        context: Pipeline context containing metadata
    Returns:
        dict: Evaluation result with metric name and score
    """
    metadata = context.get('last') if isinstance(context, dict) else context
    evaluator = RampupEvaluator()
    return evaluator.evaluate(metadata)

"""
Dataset and Code Availability Evaluation Job
Evaluates availability of datasets and code using LLM analysis
"""
import json
import time
from typing import Dict, Any, Optional
from ..providers.LLMAgent import LLMAgent


class AvailabilityEvaluator:
    """
    Job class for evaluating dataset and code availability
    using LLM-based analysis following clean architecture principles.
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
        Main evaluation method for dataset and code availability
        Args:
            metadata: Model metadata object
        Returns:
            dict: Evaluation result with metric_name, score, and details
        """
        start_time = time.time()
        try:
            print("[AvailabilityEvaluator] Starting evaluation...")

            # Extract and compose source text
            text = self._compose_source_text(metadata)

            if not self._is_text_sufficient(text):
                latency = time.time() - start_time
                return self._create_insufficient_text_result(latency)

            # Prepare LLM prompt
            prompt = self._prepare_llm_prompt(text)

            # Send to LLM
            response = self._send_to_llm(prompt)

            # Parse and validate response
            parsed_result = self._parse_llm_response(response)

            # Calculate score
            score = self._calculate_score(parsed_result)

            # Create final result
            latency = time.time() - start_time
            return self._create_success_result(parsed_result, score, latency)

        except Exception as e:
            print(f"[AvailabilityEvaluator] Error during evaluation: {e}")
            import traceback
            traceback.print_exc()
            latency = time.time() - start_time
            return self._create_error_result(str(e), latency)

    def _compose_source_text(self, metadata) -> str:
        """
        Extract and compose documentation text from README and model card
        """
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
                f"[AvailabilityEvaluator] "
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
            "OUTPUT FORMAT: JSON ONLY\n\n"
            "Check for dataset and code references. "
            "Return this JSON format:\n\n"
            "{\n"
            '  "lists_training_datasets": true,\n'
            '  "links_to_huggingface_datasets": false,\n'
            '  "links_to_code_repo": true,\n'
            '  "notes": "Found dataset names and GitHub links"\n'
            "}\n\n"
            "Criteria:\n"
            "- lists_training_datasets: true if mentions specific "
            "dataset names\n"
            "- links_to_huggingface_datasets: true if has "
            "huggingface.co/datasets/ URLs\n"
            "- links_to_code_repo: true if has GitHub/GitLab "
            "repository links\n\n"
            f"ANALYZE THIS TEXT:\n{truncated_text}\n\n"
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
        print(f"[AvailabilityEvaluator] LLM response: {content[:100]}...")

        return content

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse and validate LLM response"""
        try:
            if not response_text or not response_text.strip():
                print("[AvailabilityEvaluator] Warning: Empty LLM response")
                return self._get_default_parsed_result()

            # Clean markdown formatting
            clean_response = self._clean_markdown(response_text)

            # Parse JSON
            obj = json.loads(clean_response)

            return {
                "lists_training_datasets": bool(
                    obj.get("lists_training_datasets", False)
                ),
                "links_to_huggingface_datasets": bool(
                    obj.get("links_to_huggingface_datasets", False)
                ),
                "links_to_code_repo": bool(
                    obj.get("links_to_code_repo", False)
                ),
                "notes": str(obj.get("notes", ""))[:self.MAX_NOTES_LENGTH],
            }

        except json.JSONDecodeError as e:
            print(f"[AvailabilityEvaluator] Warning: JSON parse error: {e}")
            print(
                f"[AvailabilityEvaluator] "
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
            "lists_training_datasets": False,
            "links_to_huggingface_datasets": False,
            "links_to_code_repo": False,
            "notes": "Failed to parse LLM response"
        }

    def _calculate_score(self, parsed_result: Dict[str, Any]) -> float:
        """Calculate final score from parsed result"""
        score = 0.0
        if parsed_result["lists_training_datasets"]:
            score += 0.3
        if parsed_result["links_to_huggingface_datasets"]:
            score += 0.3
        if parsed_result["links_to_code_repo"]:
            score += 0.4

        return min(1.0, score)

    def _create_success_result(
        self,
        parsed_result: Dict[str, Any],
        score: float,
        latency: float
    ) -> Dict[str, Any]:
        """Create successful evaluation result"""
        print(f"[AvailabilityEvaluator] Availability Score: {score}")

        return {
            'metric_name': 'availability',
            'score': score,
            'latency': round(latency, 3),
            'details': {
                'mode': 'llm',
                **parsed_result,
                'evaluator': 'AvailabilityEvaluator'
            }
        }

    def _create_insufficient_text_result(
        self, latency: float
    ) -> Dict[str, Any]:
        """Create result for insufficient documentation"""
        print("[AvailabilityEvaluator] Insufficient text for LLM analysis")
        return {
            'metric_name': 'availability',
            'score': 0.0,
            'latency': round(latency, 3),
            'details': {
                'mode': 'llm',
                'notes': 'Insufficient documentation for analysis',
                'evaluator': 'AvailabilityEvaluator'
            }
        }

    def _create_error_result(
        self, error_msg: str, latency: float
    ) -> Dict[str, Any]:
        """Create fallback result when LLM evaluation fails"""
        print("[AvailabilityEvaluator] Using fallback score: 0.0")

        return {
            'metric_name': 'availability',
            'score': 0.0,
            'latency': round(latency, 3),
            'details': {
                'mode': 'fallback',
                'error': error_msg,
                'evaluator': 'AvailabilityEvaluator'
            }
        }


# Pipeline integration function
def evaluate_availability(context):
    """
    Evaluate dataset and code availability using LLM-based analysis
    Args:
        context: Pipeline context containing metadata
    Returns:
        dict: Evaluation result with metric name and score
    """
    metadata = context.get('last') if isinstance(context, dict) else context
    evaluator = AvailabilityEvaluator()
    return evaluator.evaluate(metadata)

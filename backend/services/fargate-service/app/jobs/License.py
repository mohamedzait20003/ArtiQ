"""
License Evaluation Job
Evaluates license permissiveness using rule-based and LLM analysis
"""
import json
import time
import logging
from typing import Dict, Any, Optional, Tuple
from app.bootstrap import get_llm_agent

# Configure logger for CloudWatch
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LicenseEvaluator:
    """
    Job class for evaluating license permissiveness using rule-based
    classification and LLM analysis following clean architecture.
    """

    # Constants
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 4096
    MAX_LICENSE_TEXT = 500
    MAX_LLM_TEXT = 2000

    def __init__(self, llm_agent=None):
        """Initialize with optional LLMAgent instance"""
        self.llm_agent = llm_agent or get_llm_agent()

    def evaluate(self, metadata) -> Dict[str, Any]:
        """
        Main evaluation method for license permissiveness
        Args:
            metadata: Model metadata object
        Returns:
            dict: Evaluation result with metric_name, score, and details
        """
        start_time = time.time()
        try:
            logger.info("[LICENSE] Starting evaluation")
            print("[LicenseEvaluator] Starting evaluation...")

            # Extract license information from all sources
            license_text = self._get_license_info(metadata)
            logger.info(
                f"[LICENSE] Extracted license text "
                f"(length: {len(license_text) if license_text else 0})"
            )

            # Attempt rule-based classification first
            score, classification_type, reason = self._classify_license(
                license_text
            )

            if score is not None:
                # Successfully classified with rules
                logger.info(
                    f"[LICENSE] Rule-based classification: "
                    f"score={score:.3f}, type={classification_type}"
                )
                latency = time.time() - start_time
                return self._create_rule_based_result(
                    score, license_text, reason, latency
                )
            else:
                # Need LLM analysis for custom license
                if not license_text:
                    logger.warning("[LICENSE] No license text found")
                    latency = time.time() - start_time
                    return self._create_no_license_result(latency)

                logger.info("[LICENSE] Using LLM analysis for custom license")
                latency_before_llm = time.time() - start_time
                return self._analyze_with_llm(license_text, latency_before_llm)

        except Exception as e:
            logger.error(
                f"[LICENSE] Error during evaluation: {e}",
                exc_info=True
            )
            print(f"[LicenseEvaluator] Error during evaluation: {e}")
            import traceback
            traceback.print_exc()
            latency = time.time() - start_time
            return self._create_error_result(str(e), latency)

    def _get_license_info(self, metadata) -> str:
        """Extract license information from all available sources"""
        license_info = []

        # DEBUG: Log metadata structure
        logger.info(f"[LICENSE] Metadata type: {type(metadata)}")
        logger.info(f"[LICENSE] Metadata attributes: {dir(metadata)}")
        
        # Priority 1: Check HuggingFace info.license (most common)
        hf_info = getattr(metadata, "info", None)
        logger.info(f"[LICENSE] info object: {hf_info}")
        logger.info(f"[LICENSE] info type: {type(hf_info)}")
        
        if hf_info:
            logger.info(f"[LICENSE] info attributes: {dir(hf_info)}")
            
            # Try different ways to access license
            license_field = None
            
            # Method 1: Direct attribute
            if hasattr(hf_info, "license"):
                license_field = getattr(hf_info, "license", None)
                logger.info(f"[LICENSE] Found via hasattr: {license_field}")
            
            # Method 2: Dict access if info is dict-like
            if not license_field and isinstance(hf_info, dict):
                license_field = hf_info.get("license")
                logger.info(f"[LICENSE] Found via dict.get: {license_field}")
            
            # Method 3: Try to access as property
            if not license_field:
                try:
                    license_field = hf_info.license
                    logger.info(f"[LICENSE] Found via property: {license_field}")
                except AttributeError:
                    logger.info("[LICENSE] No license property on info")
            
            if license_field:
                logger.info(f"[LICENSE] Found in info.license: {license_field}")
                license_info.append(f"license: {license_field}")

        # Priority 2: Check direct license attribute
        direct_license = getattr(metadata, "license", None)
        if direct_license:
            logger.info(f"[LICENSE] Found in direct attribute: {direct_license}")
            license_info.append(f"license: {direct_license}")

        # Priority 3: Check model card for license information
        card_obj = getattr(metadata, "card", None)
        logger.info(f"[LICENSE] card object: {card_obj}")
        logger.info(f"[LICENSE] card type: {type(card_obj)}")
        
        if card_obj:
            # Try multiple ways to access card data
            card_dict = None
            
            # Method 1: If it's already a dict
            if isinstance(card_obj, dict):
                card_dict = card_obj
                logger.info("[LICENSE] Card is dict")
            
            # Method 2: If it has a to_dict method
            elif hasattr(card_obj, 'to_dict'):
                card_dict = card_obj.to_dict()
                logger.info("[LICENSE] Card converted via to_dict()")
            
            # Method 3: If it's a ModelCard/CardData object with data attribute
            elif hasattr(card_obj, 'data'):
                card_dict = card_obj.data
                logger.info("[LICENSE] Card accessed via .data")
            
            # Method 4: Try accessing as dict-like object
            elif hasattr(card_obj, '__getitem__'):
                try:
                    license_val = card_obj['license']
                    if license_val:
                        logger.info(f"[LICENSE] Found via card['license']: {license_val}")
                        license_info.append(f"license: {license_val}")
                except (KeyError, TypeError):
                    pass
            
            # Method 5: Try as object attributes
            if hasattr(card_obj, 'license'):
                license_val = getattr(card_obj, 'license', None)
                if license_val:
                    logger.info(f"[LICENSE] Found via card.license: {license_val}")
                    license_info.append(f"license: {license_val}")
            
            # Process card_dict if we got one
            if card_dict and isinstance(card_dict, dict):
                license_fields = [
                    "license", "license_name",
                    "license_link", "license_url"
                ]
                for field in license_fields:
                    if field in card_dict and card_dict[field]:
                        logger.info(f"[LICENSE] Found in card_dict.{field}: {card_dict[field]}")
                        license_info.append(f"{field}: {card_dict[field]}")

                # Check description for license mentions
                description = card_dict.get("description", "")
                license_words = [
                    "license", "mit", "apache", "bsd", "gpl", "lgpl"
                ]
                if description and any(
                    word in description.lower() for word in license_words
                ):
                    license_info.append(f"description: {description}")

        # Priority 4: Check repository metadata for license
        repo_metadata = getattr(metadata, "repo_metadata", {})
        if isinstance(repo_metadata, dict):
            repo_license = repo_metadata.get("license")
            if repo_license:
                if isinstance(repo_license, dict):
                    # GitHub API license object
                    license_name = repo_license.get("name", "")
                    license_key = repo_license.get("key", "")
                    if license_name or license_key:
                        logger.info(
                            f"[LICENSE] Found in repo_metadata: "
                            f"{license_name} ({license_key})"
                        )
                        license_info.append(
                            f"repo_license: {license_name} ({license_key})"
                        )
                else:
                    # Simple license string
                    logger.info(f"[LICENSE] Found in repo_metadata: {repo_license}")
                    license_info.append(f"repo_license: {repo_license}")

        if not license_info:
            logger.warning("[LICENSE] No license found in any metadata field")

        result = "\n".join(license_info) if license_info else ""
        logger.info(f"[LICENSE] Final extracted license text: {result}")
        return result

    def _classify_license(self, license_text: str) -> Tuple[
        Optional[float], str, str
    ]:
        """Classify license and return (score, type, reason)"""
        if not license_text:
            return 0.0, "rule_based", "No license information found"

        license_lower = license_text.lower()

        # PERMISSIVE LICENSES -> 1.0 (EXACTLY 1.0!)
        permissive_licenses = {
            "mit": "MIT License",
            "bsd": "BSD License",
            "bsd-2-clause": "BSD 2-Clause License",
            "bsd-3-clause": "BSD 3-Clause License",
            "apache": "Apache License",
            "apache-2.0": "Apache License 2.0",
            "apache 2.0": "Apache License 2.0",
            "lgpl-2.1": "LGPL v2.1",
            "lgpl v2.1": "LGPL v2.1",
            "lgpl-3.0": "LGPL v3.0",
            "lgpl v3.0": "LGPL v3.0",
            "isc": "ISC License",
            "unlicense": "Unlicense"
        }

        for license_key, license_name in permissive_licenses.items():
            if license_key in license_lower:
                return (
                    1.0, "rule_based",
                    f"Permissive license: {license_name}"
                )

        # RESTRICTIVE/INCOMPATIBLE LICENSES -> 0.0 (EXACTLY 0.0!)
        restrictive_licenses = {
            "gpl-2.0": "GPL v2.0",
            "gpl v2.0": "GPL v2.0",
            "gpl-3.0": "GPL v3.0",
            "gpl v3.0": "GPL v3.0",
            "cc by-nc": "Creative Commons Non-Commercial",
            "cc-by-nc": "Creative Commons Non-Commercial",
            "non-commercial": "Non-Commercial License",
            "proprietary": "Proprietary License",
            "all rights reserved": "All Rights Reserved"
        }

        for license_key, license_name in restrictive_licenses.items():
            if license_key in license_lower:
                return (
                    0.0, "rule_based",
                    f"Restrictive license: {license_name}"
                )

        # If contains license keywords but unclassified -> use LLM
        license_keywords = ["license", "copyright", "terms", "conditions"]
        if any(keyword in license_lower for keyword in license_keywords):
            return (
                None, "llm_needed",
                "Custom license requires LLM analysis"
            )

        # No clear license information -> 0.0
        return (
            0.0, "rule_based",
            "Unclear or missing license information"
        )

    def _analyze_with_llm(
        self, license_text: str, prior_latency: float
    ) -> Dict[str, Any]:
        """Analyze custom license using LLM"""
        try:
            prompt = self._prepare_llm_prompt(license_text)
            response = self._send_to_llm(prompt)
            parsed = self._parse_llm_response(response)

            # Ensure score is within valid range [0.0, 1.0]
            llm_score = max(0.0, min(1.0, parsed["permissiveness_score"]))

            print(f"[LicenseEvaluator] LLM License Score: {llm_score}")

            return {
                'metric_name': 'license',
                'score': llm_score,
                'latency': round(prior_latency, 3),
                'details': {
                    'classification_method': 'llm_analysis',
                    'license_text': license_text[:self.MAX_LICENSE_TEXT],
                    'llm_analysis': parsed,
                    'evaluator': 'LicenseEvaluator'
                }
            }

        except Exception as e:
            print(f"[LicenseEvaluator] LLM analysis failed: {e}")
            return self._create_error_result(str(e), prior_latency)

    def _prepare_llm_prompt(self, license_text: str) -> str:
        """Prepare LLM prompt for custom license analysis"""
        truncated_text = license_text[:self.MAX_LLM_TEXT]

        return (
            "OUTPUT FORMAT: JSON ONLY\n\n"
            "Analyze this license text for permissiveness. "
            "Return this JSON format:\n\n"
            "{\n"
            '  "permissiveness_score": 0.7,\n'
            '  "license_type": "Custom permissive",\n'
            '  "allows_commercial": true,\n'
            '  "allows_modification": true,\n'
            '  "notes": "Allows commercial use with attribution"\n'
            "}\n\n"
            "Scoring rules (STRICT):\n"
            "- 1.0: MIT/Apache/BSD-like (very permissive)\n"
            "- 0.8-0.9: Permissive with minor restrictions\n"
            "- 0.5-0.7: Some commercial/modification limits\n"
            "- 0.1-0.4: Significant restrictions\n"
            "- 0.0: GPL/Non-commercial/Highly restrictive\n\n"
            f"LICENSE TEXT:\n{truncated_text}\n\n"
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
        print(f"[LicenseEvaluator] LLM response: {content[:100]}...")

        return content

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response for license analysis"""
        try:
            # Clean markdown formatting
            clean_response = self._clean_markdown(response_text)

            obj = json.loads(clean_response)
            return {
                "permissiveness_score": float(
                    obj.get("permissiveness_score", 0.0)
                ),
                "license_type": str(obj.get("license_type", "Unknown")),
                "allows_commercial": bool(
                    obj.get("allows_commercial", False)
                ),
                "allows_modification": bool(
                    obj.get("allows_modification", False)
                ),
                "notes": str(obj.get("notes", ""))[:200],
            }
        except Exception as e:
            print(f"[LicenseEvaluator] Parse error: {e}")
            return {
                "permissiveness_score": 0.0,
                "license_type": "Parse error",
                "allows_commercial": False,
                "allows_modification": False,
                "notes": "Failed to parse LLM response"
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

    def _create_rule_based_result(
        self,
        score: float,
        license_text: str,
        reason: str,
        latency: float
    ) -> Dict[str, Any]:
        """Create result from rule-based classification"""
        print(f"[LicenseEvaluator] Rule-based License Score: {score}")
        print(f"[LicenseEvaluator] Reason: {reason}")

        return {
            'metric_name': 'license',
            'score': score,
            'latency': round(latency, 3),
            'details': {
                'classification_method': 'rule_based',
                'license_text': license_text[:self.MAX_LICENSE_TEXT]
                if license_text else "",
                'reason': reason,
                'evaluator': 'LicenseEvaluator'
            }
        }

    def _create_no_license_result(self, latency: float) -> Dict[str, Any]:
        """Create result for missing license information"""
        print("[LicenseEvaluator] No license information available")
        return {
            'metric_name': 'license',
            'score': 0.0,
            'latency': round(latency, 3),
            'details': {
                'error': 'No license information available',
                'evaluator': 'LicenseEvaluator'
            }
        }

    def _create_error_result(
        self, error_msg: str, latency: float
    ) -> Dict[str, Any]:
        """Create fallback result when evaluation fails"""
        print("[LicenseEvaluator] Using fallback score: 0.0")

        return {
            'metric_name': 'license',
            'score': 0.0,
            'latency': round(latency, 3),
            'details': {
                'mode': 'fallback',
                'error': error_msg,
                'evaluator': 'LicenseEvaluator'
            }
        }


# Pipeline integration function
def evaluate_license(context):
    """
    Evaluate license permissiveness using rule-based and LLM analysis
    Args:
        context: Pipeline context containing metadata
    Returns:
        dict: Evaluation result with metric name and score
    """
    metadata = context.get('last') if isinstance(context, dict) else context
    evaluator = LicenseEvaluator()
    return evaluator.evaluate(metadata)

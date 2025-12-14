"""
Code Quality Evaluation Job
Evaluates code quality through tests, structure, and documentation
"""
import json
import time
import logging
from typing import Dict, Any, List
from app.bootstrap import get_llm_agent

# Configure logger for CloudWatch
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class CodeQualityEvaluator:
    """
    Job class for evaluating code quality based on tests, structure,
    and documentation following clean architecture principles.
    """

    # Constants
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 4096
    MAX_REPO_ITEMS = 50

    def __init__(self, llm_agent=None):
        """Initialize with optional LLMAgent instance"""
        self.llm_agent = llm_agent or get_llm_agent()

    def evaluate(self, metadata) -> Dict[str, Any]:
        """
        Main evaluation method for code quality
        Args:
            metadata: Model metadata object
        Returns:
            dict: Evaluation result with metric_name, score, and details
        """
        start_time = time.time()
        try:
            logger.info("[CODE_QUALITY] Starting evaluation")
            print("[CodeQualityEvaluator] Starting evaluation...")

            # Extract repository contents
            repo_contents = getattr(metadata, "repo_contents", [])
            logger.info(
                f"[CODE_QUALITY] Found {len(repo_contents)} repo items"
            )
            logger.info(
                f"[CODE_QUALITY] repo_contents type: {type(repo_contents)}"
            )
            if repo_contents and len(repo_contents) > 0:
                logger.info(
                    f"[CODE_QUALITY] First 3 items: "
                    f"{repo_contents[:3]}"
                )

            if not isinstance(repo_contents, list):
                logger.warning(
                    "[CODE_QUALITY] repo_contents is not a list"
                )
                latency = time.time() - start_time
                return self._create_no_repo_result(latency)

            # Check for test files
            has_tests = self._check_test_files(repo_contents)
            logger.info(f"[CODE_QUALITY] Has tests: {has_tests}")

            # Check for dependency management
            has_dependency_mgmt = self._check_dependency_management(
                repo_contents
            )
            logger.info(
                f"[CODE_QUALITY] Has dependency mgmt: "
                f"{has_dependency_mgmt}"
            )

            # Analyze code with LLM
            logger.info("[CODE_QUALITY] Running LLM analysis")
            llm_analysis = self._analyze_code_with_llm(repo_contents)
            logger.info(
                f"[CODE_QUALITY] LLM analysis: {llm_analysis}"
            )

            # Calculate score
            score = self._calculate_score(
                has_tests,
                has_dependency_mgmt,
                llm_analysis
            )
            logger.info(f"[CODE_QUALITY] Final score: {score:.3f}")

            # Create final result
            latency = time.time() - start_time
            logger.info(
                f"[CODE_QUALITY] Evaluation complete "
                f"(latency: {latency:.3f}s)"
            )
            return self._create_success_result(
                score,
                has_tests,
                has_dependency_mgmt,
                llm_analysis,
                latency
            )

        except Exception as e:
            logger.error(
                f"[CODE_QUALITY] Error during evaluation: {e}",
                exc_info=True
            )
            print(f"[CodeQualityEvaluator] Error during evaluation: {e}")
            import traceback
            traceback.print_exc()
            latency = time.time() - start_time
            return self._create_error_result(str(e), latency)

    def _check_test_files(self, repo_contents: List) -> bool:
        """Check if repository contains test files"""
        if not isinstance(repo_contents, list):
            return False

        test_indicators = [
            'test', 'tests', 'testing', 'unittest', 'unit_test',
            'test_', '_test', 'spec', 'specs'
        ]

        for item in repo_contents:
            if isinstance(item, dict):
                name = item.get('name', '').lower()
                path = item.get('path', '').lower()

                for indicator in test_indicators:
                    if (indicator in name or indicator in path or
                            name.startswith('test_') or
                            name.endswith('_test.py') or
                            name.endswith('_test') or
                            'test.py' in name):
                        return True
        return False

    def _check_dependency_management(self, repo_contents: List) -> bool:
        """Check if repository has dependency management files"""
        if not isinstance(repo_contents, list):
            return False

        dependency_files = [
            'requirements.txt', 'setup.py', 'pyproject.toml',
            'pipfile', 'poetry.lock', 'conda.yml', 'environment.yml'
        ]

        for item in repo_contents:
            if isinstance(item, dict):
                name = item.get('name', '').lower()
                if name in dependency_files:
                    return True
        return False

    def _analyze_code_with_llm(self, repo_contents: List) -> Dict[str, Any]:
        """Analyze code structure using LLM"""
        repo_summary = []
        for item in repo_contents[:self.MAX_REPO_ITEMS]:
            if isinstance(item, dict):
                name = item.get('name', '')
                item_type = item.get('type', '')
                repo_summary.append(f"{item_type}: {name}")

        repo_text = "\n".join(repo_summary)
        
        logger.info(
            f"[CODE_QUALITY] Repo summary lines: {len(repo_summary)}"
        )
        logger.info(
            f"[CODE_QUALITY] Repo text preview: {repo_text[:200]}..."
        )

        prompt = (
            "CRITICAL: You MUST respond with ONLY valid JSON. "
            "No explanations, no markdown, no code blocks.\n\n"
            "Task: Analyze this repository structure for code quality. "
            "Return EXACTLY this JSON structure:\n\n"
            "{\n"
            '  "has_comprehensive_tests": true|false,\n'
            '  "shows_good_structure": true|false,\n'
            '  "has_documentation": true|false,\n'
            '  "notes": "analysis summary"\n'
            "}\n\n"
            "Rules:\n"
            "1. ONLY return JSON - nothing else\n"
            "2. Use true/false (lowercase) for booleans\n"
            "3. Keep notes under 30 characters\n\n"
            "Evaluation criteria:\n"
            "- has_comprehensive_tests: Are there test files covering "
            "multiple components?\n"
            "- shows_good_structure: Well-organized directories and "
            "separation of concerns?\n"
            "- has_documentation: README, docs, or documentation "
            "files present?\n\n"
            "Repository structure:\n"
            f"{repo_text}\n\n"
            "Remember: ONLY return the JSON object."
        )

        try:
            response = self.llm_agent.send_prompt(
                prompt=prompt,
                temperature=self.DEFAULT_TEMPERATURE,
                max_tokens=self.DEFAULT_MAX_TOKENS
            )

            if not response.get('success', False):
                return self._get_default_llm_analysis()

            content = response.get('content', '')
            print(
                f"[CodeQualityEvaluator] LLM response: {content[:100]}..."
            )

            # Clean and parse response
            clean_response = self._clean_markdown(content)
            obj = json.loads(clean_response)

            return {
                "has_comprehensive_tests": bool(
                    obj.get("has_comprehensive_tests", False)
                ),
                "shows_good_structure": bool(
                    obj.get("shows_good_structure", False)
                ),
                "has_documentation": bool(
                    obj.get("has_documentation", False)
                ),
                "notes": str(obj.get("notes", ""))[:400],
            }
        except Exception as e:
            print(f"[CodeQualityEvaluator] LLM analysis failed: {e}")
            return self._get_default_llm_analysis()

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

    def _get_default_llm_analysis(self) -> Dict[str, Any]:
        """Get default LLM analysis for errors"""
        return {
            "has_comprehensive_tests": False,
            "shows_good_structure": False,
            "has_documentation": False,
            "notes": "LLM analysis failed"
        }

    def _calculate_score(
        self,
        has_tests: bool,
        has_dependency_mgmt: bool,
        llm_analysis: Dict[str, Any]
    ) -> float:
        """Calculate final score from analysis results"""
        score = 0.0
        if has_tests:
            score += 0.35

        if llm_analysis["shows_good_structure"]:
            score += 0.30
        if has_dependency_mgmt:
            score += 0.25
        if llm_analysis["has_documentation"]:
            score += 0.10

        # Give base score for basic code quality indicators
        if has_dependency_mgmt or llm_analysis["shows_good_structure"]:
            score = max(0.4, score)

        return min(1.0, score)

    def _create_success_result(
        self,
        score: float,
        has_tests: bool,
        has_dependency_mgmt: bool,
        llm_analysis: Dict[str, Any],
        latency: float
    ) -> Dict[str, Any]:
        """Create successful evaluation result"""
        print(f"[CodeQualityEvaluator] Code Quality Score: {score}")

        return {
            'metric_name': 'code_quality',
            'score': score,
            'latency': round(latency, 3),
            'details': {
                'has_tests': has_tests,
                'has_dependency_management': has_dependency_mgmt,
                'lint_check_proxy': llm_analysis["shows_good_structure"],
                'llm_analysis': llm_analysis,
                'evaluator': 'CodeQualityEvaluator'
            }
        }

    def _create_no_repo_result(self, latency: float) -> Dict[str, Any]:
        """Create result for missing repository contents"""
        print("[CodeQualityEvaluator] No repository contents available")
        return {
            'metric_name': 'code_quality',
            'score': 0.0,
            'latency': round(latency, 3),
            'details': {
                'error': 'No repository contents available',
                'evaluator': 'CodeQualityEvaluator'
            }
        }

    def _create_error_result(
        self, error_msg: str, latency: float
    ) -> Dict[str, Any]:
        """Create fallback result when evaluation fails"""
        print("[CodeQualityEvaluator] Using fallback score: 0.0")

        return {
            'metric_name': 'code_quality',
            'score': 0.0,
            'latency': round(latency, 3),
            'details': {
                'mode': 'fallback',
                'error': error_msg,
                'evaluator': 'CodeQualityEvaluator'
            }
        }


# Pipeline integration function
def evaluate_code_quality(context):
    """
    Evaluate code quality based on tests, structure, and documentation
    Args:
        context: Pipeline context containing metadata
    Returns:
        dict: Evaluation result with metric name and score
    """
    metadata = context.get('last') if isinstance(context, dict) else context
    evaluator = CodeQualityEvaluator()
    return evaluator.evaluate(metadata)

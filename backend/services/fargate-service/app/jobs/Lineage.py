"""
Lineage Evaluation Job
Reports the lineage graph of a model from structured metadata
"""
import time
import logging
from typing import Dict, Any

# Configure logger for CloudWatch
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LineageEvaluator:
    """
    Job class for extracting and reporting model lineage information
    from config.json and other metadata sources
    """

    def __init__(self):
        """Initialize the Lineage Evaluator"""
        pass

    def evaluate(self, metadata) -> Dict[str, Any]:
        """
        Main evaluation method for lineage extraction

        Args:
            metadata: Model metadata object

        Returns:
            dict: Evaluation result with lineage information
        """
        start_time = time.time()
        try:
            logger.info("[LINEAGE] Starting lineage extraction")
            print("[LineageEvaluator] Starting lineage extraction...")

            # Extract lineage from various metadata sources
            lineage_graph = self._extract_lineage(metadata)

            logger.info(
                f"[LINEAGE] Extracted lineage with "
                f"{len(lineage_graph.get('parents', []))} parent(s)"
            )

            # Create result
            latency = time.time() - start_time
            logger.info(
                f"[LINEAGE] Extraction complete (latency: {latency:.3f}s)"
            )
            return self._create_success_result(lineage_graph, latency)

        except Exception as e:
            logger.error(
                f"[LINEAGE] Error during extraction: {e}",
                exc_info=True
            )
            print(f"[LineageEvaluator] Error during extraction: {e}")
            import traceback
            traceback.print_exc()
            latency = time.time() - start_time
            return self._create_error_result(str(e), latency)

    def _extract_lineage(self, metadata) -> Dict[str, Any]:
        """
        Extract lineage information from metadata

        Args:
            metadata: Model metadata object

        Returns:
            dict: Lineage graph with parents list and metadata
        """
        lineage = {
            'parents': [],
            'base_model': None,
            'model_type': None,
            'architecture': None
        }

        # Get model info directly
        info = getattr(metadata, 'info', None)
        card = getattr(metadata, 'card', None)

        # Process ModelInfo object
        if info:
            # Get config
            config = getattr(info, 'config', {})
            if isinstance(config, dict):
                lineage['architecture'] = config.get(
                    'architectures', [None]
                )[0] if config.get('architectures') else None
                lineage['model_type'] = config.get('model_type')

                # Extract base model from various config fields
                base_model = (
                    config.get('_name_or_path') or
                    config.get('base_model') or
                    config.get('base_model_name_or_path')
                )
                if base_model and base_model != '.':
                    lineage['base_model'] = base_model
                    # Add to parents list if it looks like a model ID
                    if '/' in base_model or '-' in base_model:
                        lineage['parents'].append({
                            'model_id': base_model,
                            'source': 'config._name_or_path'
                        })

            # Check card_data from ModelInfo
            card_data = getattr(info, 'card_data', None)
            if card_data:
                # Convert to dict if needed
                if hasattr(card_data, 'to_dict'):
                    card_dict = card_data.to_dict()
                elif isinstance(card_data, dict):
                    card_dict = card_data
                else:
                    card_dict = {}

                # Look for base_model in card
                card_base = card_dict.get('base_model')
                if card_base and card_base not in [
                    p['model_id'] for p in lineage['parents']
                ]:
                    lineage['parents'].append({
                        'model_id': card_base,
                        'source': 'model_card.base_model'
                    })

        # Process ModelCardData object
        if card:
            # Convert to dict
            if hasattr(card, 'to_dict'):
                card_dict = card.to_dict()
            elif isinstance(card, dict):
                card_dict = card
            else:
                card_dict = {}

            # Look for base_model
            card_base = card_dict.get('base_model')
            if card_base and card_base not in [
                p['model_id'] for p in lineage['parents']
            ]:
                lineage['parents'].append({
                    'model_id': card_base,
                    'source': 'model_card.base_model'
                })

            # Look for parent models in tags
            tags = card_dict.get('tags', [])
            if isinstance(tags, list):
                for tag in tags:
                    if isinstance(tag, str) and 'base-model:' in tag:
                        model_id = tag.split('base-model:')[1].strip()
                        if model_id not in [
                            p['model_id'] for p in lineage['parents']
                        ]:
                            lineage['parents'].append({
                                'model_id': model_id,
                                'source': 'model_card.tags'
                            })

        # Check repo metadata for additional lineage info
        repo_metadata = getattr(metadata, 'repo_metadata', {})
        if isinstance(repo_metadata, dict):
            # GitHub repo description might mention base models
            description = repo_metadata.get('description', '')
            if description and isinstance(description, str):
                # Simple pattern matching for common base model mentions
                base_patterns = [
                    'based on',
                    'fine-tuned from',
                    'derived from',
                    'trained on top of'
                ]
                for pattern in base_patterns:
                    if pattern in description.lower():
                        logger.info(
                            f"[LINEAGE] Found potential base model "
                            f"mention in description: '{pattern}'"
                        )
                        # Store pattern for reference
                        lineage['description_mentions'] = pattern

        # Check README content for base model references
        readme = getattr(metadata, 'readme', '')
        if readme and isinstance(readme, str):
            import re
            # Look for model ID patterns after keywords
            patterns = [
                (r'(?:based on|fine-tuned from|derived from|'
                 r'trained on top of)\s+(?:\[)?'
                 r'([a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+)'),
                (r'(?:base model|parent model|original model):'
                 r'\s*(?:\[)?([a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+)'),
                r'(?:https://huggingface\.co/)([a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+)',
            ]
            for pattern in patterns:
                matches = re.findall(pattern, readme.lower(), re.IGNORECASE)
                for match in matches:
                    parent_ids = [p['model_id'] for p in lineage['parents']]
                    if match and match not in parent_ids:
                        lineage['parents'].append({
                            'model_id': match,
                            'source': 'readme'
                        })
                        logger.info(
                            f"[LINEAGE] Found parent in README: {match}"
                        )

        # If no parents found, check if model name suggests derivation
        if not lineage['parents']:
            source_url = getattr(metadata, 'source_url', '')
            if 'distil' in source_url.lower():
                # DistilBERT-like models derive from BERT
                lineage['parents'].append({
                    'model_id': 'inferred-from-name',
                    'source': 'model_name_pattern',
                    'note': 'Distilled model likely has base model parent'
                })

        logger.info(
            f"[LINEAGE] Lineage extraction complete: "
            f"{len(lineage['parents'])} parent(s), "
            f"architecture={lineage.get('architecture')}"
        )

        return lineage

    def _create_success_result(
        self, lineage_graph: Dict[str, Any], latency: float
    ) -> Dict[str, Any]:
        """
        Create successful evaluation result

        Args:
            lineage_graph: Extracted lineage information
            latency: Evaluation time in seconds

        Returns:
            dict: Standardized result dictionary
        """
        parent_count = len(lineage_graph.get('parents', []))
        print(f"[LineageEvaluator] Parents found: {parent_count}")
        print(
            f"[LineageEvaluator] Architecture: "
            f"{lineage_graph.get('architecture', 'unknown')}"
        )

        return {
            'metric_name': 'lineage',
            'lineage_graph': lineage_graph,
            'latency': round(latency, 3),
            'details': {
                'parent_count': parent_count,
                'has_base_model': lineage_graph.get('base_model') is not None,
                'evaluator': 'LineageEvaluator'
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
        print("[LineageEvaluator] Using fallback: empty lineage")

        return {
            'metric_name': 'lineage',
            'lineage_graph': {'parents': []},
            'latency': round(latency, 3),
            'details': {
                'mode': 'fallback',
                'error': error_msg,
                'evaluator': 'LineageEvaluator'
            }
        }


# Pipeline integration function
def evaluate_lineage(context):
    """
    Evaluate model lineage

    Args:
        context: Pipeline context containing metadata

    Returns:
        dict: Evaluation result with lineage information
    """
    metadata = context.get('last') if isinstance(context, dict) else context
    evaluator = LineageEvaluator()
    return evaluator.evaluate(metadata)

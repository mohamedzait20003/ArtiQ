"""
Artifact Lineage Get Job
Retrieves lineage graph for a model artifact
"""
import logging
from typing import List, Dict, Any
from app.models import Artifact_Model

# Configure logger for CloudWatch
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    AWS Lambda handler for GET /artifact/model/{id}/lineage
    Retrieves lineage graph for a model artifact

    Args:
        event: {
            'artifact_id': str - The model artifact ID
        }
        context: Lambda context object

    Returns:
        tuple: (response_data, status_code)
    """
    try:
        logger.info("[LINEAGE] Starting artifact lineage request")

        # Extract artifact_id from event
        artifact_id = event.get('artifact_id')
        logger.info(f"[LINEAGE] Requested artifact ID: {artifact_id}")

        if not artifact_id:
            logger.warning("[LINEAGE] artifact_id is missing from request")
            return (
                {'errorMessage': 'artifact_id is required'},
                400
            )

        # Retrieve the artifact from database
        logger.info(
            f"[LINEAGE] Retrieving artifact from database: {artifact_id}"
        )
        artifact = Artifact_Model.get({'id': artifact_id})

        if not artifact:
            logger.warning(f"[LINEAGE] Artifact not found: {artifact_id}")
            return (
                {'errorMessage': f'Artifact {artifact_id} does not exist'},
                404
            )

        logger.info(
            f"[LINEAGE] Artifact found: {artifact.name} "
            f"(type: {artifact.artifact_type})"
        )

        # Verify it's a model artifact
        if artifact.artifact_type != 'model':
            logger.warning(
                f"[LINEAGE] Artifact type mismatch: expected 'model', "
                f"got '{artifact.artifact_type}'"
            )
            return (
                {
                    'errorMessage':
                        f'Artifact {artifact_id} is not a model artifact'
                },
                400
            )

        # Get rating to access lineage_graph
        logger.info(
            f"[LINEAGE] Fetching rating for artifact {artifact_id}"
        )
        rating_obj = artifact.rating()

        if not rating_obj:
            logger.warning(
                f"[LINEAGE] No rating found for artifact {artifact_id}"
            )
            return (
                {
                    'errorMessage':
                        f'No rating found for artifact {artifact_id}'
                },
                404
            )

        # Extract lineage_graph from rating
        lineage_graph = getattr(rating_obj, 'lineage_graph', None)

        if not lineage_graph:
            logger.warning(
                f"[LINEAGE] No lineage data for artifact {artifact_id}"
            )
            # Return empty lineage structure
            return (
                {
                    'nodes': [],
                    'edges': []
                },
                200
            )

        logger.info(
            f"[LINEAGE] Lineage graph found with "
            f"{len(lineage_graph.get('parents', []))} parents"
        )

        # Transform lineage_graph to nodes/edges format
        nodes: List[Dict[str, Any]] = []
        edges: List[Dict[str, Any]] = []

        # Add current artifact as root node
        nodes.append({
            'artifact_id': artifact_id,
            'name': artifact.name,
            'source': 'current'
        })

        # Process parent models
        parents = lineage_graph.get('parents', [])
        for parent in parents:
            parent_model_id = parent.get('model_id', '')
            parent_source = parent.get('source', 'unknown')

            if not parent_model_id:
                continue

            # Try to find parent artifact by matching model_id
            # in source_url or name
            parent_artifact = _find_artifact_by_model_id(parent_model_id)

            if parent_artifact:
                # Parent exists in our database
                nodes.append({
                    'artifact_id': parent_artifact.id,
                    'name': parent_artifact.name,
                    'source': parent_source
                })

                edges.append({
                    'from_node_artifact_id': parent_artifact.id,
                    'to_node_artifact_id': artifact_id,
                    'relationship': 'parent'
                })
            else:
                # Parent not in database, use placeholder
                nodes.append({
                    'artifact_id': parent_model_id,
                    'name': parent_model_id,
                    'source': parent_source
                })

                edges.append({
                    'from_node_artifact_id': parent_model_id,
                    'to_node_artifact_id': artifact_id,
                    'relationship': 'parent'
                })

        logger.info(
            f"[LINEAGE] Transformed lineage: {len(nodes)} nodes, "
            f"{len(edges)} edges"
        )

        return (
            {
                'nodes': nodes,
                'edges': edges
            },
            200
        )

    except Exception as e:
        logger.error(
            f"[LINEAGE] Error in artifact_lineage_get: {str(e)}",
            exc_info=True
        )
        return (
            {
                'errorMessage':
                    'The lineage metadata is malformed or could not '
                    'be retrieved'
            },
            400
        )


def _find_artifact_by_model_id(model_id: str):
    """
    Find artifact by matching model_id in source_url or name

    Args:
        model_id: Model identifier (e.g., 'microsoft/phi-2')

    Returns:
        Artifact_Model or None
    """
    try:
        # Search for artifacts where source_url or name contains model_id
        artifacts = Artifact_Model.scan(limit=100)

        for artifact in artifacts:
            # Check if model_id appears in source_url
            if artifact.source_url and model_id in artifact.source_url:
                return artifact

            # Check if model_id matches name
            if artifact.name and model_id == artifact.name:
                return artifact

            # Check if model_id is the last part of source_url
            if artifact.source_url:
                url_parts = artifact.source_url.rstrip('/').split('/')
                if len(url_parts) >= 2:
                    owner_repo = f"{url_parts[-2]}/{url_parts[-1]}"
                    if owner_repo == model_id:
                        return artifact

        return None
    except Exception as e:
        logger.error(
            f"[LINEAGE] Error finding artifact by model_id: {str(e)}"
        )
        return None

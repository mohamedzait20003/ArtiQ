"""
Save Ratings Job
Saves ratings to database
"""
import uuid
import logging
from app.models.Rating_Model import Rating_Model
from app.models.Artifact_Model import Artifact_Model

# Configure logger for CloudWatch
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def save_ratings_step(context):
    """
    Step 5: Save ratings to database
    """
    aggregated_data = (
        context.get('last') if isinstance(context, dict) else context
    )

    logger.info("[SAVE] Starting ratings save to database")
    print("[PIPELINE] Step 5: Saving ratings to database...")

    artifact = aggregated_data.get('artifact')
    scores = aggregated_data.get('scores', {})
    latencies = aggregated_data.get('latencies', {})
    net_score = aggregated_data.get('net_score', 0.0)
    net_latency = aggregated_data.get('net_latency', 0.0)

    if not artifact:
        logger.warning("[SAVE] No artifact found, skipping save")
        print("[PIPELINE] Warning: No artifact found, skipping save")
        return aggregated_data

    # Validate artifact exists in database
    logger.info(
        f"[SAVE] Validating artifact existence in database: {artifact.id}"
    )
    db_artifact = Artifact_Model.get({'id': artifact.id})

    if not db_artifact:
        logger.error(
            f"[SAVE] Artifact not found in database: {artifact.id}"
        )
        print(
            f"[PIPELINE] Error: Artifact {artifact.id} not found in database"
        )
        raise ValueError(
            f"Artifact not found in database: {artifact.id}"
        )

    logger.info(
        f"[SAVE] Artifact validated in database: {artifact.id}"
    )

    logger.info(
        f"[SAVE] Saving ratings for artifact: {artifact.id} ({artifact.name})"
    )

    try:
        # Helper to create metric dict with value and latency
        # Uses actual score if available, otherwise uses default
        def metric_dict(metric_name, default=0.0):
            return {
                'value': scores.get(metric_name, default),
                'latency': latencies.get(metric_name, 0.0)
            }

        # Generate unique rating ID
        rating_id = str(uuid.uuid4())

        # Log which metrics were evaluated
        logger.info(f"[SAVE] Available metrics: {list(scores.keys())}")
        logger.info(f"[SAVE] Scores values: {scores}")

        # Create or update rating with evaluated metrics
        # All metrics in parallel pipeline should be present
        rating = Rating_Model(
            id=rating_id,
            artifact_id=artifact.id,
            net_score={
                'value': net_score,
                'latency': net_latency
            },
            ramp_up_time=metric_dict('ramp_up', 0.0),
            bus_factor=metric_dict('bus_factor', 0.0),
            performance_claims=metric_dict('performance', 0.0),
            license=metric_dict('license', 0.0),
            dataset_and_code_score=metric_dict('availability', 0.0),
            dataset_quality=metric_dict('dataset_quality', 0.0),
            code_quality=metric_dict('code_quality', 0.0),
            reproducibility={'value': 0.0, 'latency': 0.0},
            reviewedness=metric_dict('reviewedness', -1.0),
            tree_score={'value': 0.0, 'latency': 0.0},
            size_score={
                'value': scores.get('size', {
                    'raspberry_pi': 0.0,
                    'jetson_nano': 0.0,
                    'desktop_pc': 0.0,
                    'aws_server': 0.0
                }),
                'latency': latencies.get('size', 0.0)
            }
        )

        rating.save()
        logger.info(f"[SAVE] Ratings saved for artifact {artifact.id}")
        print(f"[PIPELINE] Ratings saved for artifact {artifact.id}")

        # Rating is now accessible via artifact.rating() relationship
        logger.info(
            f"[SAVE] Rating can be accessed via relationship for "
            f"artifact {artifact.id}"
        )

    except Exception as e:
        logger.error(
            f"[SAVE] Error saving ratings for {artifact.id}: {e}",
            exc_info=True
        )
        print(f"[PIPELINE] Error saving ratings: {e}")
        import traceback
        traceback.print_exc()

    return aggregated_data

"""
Aggregate Scores Job
Aggregates metric scores into final rating
"""
import logging

# Configure logger for CloudWatch
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def aggregate_scores_step(context):
    """
    Step 4: Aggregate metric scores into final rating
    """
    metric_results = (
        context.get('last') if isinstance(context, dict) else context
    )
    metadata = (
        context.get('results')[-2] if isinstance(context, dict) else None
    )

    logger.info("[AGGREGATE] Starting score aggregation")
    print("[PIPELINE] Step 4: Aggregating scores...")

    scores = {}
    latencies = {}
    total_score = 0.0
    count = 0

    # Extract scores and latencies from metric results
    for result in metric_results:
        if result and isinstance(result, dict):
            metric_name = result.get('metric_name', 'unknown')
            score = result.get('score', 0.0)
            latency = result.get('latency', 0.0)

            scores[metric_name] = score
            latencies[metric_name] = latency
            total_score += score
            count += 1
            logger.info(
                f"[AGGREGATE] {metric_name}: {score:.3f} "
                f"(latency: {latency:.3f}s)"
            )
            print(f"[PIPELINE]   {metric_name}: {score} "
                  f"(latency: {latency}s)")

    # Calculate net score (average)
    net_score = total_score / count if count > 0 else 0.0
    net_latency = sum(latencies.values())

    logger.info(
        f"[AGGREGATE] Net Score: {net_score:.3f} "
        f"(total latency: {net_latency:.3f}s)"
    )
    print(f"[PIPELINE] Net Score: {net_score}")
    print(f"[PIPELINE] Total Latency: {net_latency}s")

    return {
        'metadata': metadata,
        'scores': scores,
        'latencies': latencies,
        'net_score': net_score,
        'net_latency': net_latency,
        'artifact': metadata.artifact if metadata else None
    }

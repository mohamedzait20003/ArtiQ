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

    # Get metadata from pipeline context
    # results[0] = validate, results[1] = fetch_metadata, results[2] = metrics
    if isinstance(context, dict):
        all_results = context.get('results', [])
    else:
        all_results = []
    metadata = all_results[1] if len(all_results) > 1 else None

    logger.info("[AGGREGATE] Starting score aggregation")
    print("[PIPELINE] Step 4: Aggregating scores...")
    
    logger.info(f"[AGGREGATE] Raw metric_results type: {type(metric_results)}")
    logger.info(
        f"[AGGREGATE] Raw metric_results length: "
        f"{len(metric_results) if isinstance(metric_results, list) else 'N/A'}"
    )

    scores = {}
    latencies = {}
    total_score = 0.0
    count = 0

    # Handle both single result and list of results
    if isinstance(metric_results, list):
        results_list = metric_results
    else:
        results_list = [metric_results]

    # Extract scores and latencies from metric results
    for result in results_list:
        if result and isinstance(result, dict):
            metric_name = result.get('metric_name', 'unknown')

            # Skip non-metric results (e.g., download_upload job)
            if metric_name == 'unknown' or not metric_name:
                job_name = result.get('job_name', 'unknown')
                logger.info(
                    f"[AGGREGATE] Skipping non-metric result: {job_name}"
                )
                continue

            # Handle lineage specially (not a score metric)
            if metric_name == 'lineage':
                lineage_graph = result.get('lineage_graph', {})
                scores['lineage'] = lineage_graph
                latencies['lineage'] = result.get('latency', 0.0)
                logger.info(
                    f"[AGGREGATE] lineage: "
                    f"{len(lineage_graph.get('parents', []))} parent(s)"
                )
                continue

            # Handle tree_score specially (included in net score)
            if metric_name == 'tree_score':
                score = result.get('score', 0.0)
                latency = result.get('latency', 0.0)
                scores[metric_name] = score
                latencies[metric_name] = latency
                total_score += score
                count += 1
                logger.info(
                    f"[AGGREGATE] {metric_name}: {score:.4f} "
                    f"(latency: {latency:.3f}s)"
                )
                print(f"[PIPELINE]   {metric_name}: {score} "
                      f"(latency: {latency}s)")
                continue

            score = result.get('score', 0.0)
            latency = result.get('latency', 0.0)

            # Handle size metric specially (nested dict with average)
            if metric_name == 'size' and isinstance(score, dict):
                score_value = score.get('average', 0.0)
                scores[metric_name] = score  # Keep full nested structure
                latencies[metric_name] = latency
                total_score += score_value  # Use average for net score
                count += 1
                logger.info(
                    f"[AGGREGATE] {metric_name}: {score_value:.3f} "
                    f"(latency: {latency:.3f}s)"
                )
                print(f"[PIPELINE]   {metric_name}: {score_value} "
                      f"(latency: {latency}s)")
            else:
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
    logger.info(f"[AGGREGATE] Final scores dict keys: {list(scores.keys())}")
    logger.info(f"[AGGREGATE] Final scores dict: {scores}")
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

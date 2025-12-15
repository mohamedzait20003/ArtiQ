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
    # Get the parallel results from context (index 2: after validate and fetch)
    # context['results'] = [validate, fetch, parallel_metrics, lineage,
    # tree_score]
    if isinstance(context, dict):
        all_results = context.get('results', [])
        # Parallel execution is at index 2
        parallel_results = all_results[2] if len(all_results) > 2 else []
        # Lineage is at index 3
        lineage_result = all_results[3] if len(all_results) > 3 else None
        # Tree score is at index 4 (also in context['last'])
        tree_score_result = all_results[4] if len(all_results) > 4 else None
        # Metadata from fetch (index 1)
        metadata = all_results[1] if len(all_results) > 1 else None
    else:
        parallel_results = []
        lineage_result = None
        tree_score_result = None
        metadata = None

    logger.info("[AGGREGATE] Starting score aggregation")
    print("[PIPELINE] Step 4: Aggregating scores...")
    
    logger.info(
        f"[AGGREGATE] Parallel results count: {len(parallel_results)}"
    )
    logger.info(
        f"[AGGREGATE] Has lineage result: {lineage_result is not None}"
    )
    logger.info(
        f"[AGGREGATE] Has tree_score result: "
        f"{tree_score_result is not None}"
    )

    scores = {}
    latencies = {}
    total_score = 0.0
    count = 0

    # Process parallel metric results
    for result in parallel_results:
        if result and isinstance(result, dict):
            metric_name = result.get('metric_name', 'unknown')

            # Skip non-metric results (e.g., download_upload job)
            if metric_name == 'unknown' or not metric_name:
                job_name = result.get('job_name', 'unknown')
                logger.info(
                    f"[AGGREGATE] Skipping non-metric result: {job_name}"
                )
                continue

            # Extract score and latency for normal metrics
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

    # Process lineage result separately
    if lineage_result and isinstance(lineage_result, dict):
        lineage_graph = lineage_result.get('lineage_graph', {})
        scores['lineage'] = lineage_graph
        latencies['lineage'] = lineage_result.get('latency', 0.0)
        logger.info(
            f"[AGGREGATE] lineage: "
            f"{len(lineage_graph.get('parents', []))} parent(s)"
        )

    # Process tree_score result separately
    if tree_score_result and isinstance(tree_score_result, dict):
        score = tree_score_result.get('score', 0.0)
        latency = tree_score_result.get('latency', 0.0)
        scores['tree_score'] = score
        latencies['tree_score'] = latency
        total_score += score
        count += 1
        logger.info(
            f"[AGGREGATE] tree_score: {score:.4f} "
            f"(latency: {latency:.3f}s)"
        )
        print(f"[PIPELINE]   tree_score: {score} "
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

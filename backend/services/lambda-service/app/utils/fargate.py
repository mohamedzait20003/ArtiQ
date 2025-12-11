"""
Fargate invocation utility for the Lambda service
"""
import os
from typing import Dict, Any
from include import get_ecs, encrypt_artifact_id


def invoke_fargate_task(artifact_id: str) -> Dict[str, Any]:
    """
    Invoke Fargate task to process an artifact

    Args:
        artifact_id: The artifact ID to process (will be encrypted)

    Returns:
        dict: ECS run_task response

    Raises:
        ValueError: If required environment variables are not set
        Exception: If ECS task invocation fails
    """
    # Encrypt the artifact ID before passing to Fargate
    encrypted_artifact_id = encrypt_artifact_id(artifact_id)

    # Get ECS configuration from environment variables
    cluster_name = os.environ.get(
        'ECS_CLUSTER_NAME',
        'artifact-evaluation-cluster'
    )
    task_definition = os.environ.get(
        'ECS_TASK_DEFINITION',
        'artifact-evaluation-task'
    )
    subnet_id = os.environ.get('ECS_SUBNET_ID')
    security_group = os.environ.get('ECS_SECURITY_GROUP')
    container_name = os.environ.get(
        'ECS_CONTAINER_NAME',
        'fargate-processor'
    )

    # Validate required environment variables
    if not subnet_id:
        raise ValueError(
            "ECS_SUBNET_ID environment variable is required"
        )
    if not security_group:
        raise ValueError(
            "ECS_SECURITY_GROUP environment variable is required"
        )

    # Get ECS client
    ecs_client = get_ecs()

    try:
        # Run Fargate task
        response = ecs_client.run_task(
            cluster=cluster_name,
            taskDefinition=task_definition,
            launchType='FARGATE',
            networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': [subnet_id],
                    'securityGroups': [security_group],
                    'assignPublicIp': 'ENABLED'
                }
            },
            overrides={
                'containerOverrides': [
                    {
                        'name': container_name,
                        'command': [
                            'python', '-m', 'app.main',
                            encrypted_artifact_id
                        ]
                    }
                ]
            }
        )

        print(f"[LAMBDA] Fargate task started for artifact: "
              f"{encrypted_artifact_id}")

        # Extract task ARN if available
        if response.get('tasks'):
            task_arn = response['tasks'][0].get('taskArn')
            print(f"[LAMBDA] Task ARN: {task_arn}")

        return response

    except Exception as e:
        print(f"[LAMBDA] Error invoking Fargate task: {e}")
        raise

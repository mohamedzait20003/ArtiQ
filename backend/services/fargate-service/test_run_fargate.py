import boto3
import json
import time

def run_fargate_task(message="Hello from test script!"):
    """
    Test script to run the Fargate task and fetch logs
    """
    ecs_client = boto3.client('ecs', region_name='us-east-2')
    logs_client = boto3.client('logs', region_name='us-east-2')
    
    # Configuration
    CLUSTER_NAME = "ModelEvaluation"
    TASK_DEFINITION = "ModelEvalTask"
    CONTAINER_NAME = "ModelEvalContainer"
    SUBNET_ID = "subnet-066efdb18b16bdcf5"
    SECURITY_GROUP = "sg-09e4b74cc268af399"
    LOG_GROUP = "/ecs/ModelEvalTask"
    
    print(f"Running Fargate task with message: '{message}'")
    
    try:
        # Run the task
        response = ecs_client.run_task(
            cluster=CLUSTER_NAME,
            taskDefinition=TASK_DEFINITION,
            launchType='FARGATE',
            networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': [SUBNET_ID],
                    'securityGroups': [SECURITY_GROUP],
                    'assignPublicIp': 'ENABLED'
                }
            },
            overrides={
                'containerOverrides': [
                    {
                        'name': CONTAINER_NAME,
                        'command': [message]
                    }
                ]
            }
        )
        
        task_arn = response['tasks'][0]['taskArn']
        task_id = task_arn.split('/')[-1]
        
        print(f"Task started successfully!")
        print(f"Task ARN: {task_arn}")
        print(f"\nWaiting for task to complete...")
        
        # Wait for task to complete
        waiter = ecs_client.get_waiter('tasks_stopped')
        try:
            waiter.wait(
                cluster=CLUSTER_NAME,
                tasks=[task_arn],
                WaiterConfig={'Delay': 5, 'MaxAttempts': 60}
            )
            print("Task completed!")
        except Exception as e:
            print(f"Task may still be running: {str(e)}")
        
        # Get task details
        task_details = ecs_client.describe_tasks(
            cluster=CLUSTER_NAME,
            tasks=[task_arn]
        )
        
        if task_details['tasks']:
            task = task_details['tasks'][0]
            last_status = task.get('lastStatus', 'UNKNOWN')
            print(f"Task Status: {last_status}")
            
            # Check for container exit code
            for container in task.get('containers', []):
                if 'exitCode' in container:
                    print(f"Exit Code: {container['exitCode']}")
                    if container['exitCode'] != 0:
                        print(f"Error: Container exited with non-zero code")
        
        # Fetch logs
        print(f"\nFetching logs from CloudWatch...")
        log_stream_name = f"ecs/{CONTAINER_NAME}/{task_id}"
        
        try:
            time.sleep(2)  # Give logs a moment to arrive
            log_response = logs_client.get_log_events(
                logGroupName=LOG_GROUP,
                logStreamName=log_stream_name,
                startFromHead=True
            )
            
            if log_response['events']:
                print(f"\n{'='*60}")
                print("TASK OUTPUT:")
                print(f"{'='*60}")
                for event in log_response['events']:
                    print(event['message'])
                print(f"{'='*60}")
            else:
                print("No logs found yet. Logs may take a moment to appear.")
                print(f"Log stream: {log_stream_name}")
        except logs_client.exceptions.ResourceNotFoundException:
            print(f"Log stream not found: {log_stream_name}")
            print("The task may have failed before logging anything.")
        except Exception as log_error:
            print(f"Error fetching logs: {str(log_error)}")
        
        return task_arn
        
    except Exception as e:
        print(f"Error running task: {str(e)}")
        return None

if __name__ == "__main__":
    # Test with a custom message
    run_fargate_task("Testing Fargate from Python script!")

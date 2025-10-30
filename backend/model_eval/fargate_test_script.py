import boto3
import time

# --- CONFIG ---
REGION = "us-east-2"
CLUSTER = "ModelEvaluation"
TASK_DEF = "ModelEvalTask"
CONTAINER_NAME = "ModelEvalContainer"
SUBNET = "subnet-066efdb18b16bdcf5"
LOG_GROUP = "/ecs/ModelEvalTask"
STREAM_PREFIX = "ecs"

# --- CLIENTS ---
ecs = boto3.client("ecs", region_name=REGION)
logs = boto3.client("logs", region_name=REGION)

# --- 1. RUN TASK ---
response = ecs.run_task(
    cluster=CLUSTER,
    launchType="FARGATE",
    taskDefinition=TASK_DEF,
    networkConfiguration={
        "awsvpcConfiguration": {
            "subnets": [SUBNET],
            "assignPublicIp": "ENABLED"
        }
    },
    overrides={
        "containerOverrides": [
            {
                "name": CONTAINER_NAME,
                "command": ["hello from script"]
            }
        ]
    }
)

task_arn = response["tasks"][0]["taskArn"]
print(f"Started task: {task_arn}")

# --- 2. WAIT FOR COMPLETION ---
while True:
    desc = ecs.describe_tasks(cluster=CLUSTER, tasks=[task_arn])
    status = desc["tasks"][0]["lastStatus"]
    print("Status:", status)
    if status == "STOPPED":
        break
    time.sleep(5)

# --- 3. FETCH LOGS ---
# CloudWatch log stream name usually matches this pattern:
# prefix/container-name/ecs-task-id
task_id = task_arn.split("/")[-1]
log_stream = f"{STREAM_PREFIX}/{CONTAINER_NAME}/{task_id}"

print(f"Fetching logs from stream: {log_stream}")

events = logs.get_log_events(
    logGroupName=LOG_GROUP,
    logStreamName=log_stream,
    startFromHead=True
)

print("---- Task Output ----")
for e in events["events"]:
    print(e["message"].strip())
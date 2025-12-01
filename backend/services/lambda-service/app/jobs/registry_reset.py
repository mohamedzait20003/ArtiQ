import json
from app.models.Artifact_Model import Artifact_Model
from app.models.Session_Model import Session_Model
from app.models.Auth_Model import Auth_Model


def lambda_handler(event, context):
    """
    AWS Lambda handler for DELETE /reset
    Reset the registry to a system default state

    This operation:
    1. Deletes all artifacts (and their S3 files via Model.delete())
    2. Deletes all sessions
    3. Deletes all users (except potentially system defaults)
    """
    try:
        deleted_counts = {
            'artifacts': 0,
            'sessions': 0,
            'users': 0
        }

        # Delete all artifacts using the model layer
        # This ensures S3 files are also cleaned up via Model.delete()
        result = Artifact_Model.scan_artifacts(limit=1000)
        artifacts = result['items']

        while artifacts:
            for artifact in artifacts:
                if artifact.delete():
                    deleted_counts['artifacts'] += 1

            # Handle pagination
            last_key = result['last_evaluated_key']
            if not last_key:
                break
            result = Artifact_Model.scan_artifacts(
                limit=1000,
                exclusive_start_key=last_key
            )
            artifacts = result['items']

        # Delete all sessions
        # Note: Session_Model needs a scan method similar to Artifact_Model
        # For now, we'll use the table directly if needed
        try:
            session_table = Session_Model.table()
            response = session_table.scan(Limit=1000)

            while True:
                items = response.get('Items', [])
                for item in items:
                    session = Session_Model(**item)
                    if session.delete():
                        deleted_counts['sessions'] += 1

                if 'LastEvaluatedKey' not in response:
                    break
                response = session_table.scan(
                    Limit=1000,
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
        except Exception as e:
            print(f"Warning: Could not reset sessions: {str(e)}")

        # Delete all users
        try:
            user_table = Auth_Model.table()
            response = user_table.scan(Limit=1000)

            while True:
                items = response.get('Items', [])
                for item in items:
                    user = Auth_Model(**item)
                    if user.delete():
                        deleted_counts['users'] += 1

                if 'LastEvaluatedKey' not in response:
                    break
                response = user_table.scan(
                    Limit=1000,
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
        except Exception as e:
            print(f"Warning: Could not reset users: {str(e)}")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Registry is reset.',
                'deleted': deleted_counts
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Internal server error: {str(e)}'
            })
        }

import json
from src.aws import dynamodb, s3_client
from botocore.exceptions import ClientError


def lambda_handler(event, context):
    """
    AWS Lambda handler for DELETE /reset
    Reset the registry to a system default state
    """
    try:
        # Reset DynamoDB tables - clear all items from Artifacts table
        artifacts_table = dynamodb.Table('Artifacts')
        
        # Scan all items and delete them
        response = artifacts_table.scan()
        items = response.get('Items', [])
        
        # Delete all artifacts
        for item in items:
            artifacts_table.delete_item(Key={'id': item['id']})
        
        # Handle pagination if there are more items
        while 'LastEvaluatedKey' in response:
            response = artifacts_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items = response.get('Items', [])
            for item in items:
                artifacts_table.delete_item(Key={'id': item['id']})
        
        # Reset S3 bucket - delete all objects
        bucket_name = event.get('ARTIFACTS_BUCKET', 'artifacts-bucket')
        
        try:
            # List all objects in the bucket
            objects_response = s3_client.list_objects_v2(Bucket=bucket_name)
            
            if 'Contents' in objects_response:
                # Delete all objects
                objects_to_delete = [{'Key': obj['Key']} for obj in objects_response['Contents']]
                
                if objects_to_delete:
                    s3_client.delete_objects(
                        Bucket=bucket_name,
                        Delete={'Objects': objects_to_delete}
                    )
                
                # Handle pagination for S3 objects
                while objects_response.get('IsTruncated', False):
                    continuation_token = objects_response['NextContinuationToken']
                    objects_response = s3_client.list_objects_v2(
                        Bucket=bucket_name,
                        ContinuationToken=continuation_token
                    )
                    
                    if 'Contents' in objects_response:
                        objects_to_delete = [{'Key': obj['Key']} for obj in objects_response['Contents']]
                        if objects_to_delete:
                            s3_client.delete_objects(
                                Bucket=bucket_name,
                                Delete={'Objects': objects_to_delete}
                            )
        
        except ClientError as e:
            # If bucket doesn't exist or access denied, continue
            print(f"Warning: Could not reset S3 bucket: {str(e)}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Registry is reset.'})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }
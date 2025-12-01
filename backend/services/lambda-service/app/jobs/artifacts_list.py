import json
import base64
from app.models.Artifact_Model import Artifact_Model


def parse_offset(offset_str):
    """Parse the offset string to DynamoDB ExclusiveStartKey"""
    if not offset_str:
        return None
    try:
        # Decode base64 offset to get the DynamoDB key
        decoded = base64.b64decode(offset_str.encode('utf-8'))
        return json.loads(decoded.decode('utf-8'))
    except Exception as e:
        print(f"Error parsing offset: {e}")
        return None


def encode_offset(last_evaluated_key):
    """Encode DynamoDB LastEvaluatedKey to offset string"""
    if not last_evaluated_key:
        return None
    try:
        # Encode the key as base64 string
        json_str = json.dumps(last_evaluated_key)
        encoded = base64.b64encode(json_str.encode('utf-8'))
        return encoded.decode('utf-8')
    except Exception as e:
        print(f"Error encoding offset: {e}")
        return None


def lambda_handler(event, context):
    """
    AWS Lambda handler for POST /artifacts
    Returns list of artifacts based on query
    """
    try:
        # Extract parameters from event
        artifact_queries = event.get('artifact_queries', [])
        offset = event.get('offset')
        auth_token = event.get('auth_token')  # Auth token passed but ignored for now
        
        print(f"Processing artifacts list request with {len(artifact_queries)} queries, offset: {offset}")
        
        # Parse the offset to DynamoDB format
        exclusive_start_key = parse_offset(offset)
        print(f"Parsed exclusive_start_key: {exclusive_start_key}")
        
        # Process each query
        all_results = []
        final_last_evaluated_key = None
        
        for query in artifact_queries:
            name = query.get('name', '*')
            types_filter = query.get('types')
            
            print(f"Processing query: name='{name}', types={types_filter}")
            
            # Use the scan_artifacts method with filters and pagination
            result = Artifact_Model.scan_artifacts(
                name_filter=name, 
                types_filter=types_filter,
                limit=100,  # Set limit to 100
                exclusive_start_key=exclusive_start_key
            )
            artifacts = result['items']
            last_evaluated_key = result['last_evaluated_key']
            
            # Keep track of the last evaluated key for pagination
            if last_evaluated_key:
                final_last_evaluated_key = last_evaluated_key
            
            # Convert artifacts to the expected response format (ArtifactMetadata)
            for artifact in artifacts:
                all_results.append({
                    'name': artifact.name,
                    'id': artifact.id,
                    'type': artifact.artifact_type
                })
        
        # Handle empty queries as wildcard
        if len(artifact_queries) == 0:
            result = Artifact_Model.scan_artifacts(
                limit=100,
                exclusive_start_key=exclusive_start_key
            )
            artifacts = result['items']
            final_last_evaluated_key = result['last_evaluated_key']
            
            for artifact in artifacts:
                all_results.append({
                    'name': artifact.name,
                    'id': artifact.id,
                    'type': artifact.artifact_type
                })
        
        # Remove duplicates by id (in case multiple queries return same artifact)
        seen_ids = set()
        unique_results = []
        for artifact in all_results:
            if artifact['id'] not in seen_ids:
                seen_ids.add(artifact['id'])
                unique_results.append(artifact)
        
        # Encode the next offset
        next_offset = encode_offset(final_last_evaluated_key)
        
        print(f"Found {len(unique_results)} unique artifacts after processing {len(artifact_queries)} queries")
        print(f"Next offset: {next_offset}")
        
        return (
            {
                'artifacts': unique_results,
                'offset': next_offset
            },
            200
        )
        
    except Exception as e:
        print(f"Error in artifacts_list lambda: {str(e)}")
        return (
            {'errorMessage': f"Error listing artifacts: {str(e)}"},
            500
        )

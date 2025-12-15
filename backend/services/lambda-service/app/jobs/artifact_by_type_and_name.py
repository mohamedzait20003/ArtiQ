from app.models import Artifact_Model


def lambda_handler(event, context):
    """
    AWS Lambda handler for GET /artifact/{artifact_type}/byName/{name}
    Searches for artifacts by type and name with fuzzy matching

    Matching is case-insensitive and partial for the name:
    - Exact type match required
    - Name matching uses fuzzy logic (contains, starts with, etc.)
    - Results are sorted by relevance

    Returns:
        List of ArtifactMetadata objects matching the type and name
    Raises:
        Exception with statusCode 400: Missing/invalid fields
        Exception with statusCode 404: No artifact found
    """
    print("[JOB] artifact_by_type_and_name job handler started")
    print(f"[JOB] Event received: {event}")

    try:
        # Extract parameters from event
        artifact_type = event.get('artifact_type')
        search_name = event.get('name')
        print(
            f"[JOB] Extracted artifact_type: {artifact_type}, "
            f"name: {search_name}"
        )

        # Validate required fields
        if not artifact_type:
            raise ValueError("Artifact type is required")

        if not search_name:
            raise ValueError("Name field is required")

        # Validate artifact type
        valid_types = {'model', 'dataset', 'code'}
        if artifact_type not in valid_types:
            raise ValueError(
                f"Invalid artifact type: {artifact_type}. "
                f"Must be one of {valid_types}"
            )

        # Normalize search name for comparison
        search_name_lower = search_name.lower().strip()

        # Get artifacts filtered by type
        print(
            f"[JOB] Scanning artifacts with type filter: {artifact_type}"
        )
        result = Artifact_Model.scan_artifacts(
            types_filter=[artifact_type],
            limit=1000
        )
        type_artifacts = result['items']
        print(
            f"[JOB] Found {len(type_artifacts)} artifacts "
            f"of type {artifact_type}"
        )

        # Search for matching artifacts with scoring
        matches = []

        for artifact in type_artifacts:
            artifact_name_lower = artifact.name.lower()
            
            # Calculate match score (higher is better)
            score = 0
            
            # Exact match (case-insensitive)
            if artifact_name_lower == search_name_lower:
                score = 100
            # Starts with search term
            elif artifact_name_lower.startswith(search_name_lower):
                score = 80
            # Ends with search term
            elif artifact_name_lower.endswith(search_name_lower):
                score = 70
            # Contains search term
            elif search_name_lower in artifact_name_lower:
                score = 50
            # Fuzzy match: search term words are in artifact name
            else:
                search_words = search_name_lower.split()
                matching_words = sum(
                    1 for word in search_words 
                    if word in artifact_name_lower
                )
                if matching_words > 0:
                    score = (matching_words / len(search_words)) * 40

            # Add to matches if score > 0
            if score > 0:
                matches.append({
                    'score': score,
                    'artifact': {
                        'id': artifact.id,
                        'name': artifact.name,
                        'size': artifact.size if hasattr(artifact, 'size') else None,
                        'description': artifact.description if hasattr(artifact, 'description') else None
                    }
                })

        # Sort by score (descending) and then by name (ascending)
        matches.sort(key=lambda x: (-x['score'], x['artifact']['name']))

        # Extract just the artifacts (remove scores)
        matching_artifacts = [match['artifact'] for match in matches]

        # Return 404 if no matches found
        if len(matching_artifacts) == 0:
            return (
                {
                    'errorMessage': (
                        f'No {artifact_type} artifact found with name '
                        f'matching: {search_name}'
                    )
                },
                404
            )

        print(
            f"[JOB] Found {len(matching_artifacts)} {artifact_type} "
            f"artifacts matching name: {search_name}"
        )

        return (matching_artifacts, 200)

    except ValueError as e:
        # Return 400 response for validation errors
        return (
            {
                'errorMessage': (
                    f"There is missing field(s) in the request "
                    f"or it is formed improperly, or is invalid: {str(e)}"
                )
            },
            400
        )
    except Exception as e:
        # Return 500 response for unexpected errors
        return (
            {
                'errorMessage': (
                    f"Error searching artifacts by type and name: {str(e)}"
                )
            },
            500
        )

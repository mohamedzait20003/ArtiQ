from app.models import Artifact_Model


def lambda_handler(event, context):
    """
    AWS Lambda handler for GET /artifact/byName/{name}
    Searches for artifacts by name with fuzzy matching (NON-BASELINE)

    Matching is case-insensitive and partial:
    - Exact matches are prioritized
    - Partial matches (contains) are included
    - Results are sorted by relevance

    Returns:
        List of ArtifactMetadata objects matching the name
    Raises:
        Exception with statusCode 400: Missing/invalid name field
        Exception with statusCode 404: No artifact found with this name
    """
    print("[JOB] artifact_by_name job handler started")
    print(f"[JOB] Event received: {event}")
    
    try:
        # Extract name from event
        search_name = event.get('name')
        print(f"[JOB] Extracted search name: {search_name}")

        # Validate name field
        if not search_name:
            raise ValueError("Name field is required")

        # Normalize search name for comparison
        search_name_lower = search_name.lower().strip()

        # Get all artifacts from the database
        print("[JOB] Scanning artifacts with limit=1000")
        result = Artifact_Model.scan_artifacts(limit=1000)
        all_artifacts = result['items']
        print(f"[JOB] Found {len(all_artifacts)} total artifacts to search")

        # Search for matching artifacts with scoring
        matches = []

        for artifact in all_artifacts:
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
                        'type': artifact.type,
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
                        f'No artifact found with name matching: {search_name}'
                    )
                },
                404
            )

        print(
            f"[JOB] Found {len(matching_artifacts)} artifacts matching "
            f"name: {search_name}"
        )

        return (matching_artifacts, 200)

    except ValueError as e:
        # Return 400 response for validation errors
        return (
            {
                'errorMessage': (
                    f"There is missing field(s) in the artifact name "
                    f"or it is formed improperly, or is invalid: {str(e)}"
                )
            },
            400
        )
    except Exception as e:
        # Return 500 response for unexpected errors
        return (
            {'errorMessage': f"Error searching artifacts by name: {str(e)}"},
            500
        )

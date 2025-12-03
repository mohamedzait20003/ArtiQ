import re
from app.models import Artifact_Model


class TimeoutException(Exception):
    """Exception raised when regex matching times out"""
    pass


def validate_regex_safety(pattern):
    """
    Validate regex pattern for known dangerous patterns that cause ReDoS

    Args:
        pattern: Regex pattern string
  
    Raises:
        ValueError: If pattern contains known dangerous constructs
    """
    # Check for nested quantifiers (common ReDoS pattern)
    # Only check for quantifiers directly nested, not separated by literals
    nested_quantifier_patterns = [
        r'\([^)]*[+*]\)[+*{]',  # (x+)+ or (x*)*
        r'\[[^\]]*[+*]\][+*{]',  # [x+]+ or [x*]*
    ]

    for dangerous_pattern in nested_quantifier_patterns:
        if re.search(dangerous_pattern, pattern):
            raise ValueError(
                "Regex pattern contains nested quantifiers that may "
                "cause catastrophic backtracking (ReDoS)"
            )

    # Check for alternation with quantifiers (overlapping alternation)
    # Pattern like (a|aa)* or (x|xy)+ causes exponential backtracking
    if re.search(r'\([^)]*\|[^)]*\)[+*]', pattern):
        raise ValueError(
            "Regex pattern contains alternation with quantifiers "
            "that may cause catastrophic backtracking (ReDoS)"
        )

    # Check for excessive repetition
    if re.search(r'\{[\d,]+\}.*\{[\d,]+\}', pattern):
        # Multiple large repetitions
        raise ValueError(
            "Regex pattern contains multiple large repetitions "
            "that may cause excessive computation"
        )

    # Check for very large repetition counts
    repetition_match = re.search(r'\{(\d+)(,(\d+))?\}', pattern)
    if repetition_match:
        min_count = int(repetition_match.group(1))
        max_count = repetition_match.group(3)
        if max_count:
            max_count = int(max_count)
            if max_count > 10000:
                raise ValueError(
                    f"Regex repetition count too large: {max_count}. "
                    f"Maximum allowed is 10000"
                )
        if min_count > 10000:
            raise ValueError(
                f"Regex repetition count too large: {min_count}. "
                f"Maximum allowed is 10000"
            )


def lambda_handler(event, context):
    """
    AWS Lambda handler for POST /artifact/byRegEx
    Searches for artifacts matching a regular expression (BASELINE)

    The regex is applied to:
    - Artifact names
    - Artifact READMEs (if available)

    Returns:
        List of ArtifactMetadata objects matching the regex
    Raises:
        Exception with statusCode 400: Missing/invalid regex field
        Exception with statusCode 403: Authentication failed
        Exception with statusCode 404: No artifact found under this regex
    """
    print("[JOB] artifact_by_regex job handler started")
    print(f"[JOB] Event received: {event}")
    try:
        # Extract regex from event
        regex_pattern = event.get('regex')
        print(f"[JOB] Extracted regex pattern: {regex_pattern}")

        # Validate regex field
        if not regex_pattern:
            raise ValueError("Regex field is required")

        # Validate regex for safety against ReDoS
        validate_regex_safety(regex_pattern)

        # Validate that the regex is a valid pattern
        try:
            compiled_regex = re.compile(regex_pattern, re.IGNORECASE)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {str(e)}")

        # Search for artifacts matching the regex
        # Get all artifacts from the database
        print("[JOB] Scanning artifacts with limit=1000")
        result = Artifact_Model.scan_artifacts(limit=1000)
        all_artifacts = result['items']
        print(f"[JOB] Found {len(all_artifacts)} total artifacts to search")

        # Filter artifacts by regex match on name or README
        matching_artifacts = []

        for artifact in all_artifacts:
            # Check if artifact name matches
            if compiled_regex.search(artifact.name):
                matching_artifacts.append({
                    'name': artifact.name,
                    'id': artifact.id,
                    'type': artifact.artifact_type
                })
                continue

            # Check if artifact has README content that matches
            # TODO: Add README search

        # Remove duplicates by id
        seen_ids = set()
        unique_artifacts = []
        for artifact in matching_artifacts:
            if artifact['id'] not in seen_ids:
                seen_ids.add(artifact['id'])
                unique_artifacts.append(artifact)

        # Return 404 if no matches found
        if len(unique_artifacts) == 0:
            return (
                {'errorMessage': 'No artifact found under this regex.'},
                404
            )

        print(
            f"[JOB] Found {len(unique_artifacts)} artifacts matching "
            f"regex: {regex_pattern}"
        )

        return (unique_artifacts, 200)

    except ValueError as e:
        # Return 400 response for validation errors
        return (
            {
                'errorMessage': (
                    f"There is missing field(s) in the artifact_regex "
                    f"or it is formed improperly, or is invalid: {str(e)}"
                )
            },
            400
        )
    except Exception as e:
        # Return 500 response for unexpected errors
        return (
            {'errorMessage': f"Error searching artifacts by regex: {str(e)}"},
            500
        )

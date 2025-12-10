"""
Model Artifact Rate Job
Retrieves ratings for a model artifact
"""
from app.models import Artifact_Model, Rating_Model


def lambda_handler(event, context):
    """
    AWS Lambda handler for GET /artifact/model/{id}/rate
    Retrieves rating information for a model artifact

    Args:
        event: {
            'artifact_id': str - The model artifact ID
        }
        context: Lambda context object

    Returns:
        tuple: (response_data, status_code)
    """
    try:
        # Extract artifact_id from event
        artifact_id = event.get('artifact_id')

        if not artifact_id:
            return (
                {'errorMessage': 'artifact_id is required'},
                400
            )

        # Retrieve the artifact from database
        artifact = Artifact_Model.get({'id': artifact_id})

        if not artifact:
            return (
                {'errorMessage': f'Artifact {artifact_id} does not exist'},
                404
            )

        # Verify it's a model artifact
        if artifact.artifact_type != 'model':
            return (
                {
                    'errorMessage':
                        f'Artifact {artifact_id} is not a model artifact'
                },
                400
            )

        # Retrieve rating for this artifact
        rating = Rating_Model.find_by_artifact_id(artifact_id)

        if not rating:
            return (
                {
                    'errorMessage':
                        f'No rating found for artifact {artifact_id}. '
                        'The artifact may not have been evaluated yet.'
                },
                404
            )

        # Format response according to ModelRating schema
        response = {
            'name': rating.name,
            'category': rating.category,
            'net_score': rating.net_score.get('value', 0.0),
            'net_score_latency': rating.net_score.get('latency', 0.0),
            'ramp_up_time': rating.ramp_up_time.get('value', 0.0),
            'ramp_up_time_latency': rating.ramp_up_time.get('latency', 0.0),
            'bus_factor': rating.bus_factor.get('value', 0.0),
            'bus_factor_latency': rating.bus_factor.get('latency', 0.0),
            'performance_claims': rating.performance_claims.get('value', 0.0),
            'performance_claims_latency':
                rating.performance_claims.get('latency', 0.0),
            'license': rating.license.get('value', 0.0),
            'license_latency': rating.license.get('latency', 0.0),
            'dataset_and_code_score':
                rating.dataset_and_code_score.get('value', 0.0),
            'dataset_and_code_score_latency':
                rating.dataset_and_code_score.get('latency', 0.0),
            'dataset_quality': rating.dataset_quality.get('value', 0.0),
            'dataset_quality_latency':
                rating.dataset_quality.get('latency', 0.0),
            'code_quality': rating.code_quality.get('value', 0.0),
            'code_quality_latency': rating.code_quality.get('latency', 0.0),
            'reproducibility': rating.reproducibility.get('value', 0.0),
            'reproducibility_latency':
                rating.reproducibility.get('latency', 0.0),
            'reviewedness': rating.reviewedness.get('value', 0.0),
            'reviewedness_latency': rating.reviewedness.get('latency', 0.0),
            'tree_score': rating.tree_score.get('value', 0.0),
            'tree_score_latency': rating.tree_score.get('latency', 0.0),
            'size_score': rating.size_score.get('value', {
                'raspberry_pi': 0.0,
                'jetson_nano': 0.0,
                'desktop_pc': 0.0,
                'aws_server': 0.0
            }),
            'size_score_latency': rating.size_score.get('latency', 0.0)
        }

        return (response, 200)

    except Exception as e:
        print(f"Error in model_artifact_rate: {str(e)}")
        return (
            {
                'errorMessage':
                    f'The artifact rating system encountered an error: '
                    f'{str(e)}'
            },
            500
        )

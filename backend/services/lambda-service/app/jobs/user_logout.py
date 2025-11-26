import json
from app.models.Session_Model import Session_Model


def lambda_handler(event, context):
    """
    AWS Lambda handler for DELETE /logout
    Logs out user by deleting session
    """
    try:
        # Extract parameters from event
        session_id = event.get('session_id')

        if not session_id:
            error_response = {
                'statusCode': 400,
                'errorMessage': 'Session ID is required'
            }
            raise Exception(json.dumps(error_response))

        # Find session by ID (primary key)
        session = Session_Model.get({'ID': session_id})

        if session:
            if not session.delete():
                error_response = {
                    'statusCode': 500,
                    'errorMessage': 'Failed to delete session'
                }
                raise Exception(json.dumps(error_response))

        # Return success response (even if session not found)
        return {
            'message': 'Logged out successfully'
        }

    except Exception as e:
        error_str = str(e)
        # If it's already a JSON error, re-raise it
        try:
            json.loads(error_str)
            raise
        except json.JSONDecodeError:
            # Otherwise wrap in 500 error
            error_response = {
                'statusCode': 500,
                'errorMessage': f'Error during logout: {error_str}'
            }
            raise Exception(json.dumps(error_response))

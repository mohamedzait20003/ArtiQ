import json
import uuid
from app.models.Auth_Model import Auth_Model
from app.models.Session_Model import Session_Model


def lambda_handler(event, context):
    """
    AWS Lambda handler for PUT /authenticate
    Authenticates user and creates session
    """
    try:
        # Extract parameters from event
        username = event.get('username')
        password = event.get('password')
        is_admin = event.get('is_admin', False)

        if not username or not password:
            error_response = {
                'statusCode': 400,
                'errorMessage': 'There is missing field(s) in the '
                'AuthenticationRequest or it is formed improperly'
            }
            raise Exception(json.dumps(error_response))

        # Authenticate user
        user = Auth_Model.check_user(username, password)
        if not user:
            error_response = {
                'statusCode': 401,
                'errorMessage': 'The user or password is invalid'
            }
            raise Exception(json.dumps(error_response))

        # Verify admin status if required
        if is_admin and not user.is_admin:
            error_response = {
                'statusCode': 401,
                'errorMessage': 'The user or password is invalid'
            }
            raise Exception(json.dumps(error_response))

        # Generate session
        session_id = str(uuid.uuid4())
        session_token = str(uuid.uuid4())

        session = Session_Model(
            ID=session_id,
            UserID=user.ID,
            Token=session_token
        )

        if not session.save():
            error_response = {
                'statusCode': 500,
                'errorMessage': 'Failed to create session'
            }
            raise Exception(json.dumps(error_response))

        # Return success response with token
        return {
            'token': session_token
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
                'errorMessage': f'Error during authentication: {error_str}'
            }
            raise Exception(json.dumps(error_response))

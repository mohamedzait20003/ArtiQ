import json
import uuid
import logging
from app.models import Auth_Model, Session_Model

# Configure logger for CloudWatch
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    AWS Lambda handler for PUT /authenticate
    Authenticates user and creates session
    """
    try:
        logger.info("[AUTH] Starting authentication request")
        
        # Extract parameters from event
        username = event.get('username')
        password = event.get('password')
        is_admin = event.get('is_admin', False)
        
        logger.info(
            f"[AUTH] Authentication attempt for user: {username} "
            f"(is_admin: {is_admin})"
        )

        if not username or not password:
            logger.warning("[AUTH] Missing username or password")
            error_response = {
                'statusCode': 400,
                'errorMessage': 'There is missing field(s) in the '
                'AuthenticationRequest or it is formed improperly'
            }
            raise Exception(json.dumps(error_response))

        # Authenticate user
        logger.info(f"[AUTH] Checking credentials for user: {username}")
        user = Auth_Model.check_user(username, password)
        if not user:
            logger.warning(
                f"[AUTH] Authentication failed for user: {username} - "
                "Invalid credentials"
            )
            error_response = {
                'statusCode': 401,
                'errorMessage': 'The user or password is invalid'
            }
            raise Exception(json.dumps(error_response))

        logger.info(
            f"[AUTH] User authenticated successfully: {username} "
            f"(ID: {user.ID})"
        )

        # Verify admin status if required
        if is_admin and not user.is_admin:
            logger.warning(
                f"[AUTH] Admin access denied for user: {username} - "
                "User does not have admin privileges"
            )
            error_response = {
                'statusCode': 401,
                'errorMessage': 'The user or password is invalid'
            }
            raise Exception(json.dumps(error_response))

        # Generate session
        session_id = str(uuid.uuid4())
        session_token = str(uuid.uuid4())
        
        logger.info(
            f"[AUTH] Creating session for user: {username} "
            f"(session_id: {session_id})"
        )

        session = Session_Model(
            ID=session_id,
            UserID=user.ID,
            Token=session_token
        )

        if not session.save():
            logger.error(
                f"[AUTH] Failed to save session for user: {username}"
            )
            error_response = {
                'statusCode': 500,
                'errorMessage': 'Failed to create session'
            }
            raise Exception(json.dumps(error_response))

        logger.info(
            f"[AUTH] Session created successfully for user: {username} "
            f"(token: {session_token[:8]}...)"
        )

        # Return success response with token
        return {
            'token': session_token
        }

    except Exception as e:
        error_str = str(e)
        # If it's already a JSON error, re-raise it
        try:
            error_data = json.loads(error_str)
            logger.error(
                f"[AUTH] Authentication error: "
                f"{error_data.get('errorMessage', 'Unknown error')}"
            )
            raise
        except json.JSONDecodeError:
            # Otherwise wrap in 500 error
            logger.error(
                f"[AUTH] Unexpected error during authentication: {error_str}",
                exc_info=True
            )
            error_response = {
                'statusCode': 500,
                'errorMessage': f'Error during authentication: {error_str}'
            }
            raise Exception(json.dumps(error_response))

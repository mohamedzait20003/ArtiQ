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
        logger.info(
            "[AUTH] ========== Starting authentication request =========="
        )
        
        # Extract parameters from event
        username = event.get('username')
        password = event.get('password')
        is_admin = event.get('is_admin', False)
        
        # Log authentication attempt with masked password
        logger.info(
            f"[AUTH] SECTION 1: Request Parameters - "
            f"username='{username}', "
            f"password={'PROVIDED' if password else 'MISSING'}, "
            f"is_admin={is_admin}"
        )
        
        logger.info(
            f"[AUTH] Full request details: username={username}, "
            f"password={password}, is_admin={is_admin}"
        )

        if not username or not password:
            logger.warning(
                f"[AUTH] SECTION 1 FAILED: Missing required fields - "
                f"username={'present' if username else 'missing'}, "
                f"password={'present' if password else 'missing'}"
            )
            error_response = {
                'statusCode': 400,
                'errorMessage': 'There is missing field(s) in the '
                'AuthenticationRequest or it is formed improperly'
            }
            raise Exception(json.dumps(error_response))
        
        logger.info("[AUTH] SECTION 1 PASSED: All required fields present")

        # Authenticate user
        logger.info(
            f"[AUTH] SECTION 2: Credential Verification - "
            f"Checking credentials for user: {username}"
        )
        user = Auth_Model.check_user(username, password)
        
        if not user:
            logger.warning(
                f"[AUTH] SECTION 2 FAILED: Authentication failed for "
                f"user: {username} - Invalid credentials"
            )
            error_response = {
                'statusCode': 401,
                'errorMessage': 'The user or password is invalid'
            }
            raise Exception(json.dumps(error_response))

        logger.info(
            f"[AUTH] SECTION 2 PASSED: User authenticated successfully - "
            f"username={username}, user_id={user.ID}, "
            f"is_admin={user.is_admin}"
        )

        # Verify admin status if required
        logger.info(
            f"[AUTH] SECTION 3: Admin Verification - "
            f"is_admin_required={is_admin}, user_is_admin={user.is_admin}"
        )
        
        if is_admin and not user.is_admin:
            logger.warning(
                f"[AUTH] SECTION 3 FAILED: Admin access denied for "
                f"user: {username} - User does not have admin privileges "
                f"(requested admin access but user.is_admin={user.is_admin})"
            )
            error_response = {
                'statusCode': 401,
                'errorMessage': 'The user or password is invalid'
            }
            raise Exception(json.dumps(error_response))
        
        logger.info(
            f"[AUTH] SECTION 3 PASSED: Admin verification successful - "
            f"admin_required={is_admin}, user_is_admin={user.is_admin}"
        )

        # Generate session
        logger.info(
            f"[AUTH] SECTION 4: Session Creation - "
            f"Generating session for user: {username}"
        )
        
        session_id = str(uuid.uuid4())
        session_token = str(uuid.uuid4())
        
        logger.info(
            f"[AUTH] Generated session_id={session_id}, "
            f"token={session_token[:8]}..."
        )

        session = Session_Model(
            ID=session_id,
            UserID=user.ID,
            Token=session_token
        )
        
        logger.info(
            f"[AUTH] Saving session to database for user_id={user.ID}"
        )

        if not session.save():
            logger.error(
                f"[AUTH] SECTION 4 FAILED: Failed to save session for "
                f"user: {username}, session_id={session_id}"
            )
            error_response = {
                'statusCode': 500,
                'errorMessage': 'Failed to create session'
            }
            raise Exception(json.dumps(error_response))

        logger.info(
            f"[AUTH] SECTION 4 PASSED: Session created successfully - "
            f"username={username}, session_id={session_id}, "
            f"token={session_token[:8]}..."
        )

        # Return success response with token
        logger.info(
            f"[AUTH] ========== Authentication successful for "
            f"username={username} =========="
        )
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

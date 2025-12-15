import os
import jwt
import json
import logging
from app.models import Auth_Model

# Configure logger for CloudWatch
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    AWS Lambda handler for POST /login
    Authenticates user and creates session
    Args:
        event: {
            'email': str,
            'password': str
        }
    Returns:
        {
            'token': str,
            'role': str,
            'userData': {
                'name': str
            }
        }
    """
    try:
        logger.info(
            "[LOGIN] ========== Starting login request =========="
        )

        # Extract parameters from event
        email = event.get('email')
        password = event.get('password')

        logger.info(
            f"[LOGIN] Request Parameters - "
            f"email='{email}', "
            f"password={'PROVIDED' if password else 'MISSING'}"
        )

        # Validate required fields
        if not email or not password:
            logger.warning("[LOGIN] Missing required fields")
            error_response = {
                'statusCode': 400,
                'errorMessage': (
                    'There is missing field(s) in the login '
                    'request or it is formed improperly'
                )
            }
            raise Exception(json.dumps(error_response))

        # Find user by email
        logger.info(f"[LOGIN] Looking up user: {email}")
        user = Auth_Model.get({'Email': email})
        
        if not user:
            logger.warning(f"[LOGIN] User not found: {email}")
            error_response = {
                'statusCode': 401,
                'errorMessage': 'Invalid email or password'
            }
            raise Exception(json.dumps(error_response))

        # Verify password
        logger.info(f"[LOGIN] Verifying password for user: {email}")
        if not Auth_Model._verify_password(password, user.Password):
            logger.warning(f"[LOGIN] Invalid password for user: {email}")
            error_response = {
                'statusCode': 401,
                'errorMessage': 'Invalid email or password'
            }
            raise Exception(json.dumps(error_response))

        logger.info(
            f"[LOGIN] User authenticated successfully - "
            f"email={email}, user_id={user.ID}"
        )

        # Get user role
        role = user.role()
        role_name = role.Name if role else 'Unknown'

        logger.info(f"[LOGIN] User role: {role_name}")

        # Generate JWT token (no session needed)
        secret_key = os.environ.get('JWT_SECRET_KEY', 'your-secret-key')
        token = jwt.encode(
            {
                'user_id': user.ID
            },
            secret_key,
            algorithm='HS256'
        )
        
        logger.info(f"[LOGIN] Login successful for user: {email}")

        # Return response
        return {
            'token': token,
            'role': role_name,
            'userData': {
                'name': user.Name
            }
        }

    except Exception as e:
        error_str = str(e)
        logger.error(f"[LOGIN] Error: {error_str}")
        
        # Check if it's a structured error response
        try:
            error_dict = json.loads(error_str)
            status_code = error_dict.get('statusCode', 500)
            error_message = error_dict.get('errorMessage', error_str)
        except (json.JSONDecodeError, AttributeError):
            status_code = 500
            error_message = f"Error during login: {error_str}"
        
        return (
            {'errorMessage': error_message},
            status_code
        )

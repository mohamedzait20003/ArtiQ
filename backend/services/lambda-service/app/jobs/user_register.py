import os
import jwt
import json
import uuid
import logging
from app.models import Auth_Model, Role_Model

# Configure logger for CloudWatch
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    AWS Lambda handler for POST /register
    Creates a new user with visitor role
    Args:
        event: {
            'name': str,
            'email': str,
            'password': str,
            'confirm_password': str
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
            "[REGISTER] ========== Starting registration request =========="
        )

        # Extract parameters from event
        name = event.get('name')
        email = event.get('email')
        password = event.get('password')
        confirm_password = event.get('confirm_password')

        logger.info(
            f"[REGISTER] Request Parameters - "
            f"name='{name}', email='{email}', "
            f"password={'PROVIDED' if password else 'MISSING'}, "
            f"confirm_password={'PROVIDED' if confirm_password else 'MISSING'}"
        )

        # Validate required fields
        if not name or not email or not password or not confirm_password:
            logger.warning("[REGISTER] Missing required fields")
            error_response = {
                'statusCode': 400,
                'errorMessage': (
                    'There is missing field(s) in the registration '
                    'request or it is formed improperly'
                )
            }
            raise Exception(json.dumps(error_response))

        # Validate password match
        if password != confirm_password:
            logger.warning("[REGISTER] Passwords do not match")
            error_response = {
                'statusCode': 400,
                'errorMessage': 'Passwords do not match'
            }
            raise Exception(json.dumps(error_response))

        # Check if user already exists
        logger.info(f"[REGISTER] Checking if user exists: {email}")
        existing_user = Auth_Model.get({'Email': email})

        if existing_user:
            logger.warning(f"[REGISTER] User already exists: {email}")
            error_response = {
                'statusCode': 400,
                'errorMessage': 'User with this email already exists'
            }
            raise Exception(json.dumps(error_response))

        # Get visitor role
        logger.info("[REGISTER] Getting visitor role")
        visitor_role = Role_Model.get_by_name('Visitor')

        if not visitor_role:
            logger.error("[REGISTER] Visitor role not found in database")
            error_response = {
                'statusCode': 500,
                'errorMessage': 'Visitor role not configured'
            }
            raise Exception(json.dumps(error_response))

        # Create new user
        user_id = str(uuid.uuid4())
        logger.info(f"[REGISTER] Creating new user: {email}, ID: {user_id}")

        new_user = Auth_Model(
            ID=user_id,
            Name=name,
            Email=email,
            Password=password,
            Username=email,
            RoleID=visitor_role.RoleID
        )

        # Save user (password will be hashed automatically)
        new_user.save()
        logger.info(f"[REGISTER] User created successfully: {user_id}")

        # Generate JWT token (no session needed)
        secret_key = os.environ.get('JWT_SECRET_KEY', 'your-secret-key')
        token = jwt.encode(
            {
                'user_id': user_id
            },
            secret_key,
            algorithm='HS256'
        )

        logger.info(
            f"[REGISTER] Registration successful for user: {email}"
        )

        # Return response
        return {
            'token': token,
            'role': visitor_role.Name,
            'userData': {
                'name': name
            }
        }

    except Exception as e:
        error_str = str(e)
        logger.error(f"[REGISTER] Error: {error_str}")

        # Check if it's a structured error response
        try:
            error_dict = json.loads(error_str)
            status_code = error_dict.get('statusCode', 500)
            error_message = error_dict.get('errorMessage', error_str)
        except (json.JSONDecodeError, AttributeError):
            status_code = 500
            error_message = f"Error during registration: {error_str}"

        return (
            {'errorMessage': error_message},
            status_code
        )

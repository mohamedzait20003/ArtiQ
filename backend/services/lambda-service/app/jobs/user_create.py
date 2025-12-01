import json
import uuid
import hashlib
from app.models.Auth_Model import Auth_Model


def lambda_handler(event, context):
    """
    AWS Lambda handler for POST /admin/users
    Creates a new user account (admin only)
    """
    try:
        # Extract parameters from event
        name = event.get('name')
        email = event.get('email')
        password = event.get('password')
        role_id = event.get('role_id')

        # Validate required fields
        if not name or not email or not password:
            error_response = {
                'statusCode': 400,
                'errorMessage': 'Missing required field(s): '
                'name, email, and password are required'
            }
            raise Exception(json.dumps(error_response))

        # Check if user already exists
        existing_user = Auth_Model.get_by_email(email)
        if existing_user:
            error_response = {
                'statusCode': 409,
                'errorMessage': 'User with this email already exists'
            }
            raise Exception(json.dumps(error_response))

        # Generate user ID
        user_id = str(uuid.uuid4())

        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Create user
        user = Auth_Model(
            ID=user_id,
            Name=name,
            Email=email,
            Password=hashed_password,
            RoleID=role_id
        )

        if not user.save():
            error_response = {
                'statusCode': 500,
                'errorMessage': 'Failed to create user'
            }
            raise Exception(json.dumps(error_response))

        # Return success response with user details
        return {
            'id': user_id,
            'name': name,
            'email': email,
            'role_id': role_id
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
                'errorMessage': f'Error creating user: {error_str}'
            }
            raise Exception(json.dumps(error_response))

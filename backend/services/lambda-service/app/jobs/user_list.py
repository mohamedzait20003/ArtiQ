"""
Job: List All Users
Retrieves all users with their role, name, and email (Admin only)
"""

import logging
from app.models import Auth_Model

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Get all users with role, name, and email

    Returns:
        List of user objects with:
        - id: User ID
        - name: User name
        - email: User email
        - role: User role name
    """
    try:
        logger.info("[USER_LIST] Fetching all users...")

        # Get all users from database using where with empty query
        users = Auth_Model.where({})

        if not users:
            logger.info("[USER_LIST] No users found")
            return [], 200

        logger.info(f"[USER_LIST] Found {len(users)} users")

        # Format response with role, name, email
        result = []
        for user in users:
            # Get user role
            role = user.role()
            role_name = role.Name if role else 'No Role'

            user_dict = {
                'id': user.ID,
                'name': user.Name,
                'email': user.Email,
                'role': role_name
            }
            result.append(user_dict)

        logger.info(f"[USER_LIST] Returning {len(result)} users")
        return result, 200

    except Exception as e:
        logger.error(f"[USER_LIST] Error: {str(e)}")
        return {
            'errorMessage': f'Error retrieving users: {str(e)}'
        }, 500

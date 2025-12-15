from fastapi import HTTPException, Request
from app.types.user_types import CreateUserRequest, UserResponse
from app.jobs import create_user_job, user_list_job


class AdminController:
    """
    Admin Controller
    Handles administrative operations like user management
    """

    def __init__(self):
        pass

    async def create_user(
        self,
        request: Request,
        user_data: CreateUserRequest
    ) -> UserResponse:
        """
        Create a new user (admin only)

        Args:
            request: FastAPI request object (user attached by middleware)
            user_data: User creation request data

        Returns:
            UserResponse with created user details

        Raises:
            HTTPException: 400, 409, or 500
        """
        print("POST /admin/users called")
        try:
            # Prepare event for handler function
            event = {
                'name': user_data.name,
                'email': user_data.email,
                'password': user_data.password,
                'role_id': user_data.role_id,
                'is_admin': user_data.is_admin
            }

            # Call the handler function directly
            result = create_user_job(event, None)

            print("POST /admin/users RETURNING: 201 - success")
            return UserResponse(**result)

        except HTTPException:
            raise
        except Exception as e:
            error_str = str(e)
            print(f"POST /admin/users RETURNING: 500 - "
                  f"Exception: {error_str}")

            # Try to parse JSON error from job
            try:
                import json
                error_data = json.loads(error_str)
                status_code = error_data.get('statusCode', 500)
                error_message = error_data.get('errorMessage', str(e))
                raise HTTPException(
                    status_code=status_code,
                    detail=error_message
                )
            except (json.JSONDecodeError, AttributeError):
                raise HTTPException(
                    status_code=500,
                    detail=f"Error creating user: {error_str}"
                )

    async def list_users(self):
        """
        Get all users with their role, name, and email (admin only)

        Returns:
            List of user objects with id, name, email, role

        Raises:
            HTTPException: 500 on error
        """
        print("GET /admin/users called")
        try:
            # Call the handler function directly
            result, status_code = user_list_job({}, None)

            # Check if response is an error
            if status_code != 200:
                error_message = result.get('errorMessage', 'Unknown error')
                print(
                    f"GET /admin/users RETURNING: "
                    f"{status_code} - {error_message}"
                )
                raise HTTPException(
                    status_code=status_code,
                    detail=error_message
                )

            print(f"GET /admin/users RETURNING: 200 - {len(result)} users")
            return result

        except HTTPException:
            raise
        except Exception as e:
            print(f"GET /admin/users RETURNING: 500 - Exception: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving users: {str(e)}"
            )

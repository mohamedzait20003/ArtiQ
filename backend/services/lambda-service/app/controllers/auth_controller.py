from fastapi import HTTPException, Request
from app.types.auth_types import AuthenticationRequest
from app.jobs import authenticate_job, logout_job


class AuthController:
    """
    Authentication Controller
    Handles user registration, login, and session management
    """

    def __init__(self):
        pass

    async def authenticate(self, request: AuthenticationRequest):
        """
        Create an access token (NON-BASELINE)

        If your system supports the authentication scheme:
        1. The obtained token should be provided to other endpoints
           via the "X-Authorization" header.
        2. The "Authorization" header is *required* in your system.

        Otherwise, this endpoint should return HTTP 501
        "Not implemented", and the "X-Authorization" header should
        be unused for the other endpoints.

        Args:
            request: Authentication credentials (user, secret)

        Returns:
            Bearer token string

        Raises:
            HTTPException: 400, 401, or 501
        """
        print("PUT /authenticate called")
        try:
            # Validate request fields
            if not request.user or not request.secret:
                print("PUT /authenticate RETURNING: 400 - "
                      "Missing fields")
                raise HTTPException(
                    status_code=400,
                    detail="There is missing field(s) in the "
                    "AuthenticationRequest or it is formed "
                    "improperly")

            if not request.user.name or not request.secret.password:
                print("PUT /authenticate RETURNING: 400 - "
                      "Missing fields")
                raise HTTPException(
                    status_code=400,
                    detail="There is missing field(s) in the "
                    "AuthenticationRequest or it is formed "
                    "improperly")

            # Prepare event for handler function
            event = {
                'username': request.user.name,
                'password': request.secret.password,
                'is_admin': request.user.is_admin
            }

            # Call the handler function directly
            result = authenticate_job(event, None)

            # Return bearer token as JSON object with 'value' key
            print("PUT /authenticate RETURNING: 200 - success")
            token = result.get('token', '')
            return {"value": f"bearer {token}"}

        except HTTPException:
            raise
        except Exception as e:
            print(f"PUT /authenticate RETURNING: 500 - "
                  f"Exception: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error invoking login: {str(e)}")

    async def logout(
        self,
        request: Request
    ):
        """
        Logout user by deleting session

        Args:
            request: FastAPI request object (user attached by middleware)

        Returns:
            Success message
        """
        print("DELETE /logout called")
        try:
            # Get user from request state (attached by middleware)
            current_user = request.state.user
            
            # Prepare event for handler function
            event = {
                'session_id': current_user.session.ID
            }

            # Call the handler function directly
            result = logout_job(event, None)

            print("DELETE /logout RETURNING: 200 - success")
            return result

        except HTTPException:
            raise
        except Exception as e:
            print(f"DELETE /logout RETURNING: 500 - "
                  f"Exception: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error invoking logout: {str(e)}")

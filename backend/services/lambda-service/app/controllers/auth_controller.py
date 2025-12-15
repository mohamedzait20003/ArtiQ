from fastapi import HTTPException, Request
from app.jobs import (
    authenticate_job,
    logout_job,
    register_job,
    login_job
)
from app.types.auth_types import (
    AuthenticationRequest,
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse
)


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

    async def register(
        self,
        request: RegisterRequest
    ) -> RegisterResponse:
        """
        Register a new user with visitor role

        Args:
            request: Registration data (name, email, password,
            confirm_password)

        Returns:
            RegisterResponse with token, role, and userData

        Raises:
            HTTPException: 400 or 500
        """
        print("POST /register called")
        try:
            # Validate request fields
            if not request.name or not request.email:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "There is missing field(s) in the registration "
                        "request or it is formed improperly"
                    )
                )

            if not request.password or not request.confirm_password:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "There is missing field(s) in the registration "
                        "request or it is formed improperly"
                    )
                )

            # Prepare event for handler function
            event = {
                'name': request.name,
                'email': request.email,
                'password': request.password,
                'confirm_password': request.confirm_password
            }

            # Call the handler function directly
            result = register_job(event, None)

            # Check if it's an error response tuple
            if isinstance(result, tuple):
                error_data, status_code = result
                raise HTTPException(
                    status_code=status_code,
                    detail=error_data.get(
                        'errorMessage', 'Registration failed'
                    )
                )

            print("POST /register RETURNING: 200 - success")
            return RegisterResponse(**result)

        except HTTPException:
            raise
        except Exception as e:
            print(f"POST /register RETURNING: 500 - Exception: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error during registration: {str(e)}"
            )

    async def login(
        self,
        request: LoginRequest
    ) -> LoginResponse:
        """
        Login user with email and password

        Args:
            request: Login credentials (email, password)

        Returns:
            LoginResponse with token, role, and userData

        Raises:
            HTTPException: 400, 401, or 500
        """
        print("POST /login called")
        try:
            # Validate request fields
            if not request.email or not request.password:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "There is missing field(s) in the login "
                        "request or it is formed improperly"
                    )
                )

            # Prepare event for handler function
            event = {
                'email': request.email,
                'password': request.password
            }

            # Call the handler function directly
            result = login_job(event, None)

            # Check if it's an error response tuple
            if isinstance(result, tuple):
                error_data, status_code = result
                raise HTTPException(
                    status_code=status_code,
                    detail=error_data.get('errorMessage', 'Login failed')
                )

            print("POST /login RETURNING: 200 - success")
            return LoginResponse(**result)

        except HTTPException:
            raise
        except Exception as e:
            print(f"POST /login RETURNING: 500 - Exception: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error during login: {str(e)}"
            )

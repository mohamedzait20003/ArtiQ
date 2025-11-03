import uuid
from .controller import Controller
from fastapi import HTTPException, status
from src.models import Auth_Model, Session_Model
from src.types import RegisterRequest, LoginRequest, LoginResponse


class AuthController(Controller):
    """
    Authentication Controller
    Handles user registration, login, and session management
    """

    def register_routes(self):
        """Register authentication routes"""

        @self.router.post("/register", status_code=status.HTTP_201_CREATED)
        async def register(request: RegisterRequest):
            """
            Register a new user

            Args:
                request: Registration data (name, email, password)

            Returns:
                Success message with user ID

            Raises:
                HTTPException: If email already exists or fails
            """
            # Create new user
            user = Auth_Model(
                ID=str(uuid.uuid4()),
                Name=request.name,
                Email=request.email,
                Password=request.password
            )

            if user.save():
                return {"message": "User created successfully"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to register user"
                )

        @self.router.post("/login", response_model=LoginResponse)
        async def login(request: LoginRequest):
            """
            Authenticate user and create session

            Args:
                request: Login credentials (email, password)

            Returns:
                LoginResponse with user info and session token

            Raises:
                HTTPException: If credentials are invalid
            """
            user = Auth_Model.check_user(request.email, request.password)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )

            session_id = str(uuid.uuid4())
            session_token = str(uuid.uuid4())

            session = Session_Model(
                ID=session_id,
                UserID=user.ID,
                Token=session_token
            )

            if session.save():
                return LoginResponse(token=session_token)
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create session"
                )

        @self.router.post("/logout")
        async def logout(session_id: str):
            """
            Logout user by deleting session

            Args:
                session_id: The session ID to delete

            Returns:
                Success message
            """
            session = Session_Model.get({'ID': session_id})
            if session:
                session.delete()

            return {"message": "Logged out successfully"}

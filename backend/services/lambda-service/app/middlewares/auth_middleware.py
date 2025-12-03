"""
Authentication Middleware
Handles token validation and user authentication for protected routes
Node.js-style middleware that runs before route handlers
"""

from fastapi import Request, HTTPException
from app.models import Session_Model, Auth_Model


class AuthUser:
    """Authenticated user object attached to request.state"""
    
    def __init__(self, user: Auth_Model, session: Session_Model):
        self.user = user
        self.session = session
        self.user_id = user.ID
        self.username = user.Name
        self.email = user.Email
        self.is_admin = False  # TODO: Check role for admin status
        
    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission"""
        return self.user.has_permission(permission)


async def auth_optional(request: Request):
    """
    Optional authentication middleware
    Attaches user to request.state.user if valid token provided
    Does not raise exceptions - continues even without auth
    """
    x_authorization = request.headers.get("X-Authorization")
    
    if not x_authorization:
        request.state.user = None
        return
    
    # Remove 'bearer ' prefix if present
    token = x_authorization
    if token.lower().startswith('bearer '):
        token = token[7:]
    
    try:
        # Query sessions table to find session by token
        session_table = Session_Model.table()
        response = session_table.scan(
            FilterExpression='#token = :token',
            ExpressionAttributeNames={'#token': 'Token'},
            ExpressionAttributeValues={
                ':token': Session_Model._hash_token(token)
            },
            Limit=1
        )
        
        items = response.get('Items', [])
        if not items:
            request.state.user = None
            return
        
        session = Session_Model(**items[0])
        
        # Verify session hasn't expired
        import time
        if session.TTL <= int(time.time()):
            request.state.user = None
            return
        
        # Get user from session
        user = Auth_Model.get({'ID': session.UserID})
        if not user:
            request.state.user = None
            return
        
        request.state.user = AuthUser(user=user, session=session)
        
    except Exception as e:
        print(f"Error validating token: {e}")
        request.state.user = None


async def auth_required(request: Request):
    """
    Required authentication middleware
    Validates token and attaches user to request.state.user
    Raises 401 if token is missing or invalid
    """
    x_authorization = request.headers.get("X-Authorization")
    
    if not x_authorization:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )
    
    # Remove 'bearer ' prefix if present
    token = x_authorization
    if token.lower().startswith('bearer '):
        token = token[7:]
    
    try:
        # Query sessions table to find session by token
        session_table = Session_Model.table()
        response = session_table.scan(
            FilterExpression='#token = :token',
            ExpressionAttributeNames={'#token': 'Token'},
            ExpressionAttributeValues={
                ':token': Session_Model._hash_token(token)
            },
            Limit=1
        )
        
        items = response.get('Items', [])
        if not items:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired authentication token"
            )
        
        session = Session_Model(**items[0])
        
        # Verify session hasn't expired
        import time
        if session.TTL <= int(time.time()):
            raise HTTPException(
                status_code=401,
                detail="Session has expired"
            )
        
        # Get user from session
        user = Auth_Model.get({'ID': session.UserID})
        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )
        
        request.state.user = AuthUser(user=user, session=session)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error validating token: {e}")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )


async def auth_admin(request: Request):
    """
    Admin authentication middleware
    Requires valid token AND admin privileges
    Raises 403 if user is not an admin
    Must be used after auth_required
    """
    # First run auth_required
    await auth_required(request)
    
    if not request.state.user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required"
        )


# Export middleware functions
__all__ = [
    'AuthUser',
    'auth_optional',
    'auth_required',
    'auth_admin'
]


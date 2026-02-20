"""Role-based access control decorators."""
from functools import wraps
from fastapi import HTTPException, status
from app.models.user import User


def require_role(*required_roles):
    """
    Decorator to require specific roles for endpoint access.
    
    Usage:
        @require_role("ADMIN", "GESTOR_FINANCIERO")
        async def sensitive_endpoint(current_user: User = Depends(get_current_user)):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = None, **kwargs):
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not authenticated"
                )
            
            user_roles = set(current_user.roles or [])
            required = set(required_roles)
            
            if not user_roles.intersection(required):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required roles: {', '.join(required_roles)}"
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        
        return wrapper
    return decorator


def get_required_roles(roles: list):
    """
    Async function to check if current user has required roles.
    
    Usage:
        async def protected_endpoint(current_user: User = Depends(get_current_user)):
            await get_required_roles(["ADMIN"])(current_user)
    """
    async def check_roles(user: User):
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated"
            )
        
        user_roles = set(user.roles or [])
        required = set(roles)
        
        if not user_roles.intersection(required):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(roles)}"
            )
        
        return user
    
    return check_roles

"""
FastAPI dependencies for authentication and authorization.
Provides reusable dependency injection for protected routes.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
from app.core.jwt import decode_access_token
from app.db.mongo import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase


# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Dependency to get current authenticated admin from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        Decoded token payload with admin_id and organization_id
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify required fields are present
    if "admin_id" not in payload or "organization_id" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


async def get_db() -> AsyncIOMotorDatabase:
    """
    Dependency to get database instance.
    
    Returns:
        AsyncIOMotorDatabase instance
    """
    return get_database()


def verify_organization_access(required_org_id: str):
    """
    Factory function to create a dependency that verifies organization access.
    
    Args:
        required_org_id: Organization ID that must match the token
        
    Returns:
        Dependency function
    """
    async def _verify(current_admin: Dict[str, Any] = Depends(get_current_admin)):
        if current_admin["organization_id"] != required_org_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Organization mismatch"
            )
        return current_admin
    
    return _verify

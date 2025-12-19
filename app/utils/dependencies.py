
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
from app.core.jwt import decode_access_token
from app.db.mongo import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase


security = HTTPBearer()


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

    if "admin_id" not in payload or "organization_id" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


async def get_db() -> AsyncIOMotorDatabase:
    return get_database()


def verify_organization_access(required_org_id: str):
    async def _verify(current_admin: Dict[str, Any] = Depends(get_current_admin)):
        if current_admin["organization_id"] != required_org_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Organization mismatch"
            )
        return current_admin
    
    return _verify

"""
Organization-scoped rate limiting middleware.
Feature #2: Rate limits per organization, not per IP.
Demonstrates true multi-tenant isolation and fairness.
"""
from fastapi import Request, HTTPException, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.jwt import decode_access_token
from typing import Optional


def get_organization_id(request: Request) -> str:
    """
    Extract organization ID from JWT token for rate limiting.
    Falls back to IP address if no valid token is present.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Organization ID or IP address as rate limit key
    """
    # Try to extract JWT token from Authorization header
    auth_header = request.headers.get("Authorization")
    
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        payload = decode_access_token(token)
        
        if payload and "organization_id" in payload:
            # Rate limit by organization ID
            return f"org:{payload['organization_id']}"
    
    # Fallback to IP-based rate limiting for unauthenticated requests
    return f"ip:{get_remote_address(request)}"


# Initialize rate limiter with organization-scoped key function
limiter = Limiter(
    key_func=get_organization_id,
    default_limits=[f"{settings.RATE_LIMIT_PER_ORG}/{settings.RATE_LIMIT_WINDOW_SECONDS}seconds"]
)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """
    Custom handler for rate limit exceeded errors.
    
    Args:
        request: FastAPI request object
        exc: RateLimitExceeded exception
        
    Raises:
        HTTPException: 429 Too Many Requests
    """
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "error": "Rate limit exceeded",
            "message": "Your organization has exceeded the allowed request rate. Please try again later.",
            "retry_after": exc.detail
        }
    )

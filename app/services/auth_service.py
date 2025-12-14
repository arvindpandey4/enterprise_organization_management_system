"""
Authentication service layer.
Handles admin login and JWT token generation with organization context.
"""
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, status
from app.models.admin import AdminLogin, TokenResponse
from app.db.repositories.admin_repository import AdminRepository
from app.db.repositories.organization_repository import OrganizationRepository
from app.core.security import verify_password
from app.core.jwt import create_access_token


class AuthService:
    """Service for authentication business logic."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.org_repo = OrganizationRepository(db)
    
    async def authenticate_admin(self, login_data: AdminLogin) -> TokenResponse:
        """
        Authenticate admin and generate JWT token.
        Searches across all organization collections to find the admin.
        
        Args:
            login_data: Admin login credentials
            
        Returns:
            JWT token response with admin and organization context
            
        Raises:
            HTTPException: If authentication fails
        """
        # Get all active organizations
        organizations = await self.org_repo.find_all(limit=1000, include_deleted=False)
        
        # Search for admin across organization collections
        for org in organizations:
            admin_repo = AdminRepository(self.db, org.collection_name)
            admin = await admin_repo.find_by_email(login_data.email)
            
            if admin:
                # Verify password
                if not verify_password(login_data.password, admin.hashed_password):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Incorrect email or password",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                # Verify admin belongs to this organization
                if admin.organization_id != org.id:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Admin organization mismatch",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                # Generate JWT token with organization context
                token_data = {
                    "sub": admin.id,
                    "admin_id": admin.id,
                    "organization_id": org.id,
                    "email": admin.email
                }
                
                access_token = create_access_token(token_data)
                
                return TokenResponse(
                    access_token=access_token,
                    token_type="bearer",
                    admin_id=admin.id,
                    organization_id=org.id
                )
        
        # Admin not found in any organization
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

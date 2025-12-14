"""
Admin user data models and schemas.
Admins are stored in organization-specific collections.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId


class AdminBase(BaseModel):
    """Base admin schema with common fields."""
    email: EmailStr = Field(..., description="Admin email address")
    name: str = Field(..., min_length=1, max_length=100, description="Admin full name")


class AdminCreate(AdminBase):
    """Schema for creating a new admin."""
    password: str = Field(..., min_length=8, description="Admin password")
    organization_id: str = Field(..., description="Organization ID this admin belongs to")


class AdminInDB(AdminBase):
    """Admin model as stored in database."""
    id: str = Field(alias="_id")
    hashed_password: str
    organization_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class AdminResponse(BaseModel):
    """Admin response schema for API responses."""
    id: str
    email: str
    name: str
    organization_id: str
    created_at: datetime
    
    class Config:
        populate_by_name = True


class AdminLogin(BaseModel):
    """Schema for admin login."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response schema."""
    access_token: str
    token_type: str = "bearer"
    admin_id: str
    organization_id: str

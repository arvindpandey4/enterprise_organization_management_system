"""
Organization data models and schemas.
Defines the structure for organization metadata in the master database.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic models."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class OrganizationBase(BaseModel):
    """Base organization schema with common fields."""
    name: str = Field(..., min_length=1, max_length=100, description="Organization name")
    description: Optional[str] = Field(None, max_length=500, description="Organization description")
    
    @validator('name')
    def validate_name(cls, v):
        """Ensure organization name is alphanumeric with underscores/hyphens only."""
        if not v.replace('_', '').replace('-', '').replace(' ', '').isalnum():
            raise ValueError("Organization name must be alphanumeric (underscores, hyphens, spaces allowed)")
        return v.strip()


class OrganizationCreate(OrganizationBase):
    """Schema for creating a new organization."""
    admin_email: str = Field(..., description="Admin email address")
    admin_password: str = Field(..., min_length=8, description="Admin password (min 8 characters)")
    admin_name: str = Field(..., min_length=1, max_length=100, description="Admin full name")


class OrganizationUpdate(BaseModel):
    """Schema for updating an organization."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            if not v.replace('_', '').replace('-', '').replace(' ', '').isalnum():
                raise ValueError("Organization name must be alphanumeric (underscores, hyphens, spaces allowed)")
            return v.strip()
        return v


class OrganizationInDB(OrganizationBase):
    """Organization model as stored in database."""
    id: str = Field(alias="_id")
    collection_name: str = Field(..., description="Dynamic collection name for this org")
    admin_id: str = Field(..., description="Reference to admin user ID")
    created_at: datetime
    updated_at: datetime
    
    # Soft delete fields (Feature #1: Audit Trail)
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[str] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class OrganizationResponse(BaseModel):
    """Organization response schema for API responses."""
    id: str
    name: str
    description: Optional[str]
    collection_name: str
    admin_id: str
    created_at: datetime
    updated_at: datetime
    is_deleted: bool = False
    
    class Config:
        populate_by_name = True

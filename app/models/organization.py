
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    
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
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    
    @validator('name')
    def validate_name(cls, v):
        if not v.replace('_', '').replace('-', '').replace(' ', '').isalnum():
            raise ValueError("Organization name must be alphanumeric (underscores, hyphens, spaces allowed)")
        return v.strip()


class OrganizationCreate(OrganizationBase):
    admin_email: str = Field(...)
    admin_password: str = Field(..., min_length=8)
    admin_name: str = Field(..., min_length=1, max_length=100)


class OrganizationUpdate(BaseModel):
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
    id: str = Field(alias="_id")
    collection_name: str = Field(...)
    admin_id: str = Field(...)
    created_at: datetime
    updated_at: datetime
    

    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[str] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class OrganizationResponse(BaseModel):
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


from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId


class AdminBase(BaseModel):
    email: EmailStr = Field(...)
    name: str = Field(..., min_length=1, max_length=100)


class AdminCreate(AdminBase):
    password: str = Field(..., min_length=8)
    organization_id: str = Field(...)


class AdminInDB(AdminBase):
    id: str = Field(alias="_id")
    hashed_password: str
    organization_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class AdminResponse(BaseModel):
    id: str
    email: str
    name: str
    organization_id: str
    created_at: datetime
    
    class Config:
        populate_by_name = True


class AdminLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin_id: str
    organization_id: str

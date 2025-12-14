"""
Admin repository for database operations.
Handles admin user operations in organization-specific collections.
"""
from typing import Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.models.admin import AdminInDB


class AdminRepository:
    """Repository for admin data access in organization collections."""
    
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str):
        self.db = db
        self.collection = db[collection_name]
    
    async def create(self, admin_data: dict) -> AdminInDB:
        """
        Create a new admin in the organization collection.
        
        Args:
            admin_data: Admin data dictionary
            
        Returns:
            Created admin model
        """
        admin_data["created_at"] = datetime.utcnow()
        admin_data["updated_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(admin_data)
        admin_data["_id"] = str(result.inserted_id)
        
        return AdminInDB(**admin_data)
    
    async def find_by_id(self, admin_id: str) -> Optional[AdminInDB]:
        """
        Find admin by ID.
        
        Args:
            admin_id: Admin ID
            
        Returns:
            Admin model if found, None otherwise
        """
        admin = await self.collection.find_one({"_id": ObjectId(admin_id)})
        if admin:
            admin["_id"] = str(admin["_id"])
            return AdminInDB(**admin)
        return None
    
    async def find_by_email(self, email: str) -> Optional[AdminInDB]:
        """
        Find admin by email (case-insensitive).
        
        Args:
            email: Admin email
            
        Returns:
            Admin model if found, None otherwise
        """
        admin = await self.collection.find_one({"email": {"$regex": f"^{email}$", "$options": "i"}})
        if admin:
            admin["_id"] = str(admin["_id"])
            return AdminInDB(**admin)
        return None
    
    async def update(self, admin_id: str, update_data: dict) -> Optional[AdminInDB]:
        """
        Update admin data.
        
        Args:
            admin_id: Admin ID
            update_data: Fields to update
            
        Returns:
            Updated admin model if found, None otherwise
        """
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(admin_id)},
            {"$set": update_data},
            return_document=True
        )
        
        if result:
            result["_id"] = str(result["_id"])
            return AdminInDB(**result)
        return None

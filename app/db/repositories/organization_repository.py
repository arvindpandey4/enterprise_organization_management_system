"""
Organization repository for database operations.
Handles CRUD operations on the master database organizations collection.
"""
from typing import Optional, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.models.organization import OrganizationInDB


class OrganizationRepository:
    """Repository for organization data access."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["organizations"]
    
    async def create(self, org_data: dict) -> OrganizationInDB:
        """
        Create a new organization in the master database.
        
        Args:
            org_data: Organization data dictionary
            
        Returns:
            Created organization model
        """
        org_data["created_at"] = datetime.utcnow()
        org_data["updated_at"] = datetime.utcnow()
        org_data["is_deleted"] = False
        
        result = await self.collection.insert_one(org_data)
        org_data["_id"] = str(result.inserted_id)
        
        return OrganizationInDB(**org_data)
    
    async def find_by_id(self, org_id: str, include_deleted: bool = False) -> Optional[OrganizationInDB]:
        """
        Find organization by ID.
        
        Args:
            org_id: Organization ID
            include_deleted: Whether to include soft-deleted organizations
            
        Returns:
            Organization model if found, None otherwise
        """
        query = {"_id": ObjectId(org_id)}
        if not include_deleted:
            query["is_deleted"] = False
        
        org = await self.collection.find_one(query)
        if org:
            org["_id"] = str(org["_id"])
            return OrganizationInDB(**org)
        return None
    
    async def find_by_name(self, name: str, include_deleted: bool = False) -> Optional[OrganizationInDB]:
        """
        Find organization by name (case-insensitive).
        
        Args:
            name: Organization name
            include_deleted: Whether to include soft-deleted organizations
            
        Returns:
            Organization model if found, None otherwise
        """
        query = {"name": {"$regex": f"^{name}$", "$options": "i"}}
        if not include_deleted:
            query["is_deleted"] = False
        
        org = await self.collection.find_one(query)
        if org:
            org["_id"] = str(org["_id"])
            return OrganizationInDB(**org)
        return None
    
    async def find_all(self, skip: int = 0, limit: int = 100, include_deleted: bool = False) -> List[OrganizationInDB]:
        """
        Find all organizations with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: Whether to include soft-deleted organizations
            
        Returns:
            List of organization models
        """
        query = {} if include_deleted else {"is_deleted": False}
        
        cursor = self.collection.find(query).skip(skip).limit(limit)
        organizations = []
        
        async for org in cursor:
            org["_id"] = str(org["_id"])
            organizations.append(OrganizationInDB(**org))
        
        return organizations
    
    async def update(self, org_id: str, update_data: dict) -> Optional[OrganizationInDB]:
        """
        Update organization data.
        
        Args:
            org_id: Organization ID
            update_data: Fields to update
            
        Returns:
            Updated organization model if found, None otherwise
        """
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(org_id), "is_deleted": False},
            {"$set": update_data},
            return_document=True
        )
        
        if result:
            result["_id"] = str(result["_id"])
            return OrganizationInDB(**result)
        return None
    
    async def soft_delete(self, org_id: str, deleted_by: str) -> bool:
        """
        Soft delete an organization (Feature #1: Audit Trail).
        
        Args:
            org_id: Organization ID
            deleted_by: Admin ID who performed the deletion
            
        Returns:
            True if deleted, False otherwise
        """
        result = await self.collection.update_one(
            {"_id": ObjectId(org_id), "is_deleted": False},
            {
                "$set": {
                    "is_deleted": True,
                    "deleted_at": datetime.utcnow(),
                    "deleted_by": deleted_by,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return result.modified_count > 0
    
    async def hard_delete(self, org_id: str) -> bool:
        """
        Permanently delete an organization from the database.
        
        Args:
            org_id: Organization ID
            
        Returns:
            True if deleted, False otherwise
        """
        result = await self.collection.delete_one({"_id": ObjectId(org_id)})
        return result.deleted_count > 0

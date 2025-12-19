
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, status
from app.models.organization import OrganizationCreate, OrganizationUpdate, OrganizationInDB
from app.models.admin import AdminCreate
from app.db.repositories.organization_repository import OrganizationRepository
from app.db.repositories.admin_repository import AdminRepository
from app.core.security import hash_password
import re


class OrganizationService:
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.org_repo = OrganizationRepository(db)
    
    def _generate_collection_name(self, org_name: str) -> str:
        sanitized = re.sub(r'[^a-z0-9_]', '_', org_name.lower().strip())
        sanitized = re.sub(r'_+', '_', sanitized)
        sanitized = sanitized.strip('_')
        
        return f"org_{sanitized}"
    
    async def create_organization(self, org_create: OrganizationCreate) -> OrganizationInDB:

        existing_org = await self.org_repo.find_by_name(org_create.name, include_deleted=True)
        if existing_org:
            if existing_org.is_deleted:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Organization name '{org_create.name}' was previously used and is archived. Please choose a different name."
                )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Organization with name '{org_create.name}' already exists"
            )
        
        collection_name = self._generate_collection_name(org_create.name)
        
        existing_collections = await self.db.list_collection_names()
        if collection_name in existing_collections:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Collection '{collection_name}' already exists"
            )
        
        try:
            org_data = {
                "name": org_create.name,
                "description": org_create.description,
                "collection_name": collection_name,
                "admin_id": ""
            }
            
            organization = await self.org_repo.create(org_data)
            
            admin_repo = AdminRepository(self.db, collection_name)
            
            admin_data = {
                "email": org_create.admin_email,
                "name": org_create.admin_name,
                "hashed_password": hash_password(org_create.admin_password),
                "organization_id": organization.id
            }
            
            admin = await admin_repo.create(admin_data)
            
            organization = await self.org_repo.update(
                organization.id,
                {"admin_id": admin.id}
            )
            
            return organization
            
        except Exception as e:
            if organization:
                await self.org_repo.hard_delete(organization.id)
            if collection_name in await self.db.list_collection_names():
                await self.db.drop_collection(collection_name)
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create organization: {str(e)}"
            )
    
    async def get_organization(self, org_id: str) -> OrganizationInDB:

        organization = await self.org_repo.find_by_id(org_id)
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        return organization
    
    async def list_organizations(self, skip: int = 0, limit: int = 100) -> List[OrganizationInDB]:

        return await self.org_repo.find_all(skip=skip, limit=limit, include_deleted=False)
    
    async def update_organization(
        self, 
        org_id: str, 
        org_update: OrganizationUpdate,
        admin_id: str
    ) -> OrganizationInDB:

        organization = await self.get_organization(org_id)

        if organization.admin_id != admin_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this organization"
            )
        
        update_data = org_update.model_dump(exclude_unset=True)
        
        if "name" in update_data and update_data["name"] != organization.name:
            new_name = update_data["name"]
            
            # Check if new name already exists
            existing_org = await self.org_repo.find_by_name(new_name, include_deleted=True)
            if existing_org and existing_org.id != org_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Organization name '{new_name}' already exists"
                )
            
            new_collection_name = self._generate_collection_name(new_name)
            old_collection_name = organization.collection_name
            
            try:
                old_collection = self.db[old_collection_name]
                new_collection = self.db[new_collection_name]
                
                async for document in old_collection.find():
                    await new_collection.insert_one(document)
                
                # Update organization metadata
                update_data["collection_name"] = new_collection_name
                organization = await self.org_repo.update(org_id, update_data)
                
                # Drop old collection
                await self.db.drop_collection(old_collection_name)
                
                return organization
                
            except Exception as e:
                if new_collection_name in await self.db.list_collection_names():
                    await self.db.drop_collection(new_collection_name)
                
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to migrate organization data: {str(e)}"
                )
        else:
            organization = await self.org_repo.update(org_id, update_data)
            if not organization:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Organization not found"
                )
            return organization
    
    async def delete_organization(self, org_id: str, admin_id: str) -> dict:

        organization = await self.get_organization(org_id)

        if organization.admin_id != admin_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this organization"
            )
        
        try:
            success = await self.org_repo.soft_delete(org_id, admin_id)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Organization not found or already deleted"
                )
            
            
            collection_name = organization.collection_name
            if collection_name in await self.db.list_collection_names():
                await self.db.drop_collection(collection_name)
            
            return {
                "message": "Organization deleted successfully",
                "organization_id": org_id,
                "deleted_by": admin_id,
                "audit_retained": True
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete organization: {str(e)}"
            )

"""
Organization service layer.
Implements business logic for organization management including
dynamic collection creation, safe migrations, and soft-delete with audit trail.
"""
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
    """Service for organization business logic."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.org_repo = OrganizationRepository(db)
    
    def _generate_collection_name(self, org_name: str) -> str:
        """
        Generate a collection name from organization name.
        Format: org_<sanitized_name>
        
        Args:
            org_name: Organization name
            
        Returns:
            Sanitized collection name
        """
        # Convert to lowercase, replace spaces/special chars with underscores
        sanitized = re.sub(r'[^a-z0-9_]', '_', org_name.lower().strip())
        # Remove consecutive underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')
        
        return f"org_{sanitized}"
    
    async def create_organization(self, org_create: OrganizationCreate) -> OrganizationInDB:
        """
        Create a new organization with dynamic collection and admin user.
        This is an atomic operation that:
        1. Validates name uniqueness
        2. Creates organization metadata in master DB
        3. Creates dynamic collection for the organization
        4. Creates admin user in the organization collection
        
        Args:
            org_create: Organization creation data
            
        Returns:
            Created organization model
            
        Raises:
            HTTPException: If organization name already exists or creation fails
        """
        # Check if organization name already exists (including soft-deleted)
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
        
        # Generate collection name
        collection_name = self._generate_collection_name(org_create.name)
        
        # Check if collection already exists (safety check)
        existing_collections = await self.db.list_collection_names()
        if collection_name in existing_collections:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Collection '{collection_name}' already exists"
            )
        
        try:
            # Step 1: Create organization metadata (without admin_id first)
            org_data = {
                "name": org_create.name,
                "description": org_create.description,
                "collection_name": collection_name,
                "admin_id": ""  # Placeholder, will update after admin creation
            }
            
            organization = await self.org_repo.create(org_data)
            
            # Step 2: Create the dynamic collection and admin user
            admin_repo = AdminRepository(self.db, collection_name)
            
            admin_data = {
                "email": org_create.admin_email,
                "name": org_create.admin_name,
                "hashed_password": hash_password(org_create.admin_password),
                "organization_id": organization.id
            }
            
            admin = await admin_repo.create(admin_data)
            
            # Step 3: Update organization with admin_id
            organization = await self.org_repo.update(
                organization.id,
                {"admin_id": admin.id}
            )
            
            return organization
            
        except Exception as e:
            # Rollback: Clean up if anything fails
            if organization:
                await self.org_repo.hard_delete(organization.id)
            if collection_name in await self.db.list_collection_names():
                await self.db.drop_collection(collection_name)
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create organization: {str(e)}"
            )
    
    async def get_organization(self, org_id: str) -> OrganizationInDB:
        """
        Get organization by ID.
        
        Args:
            org_id: Organization ID
            
        Returns:
            Organization model
            
        Raises:
            HTTPException: If organization not found
        """
        organization = await self.org_repo.find_by_id(org_id)
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        return organization
    
    async def list_organizations(self, skip: int = 0, limit: int = 100) -> List[OrganizationInDB]:
        """
        List all active organizations with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of organization models
        """
        return await self.org_repo.find_all(skip=skip, limit=limit, include_deleted=False)
    
    async def update_organization(
        self, 
        org_id: str, 
        org_update: OrganizationUpdate,
        admin_id: str
    ) -> OrganizationInDB:
        """
        Update organization with safe collection migration if name changes.
        
        Args:
            org_id: Organization ID
            org_update: Update data
            admin_id: Admin ID performing the update (for authorization)
            
        Returns:
            Updated organization model
            
        Raises:
            HTTPException: If update fails or unauthorized
        """
        # Get existing organization
        organization = await self.get_organization(org_id)
        
        # Verify admin belongs to this organization
        if organization.admin_id != admin_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this organization"
            )
        
        update_data = org_update.model_dump(exclude_unset=True)
        
        # Handle name change with collection migration
        if "name" in update_data and update_data["name"] != organization.name:
            new_name = update_data["name"]
            
            # Check if new name already exists
            existing_org = await self.org_repo.find_by_name(new_name, include_deleted=True)
            if existing_org and existing_org.id != org_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Organization name '{new_name}' already exists"
                )
            
            # Generate new collection name
            new_collection_name = self._generate_collection_name(new_name)
            old_collection_name = organization.collection_name
            
            try:
                # Migrate data to new collection
                old_collection = self.db[old_collection_name]
                new_collection = self.db[new_collection_name]
                
                # Copy all documents
                async for document in old_collection.find():
                    await new_collection.insert_one(document)
                
                # Update organization metadata
                update_data["collection_name"] = new_collection_name
                organization = await self.org_repo.update(org_id, update_data)
                
                # Drop old collection
                await self.db.drop_collection(old_collection_name)
                
                return organization
                
            except Exception as e:
                # Rollback: drop new collection if created
                if new_collection_name in await self.db.list_collection_names():
                    await self.db.drop_collection(new_collection_name)
                
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to migrate organization data: {str(e)}"
                )
        else:
            # Simple update without migration
            organization = await self.org_repo.update(org_id, update_data)
            if not organization:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Organization not found"
                )
            return organization
    
    async def delete_organization(self, org_id: str, admin_id: str) -> dict:
        """
        Delete organization with soft-delete audit trail and hard-delete of collection.
        Feature #1: Soft-delete metadata but hard-delete dynamic collection.
        
        Args:
            org_id: Organization ID
            admin_id: Admin ID performing the deletion (for authorization and audit)
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If deletion fails or unauthorized
        """
        # Get organization
        organization = await self.get_organization(org_id)
        
        # Verify admin belongs to this organization
        if organization.admin_id != admin_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this organization"
            )
        
        try:
            # Step 1: Soft-delete organization metadata (audit trail)
            success = await self.org_repo.soft_delete(org_id, admin_id)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Organization not found or already deleted"
                )
            
            # Step 2: Hard-delete the dynamic collection
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

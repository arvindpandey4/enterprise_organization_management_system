
from fastapi import APIRouter, Depends, status, Query, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict, Any
from app.models.organization import OrganizationCreate, OrganizationUpdate, OrganizationResponse
from app.services.organization_service import OrganizationService
from app.utils.dependencies import get_db, get_current_admin
from app.utils.responses import success_response
from app.middleware.rate_limit import limiter


router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.post(
    "/",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create Organization",
    description="Create a new organization with dynamic collection and admin user"
)
@limiter.limit("5/minute")
async def create_organization(
    request: Request,
    org_data: OrganizationCreate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):

    org_service = OrganizationService(db)
    organization = await org_service.create_organization(org_data)
    
    return success_response(
        data=OrganizationResponse(**organization.model_dump()).model_dump(),
        message="Organization created successfully"
    )


@router.get(
    "/",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="List Organizations",
    description="Get all active organizations with pagination"
)
async def list_organizations(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):

    org_service = OrganizationService(db)
    organizations = await org_service.list_organizations(skip=skip, limit=limit)
    
    org_responses = [
        OrganizationResponse(**org.model_dump()).model_dump()
        for org in organizations
    ]
    
    return success_response(
        data={
            "organizations": org_responses,
            "count": len(org_responses),
            "skip": skip,
            "limit": limit
        }
    )


@router.get(
    "/{organization_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Get Organization",
    description="Get organization details by ID"
)
async def get_organization(
    organization_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):

    org_service = OrganizationService(db)
    organization = await org_service.get_organization(organization_id)
    
    return success_response(
        data=OrganizationResponse(**organization.model_dump()).model_dump()
    )


@router.put(
    "/{organization_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Update Organization",
    description="Update organization details with safe collection migration"
)
async def update_organization(
    organization_id: str,
    org_update: OrganizationUpdate,
    current_admin: Dict[str, Any] = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_db)
):

    org_service = OrganizationService(db)
    organization = await org_service.update_organization(
        organization_id,
        org_update,
        current_admin["admin_id"]
    )
    
    return success_response(
        data=OrganizationResponse(**organization.model_dump()).model_dump(),
        message="Organization updated successfully"
    )


@router.delete(
    "/{organization_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Delete Organization",
    description="Soft-delete organization with audit trail and hard-delete collection"
)
async def delete_organization(
    organization_id: str,
    current_admin: Dict[str, Any] = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_db)
):

    org_service = OrganizationService(db)
    result = await org_service.delete_organization(
        organization_id,
        current_admin["admin_id"]
    )
    
    return success_response(
        data=result,
        message="Organization deleted successfully"
    )


from fastapi import APIRouter, Depends, status, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.admin import AdminLogin, TokenResponse
from app.services.auth_service import AuthService
from app.utils.dependencies import get_db
from app.utils.responses import success_response
from app.middleware.rate_limit import limiter


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Admin Login",
    description="Authenticate admin and receive JWT access token with organization context"
)

async def login(
    request: Request,
    login_data: AdminLogin,
    db: AsyncIOMotorDatabase = Depends(get_db)
):

    auth_service = AuthService(db)
    token_response = await auth_service.authenticate_admin(login_data)
    
    return success_response(
        data=token_response.model_dump(),
        message="Login successful"
    )

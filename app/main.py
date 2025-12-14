"""
Main FastAPI application.
Enterprise-grade multi-tenant organization management system.
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.mongo import connect_to_mongo, close_mongo_connection
from app.routers import organizations, auth
from app.middleware.rate_limit import limiter, rate_limit_exceeded_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    print("🚀 Starting Organization Management System...")
    try:
        await connect_to_mongo()
        print("✅ Application ready!")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
    
    yield
    
    print("🛑 Shutting down...")
    await close_mongo_connection()
    print("✅ Shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise-Grade Multi-Tenant Organization Management System",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(organizations.router)


@app.get("/", tags=["Health"], include_in_schema=False)
async def root():
    """Root endpoint - Redirects to API documentation."""
    return RedirectResponse(url="/docs")



@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "success": True,
        "status": "healthy",
        "service": settings.APP_NAME
    }

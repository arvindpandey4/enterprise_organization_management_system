"""
MongoDB connection management using Motor (async driver).
Provides database instance and lifecycle management.
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings
from typing import Optional


class MongoDB:
    """MongoDB connection manager with async support."""
    
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None


# Global MongoDB instance
mongodb = MongoDB()


async def connect_to_mongo():
    """
    Establish connection to MongoDB.
    Called on application startup.
    """
    mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
    mongodb.db = mongodb.client[settings.MONGODB_DB_NAME]
    print(f"✅ Connected to MongoDB: {settings.MONGODB_DB_NAME}")


async def close_mongo_connection():
    """
    Close MongoDB connection.
    Called on application shutdown.
    """
    if mongodb.client:
        mongodb.client.close()
        print("✅ MongoDB connection closed")


def get_database() -> AsyncIOMotorDatabase:
    """
    Get the MongoDB database instance.
    
    Returns:
        AsyncIOMotorDatabase instance
        
    Raises:
        RuntimeError: If database is not connected
    """
    if mongodb.db is None:
        raise RuntimeError("Database not connected. Call connect_to_mongo() first.")
    return mongodb.db

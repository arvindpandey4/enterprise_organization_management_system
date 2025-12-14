"""
Standardized API response formats.
Ensures consistent response structure across all endpoints.
"""
from typing import Any, Optional, Dict
from pydantic import BaseModel


class SuccessResponse(BaseModel):
    """Standard success response format."""
    success: bool = True
    data: Any
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response format."""
    success: bool = False
    error: str
    detail: Optional[Dict[str, Any]] = None


def success_response(data: Any, message: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a standardized success response.
    
    Args:
        data: Response data
        message: Optional success message
        
    Returns:
        Formatted success response dictionary
    """
    response = {
        "success": True,
        "data": data
    }
    
    if message:
        response["message"] = message
    
    return response


def error_response(error: str, detail: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create a standardized error response.
    
    Args:
        error: Error message
        detail: Optional error details
        
    Returns:
        Formatted error response dictionary
    """
    response = {
        "success": False,
        "error": error
    }
    
    if detail:
        response["detail"] = detail
    
    return response

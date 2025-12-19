
from typing import Any, Optional, Dict
from pydantic import BaseModel


class SuccessResponse(BaseModel):
    success: bool = True
    data: Any
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[Dict[str, Any]] = None


def success_response(data: Any, message: Optional[str] = None) -> Dict[str, Any]:
    response = {
        "success": True,
        "data": data
    }
    
    if message:
        response["message"] = message
    
    return response


def error_response(error: str, detail: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    response = {
        "success": False,
        "error": error
    }
    
    if detail:
        response["detail"] = detail
    
    return response

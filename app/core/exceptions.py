from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)

class BusinessException(Exception):
    """Base exception for business logic errors"""
    def __init__(self, message: str, code: str = "BUSINESS_ERROR", status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)

class NotFoundException(BusinessException):
    """Resource not found exception"""
    def __init__(self, resource: str, id: int = None):
        message = f"{resource} not found"
        if id:
            message = f"{resource} with id {id} not found"
        super().__init__(message, "NOT_FOUND", 404)

class PermissionDeniedException(BusinessException):
    """Permission denied exception"""
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, "PERMISSION_DENIED", 403)

class ValidationException(BusinessException):
    """Validation exception"""
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR", 400)

class DuplicateException(BusinessException):
    """Duplicate entry exception"""
    def __init__(self, resource: str):
        super().__init__(f"{resource} already exists", "DUPLICATE_ERROR", 409)

def setup_exception_handlers(app: FastAPI):
    """Setup exception handlers for the application"""
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.error(f"HTTP exception: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": "HTTP_ERROR",
                    "message": exc.detail,
                    "status_code": exc.status_code
                }
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.error(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": exc.errors()
                }
            }
        )
    
    @app.exception_handler(BusinessException)
    async def business_exception_handler(request: Request, exc: BusinessException):
        logger.error(f"Business exception: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An internal server error occurred"
                }
            }
        )
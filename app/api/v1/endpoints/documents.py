from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import os
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.modules.users.models import User
from app.modules.documents.service import DocumentService
from app.modules.documents.schemas import (
    DocumentResponse, DocumentListResponse, DocumentVersionResponse
)

router = APIRouter()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    visibility: str = Form("private"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload a document"""
    metadata = {
        "title": title,
        "description": description,
        "tags": tags.split(",") if tags else [],
        "visibility": visibility
    }
    
    document = await DocumentService.upload_file(
        db, file, current_user.id, metadata
    )
    
    return document

@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List documents"""
    documents, total = await DocumentService.list_documents(
        db, current_user, skip, limit, search
    )
    
    return DocumentListResponse(
        items=documents,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

@router.get("/download/{document_id}")
async def download_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Download document"""
    file_path = await DocumentService.get_file_path(db, document_id, current_user.id)
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    document = await DocumentService.get_by_id(db, document_id)
    
    return FileResponse(
        path=file_path,
        filename=document.original_name,
        media_type=document.mime_type
    )
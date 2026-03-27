import os
import shutil
from datetime import datetime
from typing import Optional, List, Dict, Any, BinaryIO
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from fastapi import UploadFile, HTTPException
import uuid
import magic
from app.modules.documents.models import Document, DocumentAudit, DocumentVisibility
from app.modules.users.models import User, UserRole
from app.core.config import settings
from app.modules.audit.service import AuditService

import logging

logger = logging.getLogger(__name__)

class DocumentService:
    @staticmethod
    async def upload_file(
        db: AsyncSession,
        file: UploadFile,
        owner_id: int,
        metadata: Dict[str, Any],
        parent_id: Optional[int] = None
    ) -> Document:
        """Upload a new document"""

        await DocumentService._validate_file(file)
        

        file_ext = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        

        upload_dir = Path(settings.UPLOAD_DIR) / str(owner_id)
        upload_dir.mkdir(parents=True, exist_ok=True)
        

        file_path = upload_dir / unique_filename
        content = await file.read()
        

        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=400, detail="File size exceeds limit")
        
        with open(file_path, "wb") as f:
            f.write(content)
        

        mime = magic.from_buffer(content, mime=True)
        

        document = Document(
            filename=unique_filename,
            original_name=file.filename,
            file_path=str(file_path),
            file_size=len(content),
            mime_type=mime,
            owner_id=owner_id,
            parent_id=parent_id,
            title=metadata.get("title", file.filename),
            description=metadata.get("description"),
            tags=metadata.get("tags", []),
            visibility=metadata.get("visibility", DocumentVisibility.PRIVATE),
            allowed_roles=metadata.get("allowed_roles", []),
            allowed_users=metadata.get("allowed_users", [])
        )
        

        if parent_id:
            parent = await DocumentService.get_by_id(db, parent_id)
            if parent:
                document.version = parent.version + 1
        
        db.add(document)
        await db.commit()
        await db.refresh(document)
        

        await DocumentService._log_audit(
            db, document.id, owner_id, "upload",
            ip_address=metadata.get("ip_address"),
            user_agent=metadata.get("user_agent")
        )
        
        return document
    
    @staticmethod
    async def get_by_id(db: AsyncSession, document_id: int) -> Optional[Document]:
        """Get document by ID"""
        result = await db.execute(
            select(Document).where(
                Document.id == document_id,
                Document.is_deleted == False
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_documents(
        db: AsyncSession,
        user: User,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None,
        visibility: Optional[DocumentVisibility] = None
    ) -> tuple[List[Document], int]:
        """List documents with access control"""
        query = select(Document).where(Document.is_deleted == False)
        

        if user.role == UserRole.ADMIN:

            pass
        else:

            conditions = [
                Document.owner_id == user.id,
                Document.visibility == DocumentVisibility.PUBLIC
            ]
            

            if user.role.value in [r.value for r in DocumentVisibility.ROLE_BASED]:
                conditions.append(
                    and_(
                        Document.visibility == DocumentVisibility.ROLE_BASED,
                        Document.allowed_roles.contains([user.role.value])
                    )
                )
            

            conditions.append(
                and_(
                    Document.visibility == DocumentVisibility.PRIVATE,
                    Document.allowed_users.contains([user.id])
                )
            )
            
            query = query.where(or_(*conditions))
        

        if search:
            query = query.where(
                or_(
                    Document.title.ilike(f"%{search}%"),
                    Document.description.ilike(f"%{search}%"),
                    Document.original_name.ilike(f"%{search}%")
                )
            )
        
        if tags:
            for tag in tags:
                query = query.where(Document.tags.contains([tag]))
        
        if visibility:
            query = query.where(Document.visibility == visibility)
        

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()
        

        query = query.offset(skip).limit(limit).order_by(Document.created_at.desc())
        result = await db.execute(query)
        documents = result.scalars().all()
        
        return list(documents), total
    
    @staticmethod
    async def update_document(
        db: AsyncSession,
        document_id: int,
        user_id: int,
        update_data: Dict[str, Any]
    ) -> Optional[Document]:
        """Update document metadata"""
        document = await DocumentService.get_by_id(db, document_id)
        if not document:
            return None
        

        if document.owner_id != user_id:
            user = await db.get(User, user_id)
            if user.role != UserRole.ADMIN:
                raise HTTPException(status_code=403, detail="Permission denied")
        
        for key, value in update_data.items():
            if value is not None and hasattr(document, key):
                setattr(document, key, value)
        
        await db.commit()
        await db.refresh(document)
        

        await DocumentService._log_audit(
            db, document_id, user_id, "update"
        )
        
        return document
    
    @staticmethod
    async def delete_document(
        db: AsyncSession,
        document_id: int,
        user_id: int
    ) -> bool:
        """Soft delete document"""
        document = await DocumentService.get_by_id(db, document_id)
        if not document:
            return False
        

        if document.owner_id != user_id:
            user = await db.get(User, user_id)
            if user.role != UserRole.ADMIN:
                raise HTTPException(status_code=403, detail="Permission denied")
        
        document.is_deleted = True
        document.deleted_at = datetime.utcnow()
        await db.commit()
        

        await DocumentService._log_audit(
            db, document_id, user_id, "delete"
        )
        
        return True
    
    @staticmethod
    async def get_file_path(db: AsyncSession, document_id: int, user_id: int) -> Optional[str]:
        """Get file path for download with permission check"""
        document = await DocumentService.get_by_id(db, document_id)
        if not document:
            return None
        

        user = await db.get(User, user_id)
        has_access = False
        
        if user.role == UserRole.ADMIN:
            has_access = True
        elif document.owner_id == user_id:
            has_access = True
        elif document.visibility == DocumentVisibility.PUBLIC:
            has_access = True
        elif document.visibility == DocumentVisibility.ROLE_BASED:
            if user.role.value in document.allowed_roles:
                has_access = True
        elif document.visibility == DocumentVisibility.PRIVATE:
            if user_id in document.allowed_users:
                has_access = True
        
        if not has_access:
            raise HTTPException(status_code=403, detail="Access denied")
        

        await DocumentService._log_audit(
            db, document_id, user_id, "download"
        )
        
        return document.file_path
    
    @staticmethod
    async def get_versions(db: AsyncSession, document_id: int) -> List[Document]:
        """Get all versions of a document"""
        result = await db.execute(
            select(Document).where(
                or_(
                    Document.id == document_id,
                    Document.parent_id == document_id
                ),
                Document.is_deleted == False
            ).order_by(Document.version.desc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def _validate_file(file: UploadFile):
        """Validate uploaded file"""

        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
    
    @staticmethod
    async def _log_audit(
        db: AsyncSession,
        document_id: int,
        user_id: int,
        action: str,
        ip_address: str = None,
        user_agent: str = None
    ):
        """Log document audit"""
        audit = DocumentAudit(
            document_id=document_id,
            user_id=user_id,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(audit)
        await db.commit()
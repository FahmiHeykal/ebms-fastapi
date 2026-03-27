from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.modules.users.models import User, UserRole
from app.modules.invoices.service import InvoiceService
from app.modules.invoices.schemas import (
    InvoiceCreate, InvoiceUpdate, InvoiceResponse, InvoiceListResponse,
    PaymentCreate, PaymentResponse
)
from app.modules.audit.service import AuditService

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_invoice(
    invoice_data: InvoiceCreate,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
    db: AsyncSession = Depends(get_db)
):
    """Create new invoice"""
    # Create invoice
    invoice = await InvoiceService.create_invoice(db, invoice_data.dict(), current_user.id)
    
    # Simple response without relationships
    response = {
        "id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "customer_name": invoice.customer_name,
        "customer_email": invoice.customer_email,
        "subtotal": invoice.subtotal,
        "tax_rate": invoice.tax_rate,
        "tax_amount": invoice.tax_amount,
        "discount": invoice.discount,
        "total": invoice.total,
        "status": str(invoice.status),
        "issue_date": invoice.issue_date.isoformat() if invoice.issue_date else None,
        "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
        "created_by_id": invoice.created_by_id,
        "created_at": invoice.created_at.isoformat() if invoice.created_at else None
    }
    
    # Log audit
    await AuditService.log_action(
        db, current_user.id, current_user.email, "create", "invoice",
        record_id=str(invoice.id), new_data=invoice_data.dict()
    )
    
    return response
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.dependencies import require_roles
from app.modules.users.models import UserRole
from app.modules.reports.service import ReportService

router = APIRouter()

@router.get("/tickets/summary")
async def get_ticket_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _: UserRole = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER))
):
    """Get ticket analytics report"""
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).isoformat()
    if not end_date:
        end_date = datetime.now().isoformat()
    
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    
    report = await ReportService.get_ticket_summary(db, start, end)
    return report

@router.get("/invoices/summary")
async def get_invoice_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _: UserRole = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER))
):
    """Get invoice analytics report"""
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).isoformat()
    if not end_date:
        end_date = datetime.now().isoformat()
    
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    
    report = await ReportService.get_invoice_summary(db, start, end)
    return report
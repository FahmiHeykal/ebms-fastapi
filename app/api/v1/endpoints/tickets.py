from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.modules.users.models import User, UserRole
from app.modules.tickets.service import TicketService
from app.modules.tickets.schemas import (
    TicketCreate,
    TicketUpdate,
    TicketResponse,
    TicketListResponse,
    TicketCommentCreate,
    TicketCommentResponse
)
from app.modules.audit.service import AuditService

router = APIRouter()

@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_data: TicketCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    ticket = await TicketService.create(db, ticket_data.dict(), current_user.id)

    ticket.created_by_name = current_user.full_name
    if ticket.assigned_to_id:
        assigned_user = await db.get(User, ticket.assigned_to_id)
        ticket.assigned_to_name = assigned_user.full_name if assigned_user else None

    await AuditService.log_action(
        db,
        current_user.id,
        current_user.email,
        "create",
        "ticket",
        record_id=str(ticket.id),
        new_data=ticket_data.dict()
    )

    return ticket

@router.get("/", response_model=TicketListResponse)
async def list_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_to: Optional[int] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    tickets, total = await TicketService.list_tickets(
        db,
        skip,
        limit,
        status,
        priority,
        assigned_to,
        search,
        current_user.role,
        current_user.id
    )

    return TicketListResponse(
        items=tickets,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    ticket = await TicketService.get_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        if ticket.created_by_id != current_user.id and ticket.assigned_to_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

    return ticket

@router.put("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    ticket = await TicketService.get_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        if ticket.created_by_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

    updated_ticket = await TicketService.update(
        db,
        ticket_id,
        ticket_data.dict(exclude_unset=True),
        current_user.id
    )

    if not updated_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    await AuditService.log_action(
        db,
        current_user.id,
        current_user.email,
        "update",
        "ticket",
        record_id=str(ticket_id),
        new_data=ticket_data.dict(exclude_unset=True)
    )

    return updated_ticket

@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket(
    ticket_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
    db: AsyncSession = Depends(get_db)
):
    deleted = await TicketService.delete(db, ticket_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ticket not found")

    await AuditService.log_action(
        db,
        current_user.id,
        current_user.email,
        "delete",
        "ticket",
        record_id=str(ticket_id)
    )

@router.post("/{ticket_id}/comments", response_model=TicketCommentResponse)
async def add_comment(
    ticket_id: int,
    comment_data: TicketCommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    comment = await TicketService.add_comment(
        db,
        ticket_id,
        comment_data.content,
        current_user.id
    )

    if not comment:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return comment

@router.post("/{ticket_id}/assign/{user_id}")
async def assign_ticket(
    ticket_id: int,
    user_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
    db: AsyncSession = Depends(get_db)
):
    ticket = await TicketService.assign(
        db,
        ticket_id,
        user_id,
        current_user.id
    )

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return {"message": "Ticket assigned successfully"}
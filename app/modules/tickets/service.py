from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.modules.tickets.models import Ticket, TicketComment, TicketActivity, TicketStatus, TicketPriority
from app.modules.users.models import User, UserRole

import logging

logger = logging.getLogger(__name__)

class TicketService:
    @staticmethod
    async def create(db: AsyncSession, ticket_data: Dict[str, Any], user_id: int) -> Ticket:
        ticket = Ticket(
            title=ticket_data["title"],
            description=ticket_data.get("description"),
            priority=ticket_data.get("priority", TicketPriority.MEDIUM),
            created_by_id=user_id,
            assigned_to_id=ticket_data.get("assigned_to_id")
        )
        db.add(ticket)
        await db.commit()
        await db.refresh(ticket)

        await TicketService._log_activity(db, ticket.id, user_id, "created", None, None)

        result = await db.execute(
            select(Ticket)
            .options(selectinload(Ticket.created_by), selectinload(Ticket.assigned_to))
            .where(Ticket.id == ticket.id)
        )
        ticket = result.scalar_one()

        return ticket

    @staticmethod
    async def get_by_id(db: AsyncSession, ticket_id: int) -> Optional[Ticket]:
        result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update(db: AsyncSession, ticket_id: int, update_data: Dict[str, Any], user_id: int) -> Optional[Ticket]:
        ticket = await TicketService.get_by_id(db, ticket_id)
        if not ticket:
            return None

        changes = {}
        for key, value in update_data.items():
            if value is not None and hasattr(ticket, key):
                old_value = getattr(ticket, key)
                if old_value != value:
                    changes[key] = {"old": old_value, "new": value}
                    setattr(ticket, key, value)

        if "status" in update_data:
            if update_data["status"] == TicketStatus.RESOLVED and ticket.resolved_at is None:
                ticket.resolved_at = datetime.utcnow()
            elif update_data["status"] == TicketStatus.CLOSED and ticket.closed_at is None:
                ticket.closed_at = datetime.utcnow()

        await db.commit()
        await db.refresh(ticket)

        for field, change in changes.items():
            await TicketService._log_activity(
                db, ticket_id, user_id, f"updated_{field}",
                str(change["old"]), str(change["new"])
            )

        return ticket

    @staticmethod
    async def delete(db: AsyncSession, ticket_id: int) -> bool:
        ticket = await TicketService.get_by_id(db, ticket_id)
        if not ticket:
            return False

        await db.delete(ticket)
        await db.commit()
        return True

    @staticmethod
    async def assign(db: AsyncSession, ticket_id: int, user_id: int, assigned_by_id: int) -> Optional[Ticket]:
        ticket = await TicketService.get_by_id(db, ticket_id)
        if not ticket:
            return None

        old_assigned = ticket.assigned_to_id
        ticket.assigned_to_id = user_id
        await db.commit()
        await db.refresh(ticket)

        await TicketService._log_activity(
            db, ticket_id, assigned_by_id, "assigned",
            str(old_assigned), str(user_id)
        )

        return ticket

    @staticmethod
    async def add_comment(db: AsyncSession, ticket_id: int, content: str, user_id: int) -> Optional[TicketComment]:
        ticket = await TicketService.get_by_id(db, ticket_id)
        if not ticket:
            return None

        comment = TicketComment(
            ticket_id=ticket_id,
            user_id=user_id,
            content=content
        )
        db.add(comment)
        await db.commit()
        await db.refresh(comment)

        await TicketService._log_activity(db, ticket_id, user_id, "commented", None, content)

        return comment

    @staticmethod
    async def list_tickets(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[int] = None,
        search: Optional[str] = None,
        user_role: UserRole = None,
        user_id: int = None
    ) -> tuple[List[Ticket], int]:
        query = select(Ticket)

        if status:
            query = query.where(Ticket.status == status)
        if priority:
            query = query.where(Ticket.priority == priority)
        if assigned_to:
            query = query.where(Ticket.assigned_to_id == assigned_to)
        if search:
            query = query.where(
                or_(
                    Ticket.title.ilike(f"%{search}%"),
                    Ticket.description.ilike(f"%{search}%")
                )
            )

        if user_role not in [UserRole.ADMIN, UserRole.MANAGER]:
            query = query.where(
                or_(
                    Ticket.created_by_id == user_id,
                    Ticket.assigned_to_id == user_id
                )
            )

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        query = query.offset(skip).limit(limit).order_by(Ticket.created_at.desc())
        result = await db.execute(query)
        tickets = result.scalars().all()

        return list(tickets), total

    @staticmethod
    async def _log_activity(
        db: AsyncSession,
        ticket_id: int,
        user_id: int,
        action: str,
        old_value: str = None,
        new_value: str = None
    ):
        activity = TicketActivity(
            ticket_id=ticket_id,
            user_id=user_id,
            action=action,
            old_value=old_value,
            new_value=new_value
        )
        db.add(activity)
        await db.commit()
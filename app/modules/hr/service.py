from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from app.modules.hr.models import Employee, LeaveRequest, Attendance, LeaveStatus
from app.modules.users.models import User
import logging

logger = logging.getLogger(__name__)

class HRService:
    @staticmethod
    async def create_employee(db: AsyncSession, employee_data: Dict[str, Any]) -> Employee:
        employee = Employee(**employee_data)
        db.add(employee)
        await db.commit()
        await db.refresh(employee)
        return employee

    @staticmethod
    async def get_employee(db: AsyncSession, employee_id: int) -> Optional[Employee]:
        result = await db.execute(select(Employee).where(Employee.id == employee_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_employees(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        department: Optional[str] = None
    ) -> tuple[List[Employee], int]:
        query = select(Employee)

        if department:
            query = query.where(Employee.department == department)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        employees = result.scalars().all()

        return list(employees), total

    @staticmethod
    async def create_leave_request(
        db: AsyncSession,
        leave_data: Dict[str, Any],
        employee_id: int
    ) -> LeaveRequest:
        days = (leave_data["end_date"] - leave_data["start_date"]).days + 1

        leave = LeaveRequest(
            employee_id=employee_id,
            leave_type=leave_data["leave_type"],
            start_date=leave_data["start_date"],
            end_date=leave_data["end_date"],
            days=days,
            reason=leave_data.get("reason")
        )
        db.add(leave)
        await db.commit()
        await db.refresh(leave)
        return leave

    @staticmethod
    async def approve_leave(
        db: AsyncSession,
        leave_id: int,
        approver_id: int,
        approved: bool
    ) -> Optional[LeaveRequest]:
        result = await db.execute(select(LeaveRequest).where(LeaveRequest.id == leave_id))
        leave = result.scalar_one_or_none()

        if not leave:
            return None

        leave.status = LeaveStatus.APPROVED if approved else LeaveStatus.REJECTED
        leave.approved_by_id = approver_id
        leave.approved_at = datetime.utcnow()

        await db.commit()
        await db.refresh(leave)
        return leave

    @staticmethod
    async def get_employee_by_user_id(
        db: AsyncSession,
        user_id: int
    ) -> Optional[Employee]:
        result = await db.execute(select(Employee).where(Employee.user_id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_leave_requests(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        employee_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> tuple[List[LeaveRequest], int]:
        query = select(LeaveRequest)

        if employee_id:
            query = query.where(LeaveRequest.employee_id == employee_id)
        if status:
            query = query.where(LeaveRequest.status == status)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        query = query.offset(skip).limit(limit).order_by(LeaveRequest.created_at.desc())
        result = await db.execute(query)
        leaves = result.scalars().all()

        return list(leaves), total
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date
from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.modules.users.models import User, UserRole
from app.modules.hr.service import HRService
from app.modules.hr.schemas import (
    EmployeeCreate, EmployeeResponse, EmployeeListResponse,
    LeaveRequestCreate, LeaveRequestResponse, LeaveRequestListResponse,
    AttendanceCreate, AttendanceResponse
)
from app.modules.audit.service import AuditService

router = APIRouter()

async def serialize_employee(db: AsyncSession, emp) -> dict:
    user = await db.get(User, emp.user_id)
    return {
        "id": emp.id,
        "user_id": emp.user_id,
        "user_name": user.full_name if user else "",
        "employee_code": emp.employee_code,
        "department": emp.department,
        "position": emp.position,
        "hire_date": emp.hire_date.isoformat() if emp.hire_date else None,
        "salary": emp.salary,
        "bank_account": emp.bank_account,
        "emergency_contact": emp.emergency_contact,
        "emergency_phone": emp.emergency_phone,
        "address": emp.address,
        "created_at": emp.created_at.isoformat() if emp.created_at else None,
        "updated_at": emp.updated_at.isoformat() if emp.updated_at else None
    }


async def serialize_leave(db: AsyncSession, leave) -> dict:
    emp = await HRService.get_employee(db, leave.employee_id)
    emp_user = await db.get(User, emp.user_id) if emp else None
    approver = await db.get(User, leave.approved_by_id) if leave.approved_by_id else None
    return {
        "id": leave.id,
        "employee_id": leave.employee_id,
        "employee_name": emp_user.full_name if emp_user else "",
        "leave_type": leave.leave_type.value if hasattr(leave.leave_type, "value") else str(leave.leave_type),
        "start_date": leave.start_date.isoformat() if leave.start_date else None,
        "end_date": leave.end_date.isoformat() if leave.end_date else None,
        "days": leave.days,
        "reason": leave.reason,
        "status": leave.status.value if hasattr(leave.status, "value") else str(leave.status),
        "approved_by_id": leave.approved_by_id,
        "approved_by_name": approver.full_name if approver else None,
        "approved_at": leave.approved_at.isoformat() if leave.approved_at else None,
        "created_at": leave.created_at.isoformat() if leave.created_at else None,
        "updated_at": leave.updated_at.isoformat() if leave.updated_at else None
    }


async def serialize_attendance(att) -> dict:
    return {
        "id": att.id,
        "employee_id": att.employee_id,
        "date": att.date.isoformat() if att.date else None,
        "check_in": att.check_in.isoformat() if att.check_in else None,
        "check_out": att.check_out.isoformat() if att.check_out else None,
        "status": att.status.value if hasattr(att.status, "value") else str(att.status),
        "notes": att.notes,
        "created_at": att.created_at.isoformat() if att.created_at else None
    }

@router.post("/employees", status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee_data: EmployeeCreate,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
    db: AsyncSession = Depends(get_db)
):
    employee = await HRService.create_employee(db, employee_data.dict())
    return await serialize_employee(db, employee)


@router.get("/employees")
async def list_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    department: Optional[str] = None,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
    db: AsyncSession = Depends(get_db)
):
    employees, total = await HRService.list_employees(db, skip, limit, department)
    items = [await serialize_employee(db, emp) for emp in employees]
    return {
        "items": items,
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": (total + limit - 1) // limit
    }

@router.post("/leave-requests", status_code=status.HTTP_201_CREATED)
async def create_leave_request(
    leave_data: LeaveRequestCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    employee = await HRService.get_employee_by_user_id(db, current_user.id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee record not found")

    leave = await HRService.create_leave_request(db, leave_data.dict(), employee.id)
    return await serialize_leave(db, leave)


@router.get("/leave-requests")
async def list_leave_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    employee = await HRService.get_employee_by_user_id(db, current_user.id)
    employee_id = employee.id if employee else None

    leaves, total = await HRService.list_leave_requests(db, skip, limit, employee_id, status)
    items = [await serialize_leave(db, leave) for leave in leaves]

    return {
        "items": items,
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": (total + limit - 1) // limit
    }


@router.put("/leave-requests/{leave_id}/approve")
async def approve_leave_request(
    leave_id: int,
    approved: bool = True,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
    db: AsyncSession = Depends(get_db)
):
    leave = await HRService.approve_leave(db, leave_id, current_user.id, approved)
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")
    return {"message": f"Leave request {'approved' if approved else 'rejected'}"}


@router.post("/attendance")
async def create_attendance(
    attendance_data: AttendanceCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    employee = await HRService.get_employee_by_user_id(db, current_user.id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee record not found")

    attendance = await HRService.create_attendance(db, attendance_data.dict(), employee.id)
    return await serialize_attendance(attendance)


@router.get("/attendance")
async def list_attendance(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    employee = await HRService.get_employee_by_user_id(db, current_user.id)
    employee_id = employee.id if employee else None

    attendances, total = await HRService.list_attendance(db, skip, limit, employee_id, start_date, end_date)
    items = [await serialize_attendance(att) for att in attendances]

    return {
        "items": items,
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": (total + limit - 1) // limit
    }
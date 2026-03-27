from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List
from enum import Enum

class LeaveType(str, Enum):
    ANNUAL = "annual"
    SICK = "sick"
    PERSONAL = "personal"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    UNPAID = "unpaid"

class LeaveStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    HALF_DAY = "half_day"

class EmployeeBase(BaseModel):
    employee_code: str
    department: Optional[str] = None
    position: Optional[str] = None
    hire_date: date
    salary: Optional[float] = None
    bank_account: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    address: Optional[str] = None

class EmployeeCreate(EmployeeBase):
    user_id: int

class EmployeeResponse(EmployeeBase):
    id: int
    user_id: int
    user_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class LeaveRequestBase(BaseModel):
    leave_type: LeaveType
    start_date: date
    end_date: date
    reason: Optional[str] = None

class LeaveRequestCreate(LeaveRequestBase):
    pass

class LeaveRequestResponse(LeaveRequestBase):
    id: int
    employee_id: int
    employee_name: str
    days: int
    status: LeaveStatus
    approved_by_id: Optional[int]
    approved_by_name: Optional[str]
    approved_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class AttendanceCreate(BaseModel):
    employee_id: int
    date: date
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    status: AttendanceStatus = AttendanceStatus.PRESENT
    notes: Optional[str] = None

class AttendanceResponse(BaseModel):
    id: int
    employee_id: int
    employee_name: str
    date: date
    check_in: Optional[datetime]
    check_out: Optional[datetime]
    status: AttendanceStatus
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class EmployeeListResponse(BaseModel):
    items: List[EmployeeResponse]
    total: int
    page: int
    size: int
    pages: int

class LeaveRequestListResponse(BaseModel):
    items: List[LeaveRequestResponse]
    total: int
    page: int
    size: int
    pages: int
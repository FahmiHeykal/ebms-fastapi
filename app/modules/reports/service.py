from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from typing import Dict, Any, List
import pandas as pd
from io import BytesIO
from app.modules.tickets.models import Ticket
from app.modules.invoices.models import Invoice
from app.modules.inventory.models import Product, StockMovement
from app.modules.hr.models import Employee, Attendance, LeaveRequest
import logging

logger = logging.getLogger(__name__)

class ReportService:
    @staticmethod
    async def get_ticket_summary(
        db: AsyncSession,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        total_result = await db.execute(
            select(func.count()).where(
                Ticket.created_at.between(start_date, end_date)
            )
        )
        total_tickets = total_result.scalar_one()

        status_result = await db.execute(
            select(Ticket.status, func.count())
            .where(Ticket.created_at.between(start_date, end_date))
            .group_by(Ticket.status)
        )
        tickets_by_status = dict(status_result.all())

        priority_result = await db.execute(
            select(Ticket.priority, func.count())
            .where(Ticket.created_at.between(start_date, end_date))
            .group_by(Ticket.priority)
        )
        tickets_by_priority = dict(priority_result.all())

        resolution_result = await db.execute(
            select(func.avg(
                func.extract('epoch', Ticket.resolved_at - Ticket.created_at) / 3600
            )).where(
                and_(
                    Ticket.resolved_at.isnot(None),
                    Ticket.created_at.between(start_date, end_date)
                )
            )
        )
        avg_resolution_hours = resolution_result.scalar_one() or 0

        return {
            "total_tickets": total_tickets,
            "by_status": tickets_by_status,
            "by_priority": tickets_by_priority,
            "avg_resolution_hours": round(avg_resolution_hours, 2),
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }

    @staticmethod
    async def get_invoice_summary(
        db: AsyncSession,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        invoice_result = await db.execute(
            select(
                func.count(Invoice.id),
                func.sum(Invoice.total)
            ).where(
                and_(
                    Invoice.issue_date.between(start_date, end_date),
                    Invoice.status != "cancelled"
                )
            )
        )
        total_invoices, total_revenue = invoice_result.one()

        status_result = await db.execute(
            select(Invoice.status, func.count(), func.sum(Invoice.total))
            .where(Invoice.issue_date.between(start_date, end_date))
            .group_by(Invoice.status)
        )
        by_status = [
            {"status": s, "count": c, "amount": float(a) if a else 0}
            for s, c, a in status_result.all()
        ]

        overdue_result = await db.execute(
            select(func.count())
            .where(
                and_(
                    Invoice.due_date < datetime.utcnow(),
                    Invoice.status == "pending",
                    Invoice.issue_date.between(start_date, end_date)
                )
            )
        )
        overdue_count = overdue_result.scalar_one()

        return {
            "total_invoices": total_invoices or 0,
            "total_revenue": float(total_revenue or 0),
            "by_status": by_status,
            "overdue_count": overdue_count,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }

    @staticmethod
    async def get_inventory_summary(db: AsyncSession) -> Dict[str, Any]:
        total_result = await db.execute(select(func.count(Product.id)))
        total_products = total_result.scalar_one()

        low_stock_result = await db.execute(
            select(func.count()).where(Product.current_stock <= Product.reorder_level)
        )
        low_stock_count = low_stock_result.scalar_one()

        out_stock_result = await db.execute(
            select(func.count()).where(Product.current_stock == 0)
        )
        out_stock_count = out_stock_result.scalar_one()

        value_result = await db.execute(
            select(func.sum(Product.current_stock * Product.cost_price))
        )
        total_value = value_result.scalar_one() or 0

        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        top_moving = await db.execute(
            select(
                Product.name,
                func.sum(StockMovement.quantity)
            )
            .join(StockMovement)
            .where(
                and_(
                    StockMovement.created_at >= thirty_days_ago,
                    StockMovement.movement_type == "out"
                )
            )
            .group_by(Product.id)
            .order_by(func.sum(StockMovement.quantity).desc())
            .limit(10)
        )

        return {
            "total_products": total_products,
            "low_stock_count": low_stock_count,
            "out_stock_count": out_stock_count,
            "total_inventory_value": float(total_value),
            "top_moving_products": [
                {"name": name, "quantity_moved": int(qty)}
                for name, qty in top_moving.all()
            ]
        }

    @staticmethod
    async def get_hr_summary(
        db: AsyncSession,
        month: int,
        year: int
    ) -> Dict[str, Any]:
        start_date = datetime(year, month, 1)
        end_date = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)

        emp_result = await db.execute(select(func.count(Employee.id)))
        total_employees = emp_result.scalar_one()

        leave_result = await db.execute(
            select(
                LeaveRequest.status,
                func.count(),
                func.sum(LeaveRequest.days)
            )
            .where(LeaveRequest.created_at.between(start_date, end_date))
            .group_by(LeaveRequest.status)
        )
        leaves_by_status = [
            {"status": s, "count": c, "total_days": d or 0}
            for s, c, d in leave_result.all()
        ]

        total_workdays = 22
        attendance_result = await db.execute(
            select(func.count())
            .where(
                and_(
                    Attendance.date.between(start_date, end_date),
                    Attendance.status == "present"
                )
            )
        )
        total_present = attendance_result.scalar_one()

        attendance_rate = (total_present / (total_employees * total_workdays)) * 100 if total_employees > 0 else 0

        return {
            "total_employees": total_employees,
            "leave_requests": leaves_by_status,
            "attendance_rate": round(attendance_rate, 2),
            "period": {
                "month": month,
                "year": year
            }
        }

    @staticmethod
    async def export_to_csv(data: List[Dict], filename: str) -> BytesIO:
        output = BytesIO()
        if data:
            df = pd.DataFrame(data)
            df.to_csv(output, index=False)
        output.seek(0)
        return output

    @staticmethod
    async def export_to_excel(data: List[Dict], filename: str) -> BytesIO:
        output = BytesIO()
        if data:
            df = pd.DataFrame(data)
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Report', index=False)
        output.seek(0)
        return output
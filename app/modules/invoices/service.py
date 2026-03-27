from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.modules.invoices.models import Invoice, InvoiceItem, Payment, InvoiceStatus
from app.modules.users.models import User
import logging

logger = logging.getLogger(__name__)

class InvoiceService:
    @staticmethod
    async def generate_invoice_number(db: AsyncSession) -> str:
        """Generate unique invoice number"""
        result = await db.execute(
            select(Invoice.invoice_number)
            .order_by(Invoice.id.desc())
            .limit(1)
        )
        last_number = result.scalar_one_or_none()
        
        if last_number:
            try:
                num = int(last_number.split('-')[1])
                new_num = num + 1
            except:
                new_num = 1
        else:
            new_num = 1
        
        return f"INV-{new_num:06d}"
    
    @staticmethod
    async def create_invoice(
        db: AsyncSession,
        invoice_data: Dict[str, Any],
        user_id: int
    ) -> Invoice:
        """Create new invoice"""
        try:

            subtotal = sum(
                item["quantity"] * item["unit_price"] * (1 - item.get("discount", 0) / 100)
                for item in invoice_data["items"]
            )
            
            tax_amount = subtotal * (invoice_data.get("tax_rate", 0) / 100)
            total = subtotal + tax_amount - invoice_data.get("discount", 0)
            

            invoice_number = await InvoiceService.generate_invoice_number(db)
            

            invoice = Invoice(
                invoice_number=invoice_number,
                customer_name=invoice_data["customer_name"],
                customer_email=invoice_data.get("customer_email"),
                customer_phone=invoice_data.get("customer_phone"),
                customer_address=invoice_data.get("customer_address"),
                subtotal=subtotal,
                tax_rate=invoice_data.get("tax_rate", 0),
                tax_amount=tax_amount,
                discount=invoice_data.get("discount", 0),
                total=total,
                due_date=invoice_data.get("due_date"),
                notes=invoice_data.get("notes"),
                terms=invoice_data.get("terms"),
                created_by_id=user_id
            )
            
            db.add(invoice)
            await db.flush()
            

            for item_data in invoice_data["items"]:
                item_total = item_data["quantity"] * item_data["unit_price"] * (1 - item_data.get("discount", 0) / 100)
                item = InvoiceItem(
                    invoice_id=invoice.id,
                    description=item_data["description"],
                    quantity=item_data["quantity"],
                    unit_price=item_data["unit_price"],
                    discount=item_data.get("discount", 0),
                    total=item_total
                )
                db.add(item)
            
            await db.commit()
            await db.refresh(invoice)
            
            logger.info(f"Invoice created: {invoice.id}")
            return invoice
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating invoice: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    @staticmethod
    async def get_by_id(db: AsyncSession, invoice_id: int) -> Optional[Invoice]:
        """Get invoice by ID"""
        result = await db.execute(
            select(Invoice).where(Invoice.id == invoice_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_invoices(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        customer_name: Optional[str] = None
    ) -> tuple[List[Invoice], int]:
        """List invoices with filters"""
        query = select(Invoice)
        
        if status:
            query = query.where(Invoice.status == status)
        if customer_name:
            query = query.where(Invoice.customer_name.ilike(f"%{customer_name}%"))
        

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()
        

        query = query.offset(skip).limit(limit).order_by(Invoice.created_at.desc())
        result = await db.execute(query)
        invoices = result.scalars().all()
        
        return list(invoices), total
    
    @staticmethod
    async def update_status(
        db: AsyncSession,
        invoice_id: int,
        status: InvoiceStatus
    ) -> Optional[Invoice]:
        """Update invoice status"""
        invoice = await InvoiceService.get_by_id(db, invoice_id)
        if not invoice:
            return None
        
        invoice.status = status
        if status == InvoiceStatus.PAID:
            invoice.paid_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(invoice)
        
        return invoice
    
    @staticmethod
    async def add_payment(
        db: AsyncSession,
        invoice_id: int,
        payment_data: Dict[str, Any],
        user_id: int
    ) -> Optional[Payment]:
        """Add payment to invoice"""
        invoice = await InvoiceService.get_by_id(db, invoice_id)
        if not invoice:
            return None
        

        payment = Payment(
            invoice_id=invoice_id,
            amount=payment_data["amount"],
            payment_method=payment_data["payment_method"],
            reference_number=payment_data.get("reference_number"),
            notes=payment_data.get("notes"),
            received_by_id=user_id
        )
        
        db.add(payment)
        

        result = await db.execute(
            select(func.sum(Payment.amount))
            .where(Payment.invoice_id == invoice_id)
        )
        total_paid = (result.scalar_one() or 0) + payment_data["amount"]
        
        if total_paid >= invoice.total:
            invoice.status = InvoiceStatus.PAID
            invoice.paid_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(payment)
        
        return payment
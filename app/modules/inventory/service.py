from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.modules.inventory.models import Product, Category, StockMovement, LowStockAlert, StockMovementType
from app.modules.audit.service import AuditService
import logging

logger = logging.getLogger(__name__)

class InventoryService:




    @staticmethod
    async def create_product(db: AsyncSession, product_data: Dict[str, Any]) -> Product:
        """Create a new product"""
        result = await db.execute(select(Product).where(Product.sku == product_data["sku"]))
        if result.scalar_one_or_none():
            raise ValueError("Product SKU already exists")

        product = Product(**product_data)
        db.add(product)
        await db.commit()
        await db.refresh(product)

        if product.current_stock <= product.reorder_level:
            await InventoryService._create_low_stock_alert(db, product.id)

        return product

    @staticmethod
    async def get_product_by_id(db: AsyncSession, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        result = await db.execute(select(Product).where(Product.id == product_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_product(db: AsyncSession, product_id: int, update_data: Dict[str, Any]) -> Optional[Product]:
        """Update product"""
        product = await InventoryService.get_product_by_id(db, product_id)
        if not product:
            return None

        for key, value in update_data.items():
            if value is not None and hasattr(product, key):
                setattr(product, key, value)

        await db.commit()
        await db.refresh(product)
        return product

    @staticmethod
    async def delete_product(db: AsyncSession, product_id: int) -> bool:
        """Soft delete product"""
        product = await InventoryService.get_product_by_id(db, product_id)
        if not product:
            return False

        product.is_active = False
        await db.commit()
        return True

    @staticmethod
    async def list_products(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        low_stock: bool = False
    ) -> tuple[List[Product], int]:
        """List products with filters"""
        query = select(Product).where(Product.is_active == True)

        if category_id:
            query = query.where(Product.category_id == category_id)

        if search:
            query = query.where(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.sku.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%")
                )
            )

        if low_stock:
            query = query.where(Product.current_stock <= Product.reorder_level)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        query = query.offset(skip).limit(limit).order_by(Product.created_at.desc())
        result = await db.execute(query)
        products = result.scalars().all()

        return list(products), total




    @staticmethod
    async def record_stock_movement(
        db: AsyncSession,
        movement_data: Dict[str, Any],
        user_id: int
    ) -> StockMovement:
        """Record stock movement and update product stock"""
        try:
            product_id = movement_data["product_id"]
            quantity = movement_data["quantity"]
            movement_type = movement_data["movement_type"]

            logger.info(f"📦 Stock movement: product={product_id}, qty={quantity}, type={movement_type}")

            product = await db.get(Product, product_id)
            if not product:
                raise ValueError("Product not found")

            logger.info(f"✅ Product found: {product.name}, current stock={product.current_stock}")

            if movement_type == StockMovementType.IN:
                product.current_stock += quantity
            elif movement_type == StockMovementType.OUT:
                if product.current_stock < quantity:
                    raise ValueError(f"Insufficient stock. Available: {product.current_stock}")
                product.current_stock -= quantity
            elif movement_type == StockMovementType.ADJUSTMENT:
                product.current_stock = quantity

            movement = StockMovement(
                product_id=product_id,
                quantity=quantity,
                movement_type=movement_type,
                reference_type=movement_data.get("reference_type"),
                reference_id=movement_data.get("reference_id"),
                notes=movement_data.get("notes"),
                performed_by_id=user_id
            )

            db.add(movement)
            await db.commit()
            await db.refresh(movement)

            logger.info(f"✅ Movement recorded: ID={movement.id}")

            if product.current_stock <= product.reorder_level:
                await InventoryService._create_low_stock_alert(db, product_id)

            return movement

        except Exception as e:
            logger.error(f"❌ Error in record_stock_movement: {e}", exc_info=True)
            raise

    @staticmethod
    async def list_stock_movements(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        product_id: Optional[int] = None,
        movement_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> tuple[List[StockMovement], int]:
        """List stock movements with filters"""
        query = select(StockMovement)

        if product_id:
            query = query.where(StockMovement.product_id == product_id)
        if movement_type:
            query = query.where(StockMovement.movement_type == movement_type)
        if start_date:
            query = query.where(StockMovement.created_at >= start_date)
        if end_date:
            query = query.where(StockMovement.created_at <= end_date)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        query = query.offset(skip).limit(limit).order_by(StockMovement.created_at.desc())
        result = await db.execute(query)
        movements = result.scalars().all()

        return list(movements), total




    @staticmethod
    async def _create_low_stock_alert(db: AsyncSession, product_id: int):
        """Create low stock alert if not exists"""
        result = await db.execute(
            select(LowStockAlert).where(
                and_(LowStockAlert.product_id == product_id, LowStockAlert.status == "pending")
            )
        )
        if not result.scalar_one_or_none():
            product = await db.get(Product, product_id)
            alert = LowStockAlert(
                product_id=product_id,
                current_stock=product.current_stock,
                reorder_level=product.reorder_level
            )
            db.add(alert)
            await db.commit()

    @staticmethod
    async def get_low_stock_alerts(db: AsyncSession) -> List[LowStockAlert]:
        """Get all pending low stock alerts"""
        result = await db.execute(
            select(LowStockAlert)
            .where(LowStockAlert.status == "pending")
            .order_by(LowStockAlert.created_at.desc())
        )
        return result.scalars().all()




    @staticmethod
    async def create_category(db: AsyncSession, category_data: Dict[str, Any]) -> Category:
        """Create product category"""

        result = await db.execute(
            select(Category).where(Category.name == category_data["name"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing  # Return existing category instead of error
        
        category = Category(**category_data)
        db.add(category)
        await db.commit()
        await db.refresh(category)
        return category

    @staticmethod
    async def list_categories(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Category], int]:
        """List categories"""
        query = select(Category)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        query = query.offset(skip).limit(limit).order_by(Category.name)
        result = await db.execute(query)
        categories = result.scalars().all()

        return list(categories), total
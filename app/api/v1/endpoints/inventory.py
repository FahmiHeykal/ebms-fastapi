from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.modules.users.models import User, UserRole
from app.modules.inventory.service import InventoryService
from app.modules.inventory.models import Product  # ADD THIS IMPORT
from app.modules.inventory.schemas import (
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse,
    StockMovementRequest, StockMovementResponse, LowStockAlertResponse,
    CategoryCreate, CategoryResponse
)
from app.modules.audit.service import AuditService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# =========================
# PRODUCT ENDPOINTS
# =========================
@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
    db: AsyncSession = Depends(get_db)
):
    product = await InventoryService.create_product(db, product_data.dict())
    await AuditService.log_action(
        db, current_user.id, current_user.email, "create", "product",
        record_id=str(product.id), new_data=product_data.dict()
    )
    return product


@router.get("/products", response_model=ProductListResponse)
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    low_stock: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    products, total = await InventoryService.list_products(db, skip, limit, category_id, search, low_stock)
    return ProductListResponse(
        items=products,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    product = await InventoryService.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
    db: AsyncSession = Depends(get_db)
):
    product = await InventoryService.update_product(db, product_id, product_data.dict(exclude_unset=True))
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    await AuditService.log_action(
        db, current_user.id, current_user.email, "update", "product",
        record_id=str(product_id), new_data=product_data.dict(exclude_unset=True)
    )
    return product


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    deleted = await InventoryService.delete_product(db, product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")

    await AuditService.log_action(
        db, current_user.id, current_user.email, "delete", "product",
        record_id=str(product_id)
    )


# =========================
# STOCK MOVEMENT ENDPOINTS
# =========================
@router.post("/stock/movement")
async def record_stock_movement(
    movement_data: StockMovementRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Record stock movement (in/out/adjustment)"""
    try:
        movement = await InventoryService.record_stock_movement(
            db, movement_data.dict(), current_user.id
        )
        
        # Get product name - use SELECT instead of db.get with Product
        from sqlalchemy import select
        result = await db.execute(select(Product).where(Product.id == movement.product_id))
        product = result.scalar_one_or_none()
        
        # Build response manually
        response = {
            "id": movement.id,
            "product_id": movement.product_id,
            "product_name": product.name if product else "",
            "quantity": movement.quantity,
            "movement_type": movement.movement_type.value if hasattr(movement.movement_type, 'value') else str(movement.movement_type),
            "reference_type": movement.reference_type,
            "reference_id": movement.reference_id,
            "notes": movement.notes,
            "performed_by_id": movement.performed_by_id,
            "performed_by_name": current_user.full_name,
            "created_at": movement.created_at.isoformat() if movement.created_at else None
        }
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stock/movements")
async def list_stock_movements(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    product_id: Optional[int] = None,
    movement_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
    db: AsyncSession = Depends(get_db)
):
    movements, total = await InventoryService.list_stock_movements(
        db, skip, limit, product_id, movement_type, start_date, end_date
    )
    return {
        "items": movements,
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": (total + limit - 1) // limit
    }


# =========================
# LOW STOCK ALERT ENDPOINT
# =========================
@router.get("/alerts", response_model=List[LowStockAlertResponse])
async def get_low_stock_alerts(
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
    db: AsyncSession = Depends(get_db)
):
    alerts = await InventoryService.get_low_stock_alerts(db)
    return alerts


# =========================
# CATEGORY ENDPOINTS
# =========================
@router.post("/categories", status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
    db: AsyncSession = Depends(get_db)
):
    category = await InventoryService.create_category(db, category_data.dict())
    return {
        "id": category.id,
        "name": category.name,
        "description": category.description,
        "parent_id": category.parent_id,
        "created_at": category.created_at.isoformat() if category.created_at else None
    }


@router.get("/categories")
async def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    categories, total = await InventoryService.list_categories(db, skip, limit)
    items = [
        {
            "id": cat.id,
            "name": cat.name,
            "description": cat.description,
            "parent_id": cat.parent_id,
            "created_at": cat.created_at.isoformat() if cat.created_at else None
        }
        for cat in categories
    ]
    return {
        "items": items,
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": (total + limit - 1) // limit
    }
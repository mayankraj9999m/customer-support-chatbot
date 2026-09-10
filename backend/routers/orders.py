from typing import List, Optional
import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database import get_db, Order, OrderItem, Product, User
from routers.auth import get_current_user
import uuid

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/orders", tags=["orders"])

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int

class CheckoutRequest(BaseModel):
    items: List[CartItemCreate]

class OrderItemResponse(BaseModel):
    product_id: int
    quantity: int
    price_at_time: float
    product_name: Optional[str] = None
    product_image: Optional[str] = None

class OrderResponse(BaseModel):
    id: int
    total_amount: float
    status: str
    tracking_number: Optional[str] = None
    items: List[OrderItemResponse]

@router.post("/checkout", response_model=OrderResponse)
async def checkout(request: CheckoutRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not request.items:
        raise HTTPException(status_code=400, detail="Cart is empty")
        
    total_amount = 0.0
    order_items = []
    
    for item in request.items:
        stmt = select(Product).where(Product.id == item.product_id)
        result = await db.execute(stmt)
        product = result.scalars().first()
        
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if product.stock_quantity < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for {product.name}")
            
        total_amount += product.price * item.quantity
        order_items.append(OrderItem(
            product_id=product.id,
            quantity=item.quantity,
            price_at_time=product.price
        ))
        
        product.stock_quantity -= item.quantity
        
    new_order = Order(
        user_id=current_user.id,
        total_amount=total_amount,
        status="Pending",
        tracking_number=f"TRK-{uuid.uuid4().hex[:8].upper()}"
    )
    db.add(new_order)
    await db.flush() # flush to get new_order.id
    
    for oi in order_items:
        oi.order_id = new_order.id
        db.add(oi)
        
    await db.commit()
    await db.refresh(new_order)
    
    # Eagerly load items for response
    stmt = select(Order).options(selectinload(Order.items).selectinload(OrderItem.product)).where(Order.id == new_order.id)
    result = await db.execute(stmt)
    full_order = result.scalars().first()
    
    items_response = [
        OrderItemResponse(
            product_id=i.product_id,
            quantity=i.quantity,
            price_at_time=i.price_at_time,
            product_name=i.product.name if i.product else None,
            product_image=i.product.image_url if i.product else None
        ) for i in full_order.items
    ]
    
    return OrderResponse(
        id=full_order.id,
        total_amount=full_order.total_amount,
        status=full_order.status,
        tracking_number=full_order.tracking_number,
        items=items_response
    )

@router.get("/", response_model=List[OrderResponse])
async def get_my_orders(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(Order).options(
        selectinload(Order.items).selectinload(OrderItem.product)
    ).where(Order.user_id == current_user.id).order_by(Order.id.desc())
    
    result = await db.execute(stmt)
    orders = result.scalars().all()
    
    response = []
    for order in orders:
        items_response = [
            OrderItemResponse(
                product_id=i.product_id,
                quantity=i.quantity,
                price_at_time=i.price_at_time,
                product_name=i.product.name if i.product else None,
                product_image=i.product.image_url if i.product else None
            ) for i in order.items
        ]
        response.append(OrderResponse(
            id=order.id,
            total_amount=order.total_amount,
            status=order.status,
            tracking_number=order.tracking_number,
            items=items_response
        ))
    return response

@router.get("/all", response_model=List[OrderResponse])
async def get_all_orders_admin(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
        
    stmt = select(Order).options(
        selectinload(Order.items).selectinload(OrderItem.product)
    ).order_by(Order.id.desc())
    
    result = await db.execute(stmt)
    orders = result.scalars().all()
    
    response = []
    for order in orders:
        items_response = [
            OrderItemResponse(
                product_id=i.product_id,
                quantity=i.quantity,
                price_at_time=i.price_at_time,
                product_name=i.product.name if i.product else None,
                product_image=i.product.image_url if i.product else None
            ) for i in order.items
        ]
        response.append(OrderResponse(
            id=order.id,
            total_amount=order.total_amount,
            status=order.status,
            tracking_number=order.tracking_number,
            items=items_response
        ))
    return response

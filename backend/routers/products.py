from typing import List
import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db, Product

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/products", tags=["products"])

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    image_url: str
    stock_quantity: int

@router.get("/", response_model=List[ProductResponse])
async def get_products(db: AsyncSession = Depends(get_db)):
    stmt = select(Product)
    result = await db.execute(stmt)
    products = result.scalars().all()
    return products

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Product).where(Product.id == product_id)
    result = await db.execute(stmt)
    product = result.scalars().first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    return product

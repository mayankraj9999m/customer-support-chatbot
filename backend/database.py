import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get DB URL from env, or use a default local one (user must configure this in .env)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment variables.")

# Convert sync URL to async URL
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    # asyncpg doesn't support 'sslmode' or 'channel_binding' as query params directly in the same way.
    # It uses 'ssl=require' instead of 'sslmode=require'.
    if "?" in DATABASE_URL:
        # We will parse out the unsupported query parameters
        import urllib.parse as urlparse
        parts = list(urlparse.urlparse(DATABASE_URL))
        query = dict(urlparse.parse_qsl(parts[4]))
        
        # Translate sslmode to ssl for asyncpg
        if "sslmode" in query:
            query["ssl"] = query.pop("sslmode")
        
        # Remove channel_binding as asyncpg doesn't support this kwarg directly
        if "channel_binding" in query:
            query.pop("channel_binding")
            
        parts[4] = urlparse.urlencode(query)
        DATABASE_URL = urlparse.urlunparse(parts)

elif DATABASE_URL.startswith("sqlite:///"):
    DATABASE_URL = DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///", 1)

# Create engine with driver-specific arguments
engine_kwargs = {
    "echo": False,
    "pool_pre_ping": True,
    "pool_recycle": 300
}

if DATABASE_URL.startswith("postgresql"):
    engine_kwargs["connect_args"] = {"statement_cache_size": 0}

engine = create_async_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

class ConversationLog(Base):
    __tablename__ = "conversation_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_msg = Column(String, index=True)
    intent = Column(String, index=True)
    confidence = Column(Float)
    entities = Column(String) # Stored as JSON string
    timestamp = Column(DateTime, default=datetime.utcnow)

class SessionMemory(Base):
    __tablename__ = "session_memory"

    session_id = Column(String, primary_key=True, index=True)
    history = Column(String, default="[]") # Stored as JSON string
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)
    hashed_password = Column(String)
    role = Column(String, default="customer") # "customer" or "admin"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    orders = relationship("Order", back_populates="owner")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    image_url = Column(String)
    stock_quantity = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_amount = Column(Float)
    status = Column(String, default="Pending") # Pending, Shipped, Delivered, Canceled
    tracking_number = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    price_at_time = Column(Float)
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product")

async def init_db():
    async with engine.begin() as conn:
        # Create tables asynchronously
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with SessionLocal() as db:
        yield db

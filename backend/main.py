import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Configure standardized logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import services and routers
from database import init_db, SessionLocal, Product
from sqlalchemy import select
from services.ml_service import ml_service
from services.llm_service import llm_service
from routers import chat, analytics, auth, products, orders

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Enterprise AI Customer Support...")
    
    # Initialize DB
    logger.info("Initializing database...")
    await init_db()
    
    # Seed Products
    async with SessionLocal() as db:
        stmt = select(Product)
        result = await db.execute(stmt)
        if not result.scalars().first():
            logger.info("Seeding 10 dummy products...")
            dummy_products = [
                Product(name="Wireless Noise-Canceling Headphones", description="Premium over-ear headphones with active noise cancellation and 30-hour battery life.", price=299.99, image_url="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80"),
                Product(name="Minimalist Smartwatch", description="Sleek smartwatch with heart rate monitoring, sleep tracking, and a bright OLED display.", price=199.50, image_url="https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&q=80"),
                Product(name="Ergonomic Office Chair", description="Adjustable lumbar support and breathable mesh back for all-day comfort.", price=149.00, image_url="https://images.unsplash.com/photo-1505843490538-5133c6c7d0e1?w=500&q=80"),
                Product(name="Mechanical Keyboard", description="Tenkeyless layout with tactile blue switches and customizable RGB backlighting.", price=89.99, image_url="https://images.unsplash.com/photo-1595225476474-87563907a212?w=500&q=80"),
                Product(name="Portable Bluetooth Speaker", description="Waterproof, rugged speaker with deep bass and 12-hour playtime.", price=59.99, image_url="https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=500&q=80"),
                Product(name="4K Action Camera", description="Capture your adventures in stunning 4K resolution at 60fps. Includes waterproof housing.", price=249.00, image_url="https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=500&q=80"),
                Product(name="Stainless Steel Water Bottle", description="Double-wall vacuum insulated. Keeps drinks cold for 24 hours or hot for 12 hours.", price=24.95, image_url="https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=500&q=80"),
                Product(name="Yoga Mat with Alignment Lines", description="Eco-friendly, non-slip mat with laser-printed alignment lines for perfect poses.", price=35.00, image_url="https://images.unsplash.com/photo-1592432678016-e910b06b3865?w=500&q=80"),
                Product(name="Ceramic Coffee Mug Set", description="Set of 4 handcrafted ceramic mugs. Microwave and dishwasher safe.", price=45.00, image_url="https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?w=500&q=80"),
                Product(name="Leather Messenger Bag", description="Genuine vintage leather bag with padded laptop compartment. Perfect for work or school.", price=129.99, image_url="https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500&q=80")
            ]
            db.add_all(dummy_products)
            await db.commit()
    
    # Load ML assets
    logger.info("Loading ML assets...")
    ml_service.load_models()
    
    # Initialize LLM
    logger.info("Initializing LLM...")
    llm_service.initialize()
    
    yield
    
    logger.info("Shutting down...")
    # Clean up resources if necessary

app = FastAPI(title="Enterprise AI Customer Support", lifespan=lifespan)

# Setup CORS to allow React frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, tags=["chat"])
app.include_router(analytics.router, tags=["analytics"])
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)

@app.get("/health")
def health_check():
    return {
        "status": "ok", 
        "model_loaded": ml_service.model is not None, 
        "llm_loaded": llm_service.llm is not None
    }



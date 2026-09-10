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
from database import init_db
from services.ml_service import ml_service
from services.llm_service import llm_service
from routers import chat, analytics

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Enterprise AI Customer Support...")
    
    # Initialize DB
    logger.info("Initializing database...")
    await init_db()
    
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

@app.get("/health")
def health_check():
    return {
        "status": "ok", 
        "model_loaded": ml_service.model is not None, 
        "llm_loaded": llm_service.llm is not None
    }

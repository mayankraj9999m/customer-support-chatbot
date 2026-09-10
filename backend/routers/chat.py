import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db, ConversationLog
from services.ml_service import ml_service
from services.llm_service import llm_service
from websockets_manager import manager

logger = logging.getLogger(__name__)
router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default_user"

class ChatResponse(BaseModel):
    intent: str
    confidence: float
    entities: dict
    response: str

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    if not ml_service.model or not ml_service.label_encoder:
        logger.error("Deep Learning model is not loaded.")
        raise HTTPException(status_code=503, detail="Deep Learning model is not loaded.")
        
    user_msg = request.message
    
    # 1. Predict Intent using TF
    predicted_intent, confidence = ml_service.predict_intent(user_msg)
    
    # 2. Extract Entities using spaCy
    entities = ml_service.extract_entities_advanced(user_msg)
    
    # 3. Generate Response
    if confidence < 0.3:
        response_text = "I'm not quite sure I understand. Let me connect you to a human agent."
    elif llm_service.llm:
        try:
            response_text = await llm_service.generate_response(
                db, request.session_id, user_msg, predicted_intent, entities
            )
        except Exception as e:
            logger.error(f"LLM Error: {e}", exc_info=True)
            await db.rollback()
            response_text = llm_service.generate_fallback_response(predicted_intent, entities)
    else:
        response_text = llm_service.generate_fallback_response(predicted_intent, entities)
        
    # 4. Log to Database
    log_entry = ConversationLog(
        user_msg=user_msg,
        intent=predicted_intent,
        confidence=confidence,
        entities=json.dumps(entities)
    )
    db.add(log_entry)
    await db.commit()
    
    # 5. Broadcast to WebSockets
    await manager.broadcast("update_analytics")
    
    return ChatResponse(
        intent=predicted_intent,
        confidence=confidence,
        entities=entities,
        response=response_text
    )

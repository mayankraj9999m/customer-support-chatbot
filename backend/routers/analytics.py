from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from database import get_db, ConversationLog
from websockets_manager import manager

router = APIRouter()

@router.get("/analytics")
async def get_analytics(db: AsyncSession = Depends(get_db)):
    """API for the Admin Dashboard to fetch analytics data."""
    
    # Intent counts
    stmt_intents = select(ConversationLog.intent, func.count(ConversationLog.id)).group_by(ConversationLog.intent)
    result_intents = await db.execute(stmt_intents)
    intent_counts = result_intents.all()
    
    # Average confidence
    stmt_avg = select(func.avg(ConversationLog.confidence))
    result_avg = await db.execute(stmt_avg)
    avg_confidence = result_avg.scalar() or 0.0
    
    # Total messages
    stmt_total = select(func.count(ConversationLog.id))
    result_total = await db.execute(stmt_total)
    total_messages = result_total.scalar() or 0
    
    return {
        "intent_distribution": [{"name": i[0], "value": i[1]} for i in intent_counts],
        "average_confidence": float(avg_confidence),
        "total_messages": total_messages
    }

@router.websocket("/ws/analytics")
async def websocket_analytics(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Just keep the connection open and listen for client disconnects
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

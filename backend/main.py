from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func
import pickle
import asyncio

# Advanced tools
import spacy
import tensorflow as tf
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# Import database module
from database import SessionLocal, ConversationLog
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = FastAPI(title="Enterprise AI Customer Support")

# Setup CORS to allow React frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'tf_intent_model.keras')
ENCODER_PATH = os.path.join(os.path.dirname(__file__), 'tf_label_encoder.pkl')

# Global variables
model = None
label_encoder = None
nlp = None
llm = None

# Contextual Memory Store (Session ID -> List of Langchain Messages)
# We store up to 10 messages per user/session
memory_store = {}

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

@app.on_event("startup")
def load_assets():
    global model, label_encoder, nlp, llm
    
    # Load SpaCy for NER
    try:
        print("Loading spaCy model...")
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("spaCy en_core_web_sm not found. Please run: python -m spacy download en_core_web_sm")
    
    # Load TensorFlow model
    if os.path.exists(MODEL_PATH) and os.path.exists(ENCODER_PATH):
        print(f"Loading TensorFlow model from {MODEL_PATH}...")
        model = tf.keras.models.load_model(MODEL_PATH)
        with open(ENCODER_PATH, 'rb') as f:
            label_encoder = pickle.load(f)
    
    # Initialize LangChain LLM (via OpenRouter)
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if openrouter_key and openrouter_key != "your_openrouter_api_key_here":
        print("Initializing LangChain with OpenRouter...")
        llm = ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_key,
            model="nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free", # Free fast model on openrouter
        )
    else:
        print("WARNING: OPENROUTER_API_KEY not set. RAG/LLM features will fallback to basic templates.")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default_user"

class ChatResponse(BaseModel):
    intent: str
    confidence: float
    entities: dict
    response: str

def extract_entities_advanced(text: str) -> dict:
    entities = {}
    if nlp:
        doc = nlp(text)
        for ent in doc.ents:
            label = ent.label_.lower()
            if label not in entities:
                entities[label] = []
            entities[label].append(ent.text)
            
    import re
    order_match = re.search(r'(?:#|order\s+)(\d+)', text, re.IGNORECASE)
    if order_match:
        entities['order_id'] = [order_match.group(1)]
        
    return entities

def generate_llm_response(session_id: str, user_msg: str, intent: str, entities: dict) -> str:
    """Uses LangChain and conversation history to generate a contextual response."""
    if session_id not in memory_store:
        memory_store[session_id] = [
            SystemMessage(content="You are a helpful, professional customer support assistant for an e-commerce platform. "
                                  "Use the provided context (predicted intent and extracted entities) to answer the user accurately. "
                                  "Keep responses concise and friendly.")
        ]
        
    history = memory_store[session_id]
    
    # Add context as a system nudge before the user's message
    context_nudge = f"[System info: The user's predicted intent is '{intent}'. Extracted entities: {json.dumps(entities)}]"
    history.append(HumanMessage(content=f"{context_nudge}\nUser: {user_msg}"))
    
    # Truncate history to last 10 messages (plus the initial system prompt)
    if len(history) > 11:
        history = [history[0]] + history[-10:]
        
    # Generate response
    response = llm.invoke(history)
    bot_reply = response.content
    
    # Save bot reply to history
    history.append(AIMessage(content=bot_reply))
    memory_store[session_id] = history
    
    return bot_reply

def generate_fallback_response(intent: str, entities: dict) -> str:
    templates = {
        'order_management': "I can help you with your order.",
        'account_management': "I can assist you with your account settings.",
        'billing_and_payment': "I can help with billing or invoices.",
        'issue_support': "I'm sorry you're facing an issue. I'll help you resolve this.",
    }
    reply = templates.get(intent, "I understand you need help. Let me assist you with that.")
    if 'order_id' in entities:
        reply += f" I am checking the status for order #{entities['order_id'][0]}."
    return reply

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    if not model or not label_encoder:
        raise HTTPException(status_code=503, detail="Deep Learning model is not loaded.")
        
    user_msg = request.message
    
    # 1. Predict Intent using TF
    predictions = model.predict(tf.constant([user_msg]))
    predicted_class_idx = np.argmax(predictions[0])
    confidence = float(predictions[0][predicted_class_idx])
    
    predicted_intent = label_encoder.inverse_transform([predicted_class_idx])[0]
    
    # 2. Extract Entities using spaCy
    entities = extract_entities_advanced(user_msg)
    
    # 3. Generate Response (LLM if available, else Fallback)
    if confidence < 0.3:
        response_text = "I'm not quite sure I understand. Let me connect you to a human agent."
    elif llm:
        try:
            response_text = generate_llm_response(request.session_id, user_msg, predicted_intent, entities)
        except Exception as e:
            print(f"LLM Error: {e}")
            response_text = generate_fallback_response(predicted_intent, entities)
    else:
        response_text = generate_fallback_response(predicted_intent, entities)
        
    # 4. Log to Database
    log_entry = ConversationLog(
        user_msg=user_msg,
        intent=predicted_intent,
        confidence=confidence,
        entities=json.dumps(entities)
    )
    db.add(log_entry)
    db.commit()
    
    # 5. Broadcast to WebSockets
    await manager.broadcast("update_analytics")
    
    return ChatResponse(
        intent=predicted_intent,
        confidence=confidence,
        entities=entities,
        response=response_text
    )

@app.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):
    """API for the Admin Dashboard to fetch analytics data."""
    intent_counts = db.query(ConversationLog.intent, func.count(ConversationLog.id)).group_by(ConversationLog.intent).all()
    avg_confidence = db.query(func.avg(ConversationLog.confidence)).scalar() or 0.0
    total_messages = db.query(func.count(ConversationLog.id)).scalar() or 0
    
    return {
        "intent_distribution": [{"name": i[0], "value": i[1]} for i in intent_counts],
        "average_confidence": float(avg_confidence),
        "total_messages": total_messages
    }

@app.websocket("/ws/analytics")
async def websocket_analytics(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Just keep the connection open and listen for client disconnects
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/health")
def health_check():
    return {"status": "ok", "model_loaded": model is not None, "llm_loaded": llm is not None}

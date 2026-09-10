import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, messages_from_dict, messages_to_dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import SessionMemory

class LLMService:
    def __init__(self):
        self.llm = None

    def initialize(self):
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key and gemini_key != "your_gemini_api_key_here":
            print("Initializing LangChain with Gemini API...")
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-3.1-flash-lite",
                google_api_key=gemini_key,
                temperature=0.7
            )
        else:
            print("WARNING: GEMINI_API_KEY not set. RAG/LLM features will fallback to basic templates.")

    async def get_history(self, db: AsyncSession, session_id: str) -> list:
        stmt = select(SessionMemory).where(SessionMemory.session_id == session_id)
        result = await db.execute(stmt)
        mem = result.scalar_one_or_none()
        
        if mem:
            messages_dict = json.loads(mem.history)
            return messages_from_dict(messages_dict)
        else:
            return [
                SystemMessage(content="You are a helpful, professional customer support assistant for an e-commerce platform. "
                                      "Use the provided context (predicted intent and extracted entities) to answer the user accurately. "
                                      "Keep responses concise and friendly.")
            ]

    async def save_history(self, db: AsyncSession, session_id: str, history: list):
        messages_dict = messages_to_dict(history)
        history_json = json.dumps(messages_dict)
        
        stmt = select(SessionMemory).where(SessionMemory.session_id == session_id)
        result = await db.execute(stmt)
        mem = result.scalar_one_or_none()
        
        if mem:
            mem.history = history_json
        else:
            mem = SessionMemory(session_id=session_id, history=history_json)
            db.add(mem)
        
        await db.commit()

    async def generate_response(self, db: AsyncSession, session_id: str, user_msg: str, intent: str, entities: dict) -> str:
        if not self.llm:
            raise RuntimeError("LLM not initialized")
            
        history = await self.get_history(db, session_id)
        
        # Add context as a system nudge before the user's message
        context_nudge = f"[System info: The user's predicted intent is '{intent}'. Extracted entities: {json.dumps(entities)}]"
        history.append(HumanMessage(content=f"{context_nudge}\nUser: {user_msg}"))
        
        # Truncate history to last 10 messages (plus the initial system prompt)
        if len(history) > 11:
            history = [history[0]] + history[-10:]
            
        # Generate response
        response = self.llm.invoke(history)
        bot_reply = response.content
        
        # Handle cases where Gemini API returns a list of text blocks instead of a plain string
        if isinstance(bot_reply, list):
            bot_reply = "".join([block.get("text", "") for block in bot_reply if isinstance(block, dict)])
            
        # Save bot reply to history
        history.append(AIMessage(content=bot_reply))
        await self.save_history(db, session_id, history)
        
        return bot_reply

    def generate_fallback_response(self, intent: str, entities: dict) -> str:
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

llm_service = LLMService()

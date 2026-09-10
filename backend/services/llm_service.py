import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage, messages_from_dict, messages_to_dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database import SessionMemory, SessionLocal, Order, OrderItem
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

@tool
async def get_shipping_status(order_id: int) -> str:
    """Gets the shipping status and ETA of an order. Use this when the user wants to track their order."""
    async with SessionLocal() as db:
        stmt = select(Order).where(Order.id == order_id)
        result = await db.execute(stmt)
        order = result.scalars().first()
        if not order:
            return f"Order #{order_id} not found."
        
        if order.status == "Shipped":
            return f"Your order is Out for Delivery and will arrive by 8 PM today."
        return f"Your order status is {order.status}."

@tool
async def get_order_summary(order_id: int) -> str:
    """Gets the summary details of an order. Use this when the user wants to see their order details."""
    async with SessionLocal() as db:
        stmt = select(Order).options(selectinload(Order.items).selectinload(OrderItem.product)).where(Order.id == order_id)
        result = await db.execute(stmt)
        order = result.scalars().first()
        if not order:
            return f"Order #{order_id} not found."
        
        items_str = ", ".join([f"{i.quantity}x {i.product.name}" for i in order.items if i.product])
        return f"Order: #{order_id} | Total: ${order.total_amount:.2f}\nItems: {items_str}\nStatus: {order.status}"

@tool
async def check_cancel_eligibility(order_id: int) -> str:
    """Checks if an order is eligible for cancellation. Use this BEFORE executing a cancellation."""
    async with SessionLocal() as db:
        stmt = select(Order).where(Order.id == order_id)
        result = await db.execute(stmt)
        order = result.scalars().first()
        if not order:
            return f"Order #{order_id} not found."
            
        if order.status in ["Shipped", "Delivered"]:
            return "ineligible"
        if order.status == "Canceled":
            return "already_canceled"
        return "eligible"

@tool
async def execute_cancellation(order_id: int) -> str:
    """Executes the cancellation of an order permanently. Only call this AFTER checking eligibility and getting explicit user confirmation."""
    async with SessionLocal() as db:
        stmt = select(Order).where(Order.id == order_id)
        result = await db.execute(stmt)
        order = result.scalars().first()
        if not order:
            return f"Order #{order_id} not found."
            
        order.status = "Canceled"
        await db.commit()
        return f"Order #{order_id} has been successfully canceled."

@tool
async def get_recent_orders() -> str:
    """Gets the 5 most recent orders. Use this when the user wants to see their recent orders."""
    async with SessionLocal() as db:
        stmt = select(Order).order_by(Order.created_at.desc()).limit(5)
        result = await db.execute(stmt)
        orders = result.scalars().all()
        if not orders:
            return "No recent orders found."
        
        orders_str = "\n".join([f"Order #{o.id} - ${o.total_amount:.2f} - {o.status}" for o in orders])
        return f"Recent 5 Orders:\n{orders_str}"

class LLMService:
    def __init__(self):
        self.llm = None
        self.llm_with_tools = None
        self.tools_map = {}
        self.system_prompt = ""

    def initialize(self):
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key and gemini_key != "your_gemini_api_key_here":
            print("Initializing LangChain with Gemini API for Function Calling...")
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-3.1-flash-lite",
                google_api_key=gemini_key,
                temperature=0.0 # Low temp for tool reliability
            )
            
            tools_list = [get_shipping_status, get_order_summary, check_cancel_eligibility, execute_cancellation, get_recent_orders]
            self.tools_map = {tool.name: tool for tool in tools_list}
            self.llm_with_tools = self.llm.bind_tools(tools_list)
            
            self.system_prompt = "You are an e-commerce customer support AI. Your goal is to assist users with their orders efficiently, concisely, and safely.\n\nCore Workflow:\nWhen a user inquires about an order (or triggers the 'Manage Order' intent), you must present them with exactly four options: [Track Order], [Order Details], [Cancel Order], and [Recent 5 Orders].\n\nExecution Rules:\n1. Track Order: Trigger get_shipping_status. Do NOT output raw JSON. Provide a single-sentence status and ETA (e.g. 'Your order is Out for Delivery and will arrive by 8 PM today.').\n2. Get Order Details: Trigger get_order_summary. Present data in a highly compact markdown format (Order: #[ID] | Total: [Amount]\\nItems: [Item 1], [Item 2]\\nStatus: [Current Status]).\n3. Cancel Order (Strict Protocol): Trigger check_cancel_eligibility first. If ineligible (e.g. shipped) say: 'This order has already shipped and cannot be canceled. Would you like to start a return instead?' If eligible, you MUST ask for confirmation: 'Are you sure you want to permanently cancel Order #[ID]?' Provide [Yes, Cancel] and [No, Keep it] buttons. Only trigger execute_cancellation if explicitly confirmed.\n4. Recent 5 Orders: Trigger get_recent_orders and present the list in a concise format.\n\nFallback/Conversational Rule:\nIf the user ignores buttons and types a custom request, process it conversationally using the context of their order_id."
            
        else:
            print("WARNING: GEMINI_API_KEY not set. RAG/LLM features will fallback to basic templates.")

    async def get_history(self, db: AsyncSession, session_id: str) -> list:
        stmt = select(SessionMemory).where(SessionMemory.session_id == session_id)
        result = await db.execute(stmt)
        record = result.scalars().first()
        
        if record:
            history_dicts = json.loads(record.history)
            history = messages_from_dict(history_dicts)
            
            # Remove legacy system messages from old history
            history = [msg for msg in history if not isinstance(msg, SystemMessage)]
            return history
            
        return []

    async def save_history(self, db: AsyncSession, session_id: str, history: list):
        history_dicts = messages_to_dict(history)
        
        stmt = select(SessionMemory).where(SessionMemory.session_id == session_id)
        result = await db.execute(stmt)
        record = result.scalars().first()
        
        if record:
            record.history = json.dumps(history_dicts)
        else:
            new_record = SessionMemory(
                session_id=session_id,
                history=json.dumps(history_dicts)
            )
            db.add(new_record)
        await db.commit()

    async def generate_response(self, db: AsyncSession, session_id: str, user_msg: str, intent: str, entities: dict) -> str:
        history = await self.get_history(db, session_id)
        
        # Truncate history to last 10 messages
        if len(history) > 10:
            history = history[-10:]
            
        # Append intent and entities as context for the human message
        context = ""
        if intent and intent != "Unknown":
            context = f"\n[System Note: The predicted intent is '{intent}' and extracted entities are {entities}]"
            
        # Prepare messages
        messages = [SystemMessage(content=self.system_prompt)] + history + [HumanMessage(content=user_msg + context)]
        
        response = await self.llm_with_tools.ainvoke(messages)
        messages.append(response)
        
        while response.tool_calls:
            for tool_call in response.tool_calls:
                tool_func = self.tools_map[tool_call["name"]]
                tool_result = await tool_func.ainvoke(tool_call["args"])
                messages.append(ToolMessage(
                    content=str(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"]
                ))
            response = await self.llm_with_tools.ainvoke(messages)
            messages.append(response)
            
        bot_reply = response.content
        if isinstance(bot_reply, list):
            text_parts = [part.get("text", "") for part in bot_reply if isinstance(part, dict) and "text" in part]
            bot_reply = "".join(text_parts)
            if not bot_reply:
                bot_reply = "I processed your request, but had no text output."
        elif not isinstance(bot_reply, str):
            bot_reply = str(bot_reply)
        
        # Save user message and bot reply to history
        history.append(HumanMessage(content=user_msg))
        history.append(AIMessage(content=bot_reply))
        await self.save_history(db, session_id, history)
        
        return bot_reply

    def generate_fallback_response(self, intent: str, entities: dict) -> str:
        if intent == "Cancel_Order":
            return "I see you want to cancel an order. Can you please provide your order ID?"
        elif intent == "Track_Order":
            return "To track your package, I'll need your order ID or tracking number."
        elif intent == "Return_Refund":
            return "I can help with a return. Are you looking to return a recent purchase?"
        return "I'm here to help! Could you provide a bit more detail about what you need?"

llm_service = LLMService()

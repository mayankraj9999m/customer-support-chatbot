# Phase 3: Enterprise AI & Architecture Implementation Plan

Based on your approvals, we will implement the **Advanced AI** and **Enterprise Architecture** pillars, while heavily redesigning the frontend to match the `DESIGN-pinterest.md` system.

## Open Questions

1. **LLM Provider for RAG:** To implement dynamic generative responses and contextual memory, we need an LLM. Do you have an OpenAI API Key (`OPENAI_API_KEY`) or a Groq API Key (`GROQ_API_KEY`) we can use? (Groq is free and lightning fast).
2. **Redis:** Do you have a local Redis server running for the caching layer, or should we skip Redis for now and focus purely on the WebSockets and AI?

## Proposed Changes

### 1. Frontend Redesign (Pinterest System)
We will completely overhaul the UI using the Pinterest design language (warm creams, 16px border radii, `#e60023` primary red, and masonry layouts).

#### [MODIFY] `frontend/src/index.css` & `App.jsx`
- Introduce the Pinterest color palette (`canvas: #ffffff`, `surface-soft: #fbfbf9`, `primary: #e60023`).
- Implement the 70px display typography and rounded pill buttons.

#### [MODIFY] `frontend/src/ChatWindow.jsx`
- Redesign the chat bubbles to look like Pinterest cards with 16px radius and tight 8px gutters.

#### [MODIFY] `frontend/src/Dashboard.jsx`
- Convert the dashboard layout into a column-based masonry grid for the KPI cards and charts, matching the Pinterest aesthetic.

### 2. Real-Time WebSockets (Enterprise Architecture)
Instead of polling or refreshing the dashboard, it will update live.

#### [MODIFY] `backend/main.py`
- Add a new `WebSocket` endpoint `/ws/analytics`.
- When a new chat message is logged via the `/chat` endpoint, the backend will instantly broadcast the updated analytics to all connected dashboard clients.

#### [MODIFY] `frontend/src/Dashboard.jsx`
- Replace the basic `fetch` call with a WebSocket connection (`ws://localhost:8000/ws/analytics`) that listens for real-time state updates and re-renders the Recharts components instantly.

### 3. RAG & Contextual Memory (Advanced AI)
The bot will now understand conversation history and generate dynamic responses.

#### [MODIFY] `backend/requirements.txt`
- Add `langchain`, `langchain-openai` (or `langchain-groq`), and `python-dotenv`.

#### [MODIFY] `backend/main.py`
- Create a simple in-memory session store (or use Postgres) to hold the last 5 messages per user.
- Add a LangChain pipeline: After the TensorFlow model predicts the intent (e.g., `order_status`), we pass the intent, the extracted entities (via spaCy), and the conversation history to the LLM to generate a fluid, natural response.

## Verification Plan
1. **UI Audit:** Verify the frontend strictly adheres to the Pinterest tokens (colors, typography, radii) from `design.md`.
2. **WebSocket Test:** Open the Dashboard in one window and the Chat in another. Send a message and watch the Dashboard charts update instantly without a page refresh.
3. **AI Context Test:** Ask the bot "Where is my order #123?", and then ask "Can I cancel it?". Verify the bot understands "it" refers to order #123 using its new contextual memory.

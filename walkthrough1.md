# Enterprise Customer Support Chatbot

This project has been upgraded to an **Enterprise-Grade Architecture**, featuring LangChain Generative AI, Real-Time WebSockets, and a premium Pinterest-inspired UI design.

## Architecture Overview

```mermaid
graph TD
    UI[React Frontend (Vite)] <-->|WebSocket: Live Analytics| API(FastAPI Backend)
    UI -->|POST /chat| API
    
    API --> TF(TensorFlow Neural Network: Intent Routing)
    API --> NLP(spaCy NER: Entity Extraction)
    
    TF --> LLM(LangChain + OpenRouter Llama3: Generative Response)
    NLP --> LLM
    
    API --> DB[(Neon Serverless Postgres)]
    
    classDef frontend fill:#e60023,stroke:#cc001f,color:#fff
    classDef backend fill:#10b981,stroke:#064e3b,color:#fff
    classDef database fill:#f59e0b,stroke:#78350f,color:#fff
    classDef ai fill:#6366f1,stroke:#4338ca,color:#fff
    
    class UI frontend
    class API backend
    class TF,NLP,LLM ai
    class DB database
```

---

## 1. Setup Your OpenRouter API Key
Open `backend/.env` and replace `your_openrouter_api_key_here` with your actual OpenRouter API key so the GenAI can function.
```bash
OPENROUTER_API_KEY="sk-or-v1-..."
```
*(If no key is provided, the backend falls back gracefully to hardcoded template replies!)*

---

## 2. Restart Servers & Install Dependencies

**Backend Terminal:**
Stop the running server (Ctrl+C), install the new LangChain packages, and restart:
```bash
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

**Frontend Terminal:**
Your frontend should automatically hot-reload the new styling! If it gets stuck, simply restart it:
```bash
npm run dev
```

---

## 3. Experience the Upgrades

1. **Pinterest UI Redesign:** Open `http://localhost:5173`. You'll immediately notice the premium aesthetic—warm canvases, red accents, masonry grids, and 16px radius cards.
2. **Contextual Memory (RAG):** The bot now remembers the last 10 messages of your conversation. 
   - *Test it out:* Ask "Where is my order #123?", and then follow up with "Can you cancel it?". The Llama-3 LLM will know exactly what "it" refers to!
3. **Real-Time WebSockets:** Open the Admin Dashboard in one window, and the Live Chat in another. When you send a message, watch the dashboard charts update **instantly** without ever refreshing the page.

# Project Requirements Document
## Customer Support Chatbot with NLP Intent Classification

---

## 1. Project Overview

A web-based customer support chatbot that understands user queries in natural language, classifies their intent (e.g., order status, refund request, password reset), extracts relevant entities (order ID, dates), and returns an appropriate automated response — while logging every conversation for review and analytics.

**Domain (example):** E-commerce / telecom customer support (can be swapped for any domain).

---

## 2. Purpose & Business Justification

**Problem it solves:** Support teams get flooded with repetitive, low-complexity queries (order status, refunds, password resets) that don't need a human agent. A bot that triages and auto-resolves these frees up human agents for complex issues.

**Why this project (for you):** It demonstrates the full skill stack the Accenture Advanced Technology Engineer role asks for in one deliverable:
| JD Requirement | Covered By |
|---|---|
| Python | ML model + backend |
| Bots / NLP solutions | Core chatbot engine |
| Frontend (Angular/React) | Chat UI |
| SQL | Conversation/intent logging |
| Cloud (Azure/AWS/GCP) | Deployment |
| AI/ML — supervised learning, NLP | Intent classifier |
| Test automation exposure | Unit tests for API + model |

---

## 3. Functional Requirements

1. User can type a message into a chat interface.
2. System classifies the message into one of a predefined set of intents.
3. System extracts entities where relevant (e.g., order numbers, dates).
4. System returns a relevant, templated (or generative) response based on intent + entities.
5. Every conversation turn is logged to a database (message, predicted intent, confidence score, timestamp).
6. A basic history/dashboard view lets you review past conversations and model confidence.
7. (Stretch) Escalation flag: if confidence is low, response indicates "connecting you to a human agent."

---

## 4. Inputs

| Input | Source | Format |
|---|---|---|
| User message | Chat UI (frontend) | Plain text string |
| Training data | You create it (or scrape a public dataset, e.g., Kaggle "Customer Support on Twitter" or a hand-built intent dataset) | CSV/JSON: `{text, intent_label}` |
| Intent taxonomy | Defined by you upfront | List of ~10–15 intents with 20–30 example phrases each |
| (Optional) Knowledge base | FAQ docs / order database | Structured text or mock SQL table |

**Example training row:**
```json
{"text": "where is my order #4521", "intent": "order_status"}
```

---

## 5. Outputs

| Output | Consumer | Format |
|---|---|---|
| Predicted intent + confidence score | Backend logic | JSON: `{intent: "order_status", confidence: 0.91}` |
| Extracted entities | Backend logic | JSON: `{order_id: "4521"}` |
| Bot response text | Frontend chat UI | Plain text / rendered chat bubble |
| Conversation log | Database (SQL) | Row per turn: `id, user_msg, intent, confidence, entities, timestamp` |
| Analytics view (optional) | You / reviewer | Table or simple chart: intent distribution, avg. confidence, unresolved queries |

---

## 6. How It Works (Architecture)

```
User (React chat UI)
      │  POST /chat  {message: "..."}
      ▼
FastAPI Backend
      │
      ├─► NLP Model (scikit-learn / DistilBERT)
      │        → predicts intent + confidence
      │
      ├─► Entity Extractor (regex / spaCy)
      │        → pulls order IDs, dates, etc.
      │
      ├─► Response Generator
      │        → maps intent → templated reply (or looks up SQL for real data, e.g., order status)
      │
      └─► Logger
               → writes turn to SQL database
      ▼
JSON response returned to frontend → rendered as chat bubble
```

**Tech stack:**
- **ML:** Python, scikit-learn (TF-IDF + Logistic Regression/SVM baseline), optional HuggingFace DistilBERT upgrade
- **Backend:** FastAPI
- **Database:** PostgreSQL or SQLite
- **Frontend:** React
- **Deployment:** Azure App Service or AWS Elastic Beanstalk (free tier)

---

## 7. How It Will Be Used

1. **As a demo:** Live chat interface you can show interviewers — type a query, watch it classify and respond in real time.
2. **As a portfolio piece:** GitHub repo with README explaining architecture, model accuracy, and design decisions.
3. **As a learning vehicle:** Each phase (model → API → frontend → cloud) is a self-contained skill you can speak to individually in an interview.
4. **As an interview talking point:** You can walk through trade-offs — e.g., "I started with TF-IDF + Logistic Regression for interpretability and speed, then evaluated whether a transformer model improved accuracy enough to justify the latency cost."

---

## 8. Success Criteria

- Intent classifier achieves reasonable accuracy (e.g., >85% on a held-out test set for a well-scoped intent set).
- End-to-end flow works: message in → correct intent detected → sensible response out → logged in DB.
- Chat UI is functional and doesn't need to be visually polished, just usable.
- (Stretch) Successfully deployed and reachable via a public URL.

---

## 9. Suggested Build Order

1. Define intent taxonomy + build/label training data
2. Train and evaluate the classifier (Jupyter notebook)
3. Wrap model in FastAPI with `/chat` endpoint
4. Add SQL logging
5. Build React chat UI, connect to API
6. (Optional) Add entity extraction
7. (Optional) Deploy to cloud
8. Write README documenting architecture and results

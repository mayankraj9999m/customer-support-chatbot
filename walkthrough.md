# Advanced Customer Support Chatbot Setup Guide

This guide covers the **Advanced** version of the chatbot featuring a **TensorFlow/Keras Neural Network**, **spaCy** Named Entity Recognition, an **Admin Analytics Dashboard**, and **Pytest** automation.

## Architecture Overview

```mermaid
graph TD
    UI[React Frontend (Vite)] -->|POST /chat| API(FastAPI Backend)
    UI -->|GET /analytics| API
    API --> ML(TensorFlow Neural Network)
    API --> NLP(spaCy NER)
    API --> DB[(Neon Serverless Postgres)]
    
    classDef frontend fill:#3b82f6,stroke:#1e3a8a,color:#fff
    classDef backend fill:#10b981,stroke:#064e3b,color:#fff
    classDef database fill:#f59e0b,stroke:#78350f,color:#fff
    
    class UI frontend
    class API,ML,NLP backend
    class DB database
```

---

## 1. Setting up Neon DB (PostgreSQL)
Ensure your [backend/.env](file:///d:/Mayank%20Raj/CSE%20NITD/AI_ML/Project/backend/.env) file has your Neon DB connection string with `?sslmode=require`.

---

## 2. Backend Setup (TensorFlow + FastAPI)

### Step 2.1: Install Dependencies
Open your backend terminal (stop the server if it's running) and install the new advanced dependencies:
```bash
pip install -r requirements.txt
```

### Step 2.2: Download spaCy Language Model
You need the English core model for advanced entity extraction:
```bash
python -m spacy download en_core_web_sm
```

### Step 2.3: Train the Deep Learning Model
Train the TensorFlow neural network on your dataset. This might take a few minutes as it runs through epochs.
```bash
python train_dl_model.py
```
*(This generates a `tf_intent_model` folder and a `tf_label_encoder.pkl` file).*

### Step 2.4: Start the API Server
Start FastAPI:
```bash
python -m uvicorn main:app --reload
```

### Optional: Run Automated Tests
Open a new terminal in the backend folder and run:
```bash
pytest test_main.py -v
```

---

## 3. Frontend Setup (React + Recharts)

### Step 3.1: Install Charting Library
Open your frontend terminal (stop the server if it's running) and install `recharts`:
```bash
npm install recharts
```

### Step 3.2: Start the Development Server
```bash
npm run dev
```

---

## 4. Test the Advanced Flow

1. Open `http://localhost:5173` in your browser.
2. You'll see a sleek new **Live Chat / Admin Dashboard** toggle in the header.
3. Test the chat with a message like: *"Cancel my order #1234 on Friday."* 
   - spaCy will extract "Friday" as a date entity!
4. Switch to the **Admin Dashboard** tab to see a live visual distribution of all your logged intents in pie and bar charts directly from your Neon database!

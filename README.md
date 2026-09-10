# E-Commerce AI Support Platform

A modern, full-stack E-Commerce application integrating a powerful AI Support Chatbot. Built with a React frontend, FastAPI backend, and PostgreSQL, this project demonstrates a complete user journey—from browsing products and checking out, to getting intelligent support queries resolved instantly.

## 🌟 Features

### 🛒 E-Commerce Core

- **Product Browsing & Search**: Discover products with a dynamic masonry layout and real-time search filtering.
- **Cart & Checkout**: Add products to cart and complete checkout securely.
- **Order Tracking & History**: View past orders and monitor their statuses.
- **User Authentication**: Secure JWT-based authentication for user registration, login, and profile management (update name and password securely).

### 🤖 AI Support Chatbot

- **Context-Aware Assistance**: The chatbot utilizes LangChain and Google's Gemini to answer queries about products, shipping policies, and general store information.
- **Intelligent Tool Routing**: The AI can dynamically invoke backend tools to retrieve user-specific order history and tracking information.
- **Interactive UI**: The chat interface includes smart action buttons (e.g., "[Track Order]", "[Cancel Order]") directly integrated into the AI's responses for quick user actions.

### 📊 Admin Analytics

- **Intent Tracking Dashboard**: A public-facing (or admin-configurable) analytics dashboard built with Recharts, visualizing the distribution of user queries (e.g., Track_Order vs General_Query) and overall AI confidence scores.

## 🛠 Tech Stack

- **Frontend**: React (ReactJs/Vite), React Router, Recharts, Lucide-React, Vanilla CSS (Mobile-Responsive)
- **Backend**: Python, FastAPI, SQLAlchemy (asyncpg), LangChain, Google Gemini API
- **Database**: PostgreSQL / SQL
- **Architecture**: REST API + WebSockets (for analytics/streaming if applicable)

## 🎯 Key Competencies Demonstrated

This project showcases a wide range of modern software engineering skills:

- **Core Programming & Full-Stack Development**: Built a complete, end-to-end application using **ReactJs** for the frontend, **Python** (via **FastAPI**) for the backend, and **PostgreSQL** (**SQL**) for the database.
- **AI/ML & NLP Integration**: Designed and implemented a contextual **NLP Bot** leveraging foundational AI concepts and **LangChain** to solve real-world business challenges.
- **Analytical & Problem Solving**: Engineered dynamic AI tool routing to securely fetch and interpret user-specific database records within a chat interface.
- **Modern Architecture**: Developed in a fast-paced environment using scalable, cloud-ready frameworks, demonstrating readiness for deployment on hyper-scalers (e.g., **AWS**, **Google Cloud**).

## 🚀 Quick Start (Local Development)

### Prerequisites

- Node.js (v18+)
- Python (3.10+)
- PostgreSQL Server

### Backend Setup

1. Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
2. Create a virtual environment and install dependencies:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
    pip install -r requirements.txt
    ```
3. Set up your `.env` file (see `.env.example` if applicable) with your database and API credentials:
    ```env
    DATABASE_URL=postgresql://user:password@localhost:5432/dbname
    GEMINI_API_KEY=your_google_gemini_api_key
    ```
4. Start the FastAPI server:
    ```bash
    python -m uvicorn main:app --reload
    ```

### Frontend Setup

1. Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
2. Install dependencies:
    ```bash
    npm install
    ```
3. Ensure your `.env` is configured to point to the backend:
    ```env
    VITE_API_URL=http://localhost:8000
    ```
4. Start the Vite development server:
    ```bash
    npm run dev
    ```

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 📝 License

This project is licensed under the MIT License.

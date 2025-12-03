# 🎯 Guard-Railed Support Ticket Copilot

A guard-railed AI-powered support ticket processing system that combines FastAPI backend services with a Streamlit frontend interface. This project demonstrates a complete pipeline for processing IT support tickets with built-in safety guardrails, authorization checks, and RAG-based resolution.

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)

## ✨ Features

- **Guard-Railed Processing**: Built-in safety checks to ensure appropriate ticket handling
- **Authorization Engine**: Role-based access control for sensitive operations
- **RAG-Based Resolution**: Retrieval-Augmented Generation for intelligent ticket responses
- **Appropriateness Classification**: Filters out off-scope or inappropriate requests
- **Employee Lookup**: Validates employee information and permissions
- **RESTful API**: Clean FastAPI backend with automatic documentation
- **Interactive UI**: User-friendly Streamlit frontend interface

## 🏗️ Architecture

```
┌─────────────────────┐     HTTP      ┌─────────────────────┐
│   Streamlit UI      │ ────────────► │   FastAPI Backend   │
│  (streamlit_simple) │   Requests    │      (main.py)      │
└─────────────────────┘               └──────────┬──────────┘
                                                 │
                                                 ▼
                                      ┌─────────────────────┐
                                      │   Ticket Pipeline   │
                                      │   (ticket_graph)    │
                                      └──────────┬──────────┘
                                                 │
                    ┌────────────────────────────┼────────────────────────────┐
                    │                            │                            │
                    ▼                            ▼                            ▼
         ┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
         │  Appropriateness │       │  Authorization   │       │   RAG Engine     │
         │   Classifier     │       │  Rules Engine    │       │ (support_ticket) │
         └──────────────────┘       └──────────────────┘       └──────────────────┘
```

## 📦 Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Azure OpenAI API access (for LLM-powered features)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/kasaxena5/ai_hackathon.git
   cd ai_hackathon
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

Update the `.env` file in the project root directory with the api key:
```env
AZURE_OPENAI_API_KEY=your_api_key_here
```

## 🚀 Running the Application

You need to run both the backend and frontend services:

### 1. Start the FastAPI Backend

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### 2. Start the Streamlit Frontend

In a separate terminal (with the virtual environment activated):

```bash
streamlit run streamlit_simple.py
```

The UI will open automatically in your browser.

# Copilot Instructions for Student Portal AI Data Project

This repository implements a Student Portal with AI/ML capabilities, featuring a FastAPI backend, various AI modules (OpenAI, Scikit-learn), and a CLI management tool.

## 🏗 Architecture & Core Components

- **Backend API (`api/`)**: FastAPI application serving as the main interface.
  - **Entry Point**: `api/main.py`.
  - **Routes**: `api/routes/` (Analysis, Chat, Predictions, Recommendations, Students).
  - **Auth**: `X-API-Key` middleware (`api/middleware/auth.py`).
- **Data Layer**: 
  - **DB Abstraction**: `portal_db.py`, `course_db.py`, `enrollment_db.py`.
  - **Data Source**: JSON objects (e.g., `students.json`) or SQL databases.
- **AI & ML Modules**:
  - **AI (`ai/`)**: OpenAI integration for chatbots (`student_advisor.py`), sentiment analysis, and embeddings.
  - **ML (`ml/`)**: Scikit-Learn pipelines. Models stored in `ml/models/*.joblib`.
  - **Analytics (`analytics/`)**: Data analysis scripts and generated reports (`analytics/charts.py`).
- **CLI (`app.py`)**: Interactive console application for database management.

## 🛠 Critical Workflows

- **Start API Server**:
  ```bash
  uvicorn api.main:app --reload --port 8000
  ```
- **Run CLI Portal**:
  ```bash
  python app.py
  ```
- **Testing**:
  - **PowerShell Validation**: `.\test_api.ps1` (requires running server).
  - **Interactive**: Swagger UI at `http://localhost:8000/docs`.
- **Environment Setup**:
  - Copy `.env.example` to `.env` and configure `OPENAI_API_KEY`.
  - Install dependencies: `pip install -r requirements.txt`.

## 📏 Conventions & Patterns

- **Configuration**:
  - **Secrets**: Use `.env` (loaded via `python-dotenv`).
  - **App Config**: `api/config.py` for API settings, `ai/config.py` for AI settings.
- **Output Artifacts**:
  - Generated reports, charts, and models should typically be saved to `outputs/` or component-specific `*/outputs/` directories (e.g., `ai/outputs/`, `ml/outputs/`).
- **Authentication**:
  - API requests normally require the header `X-API-Key: dev-api-key-change-in-production` (default dev key).
- **Error Handling**:
  - Use `api.middleware.error_handler` for standardized JSON error responses.

## 📂 Key Directories

- `api/`: FastAPI application source.
- `ai/`: Logic for RAG, Prompt Engineering, and OpenAI interactions.
- `ml/`: Model training scripts and serialized artifacts.
- `analytics/`: EDA and visualization scripts.
- `data/`: Raw data files (JSON).

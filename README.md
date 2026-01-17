# Student Portal AI

## 🚀 Project Overview
A full-stack Student Portal application integrated with AI/ML capabilities.
- **Student Management:** View profiles and academic history.
- **AI Advisor:** A ChatGPT-style assistant for student queries.
- **Course Recommendations:** Personalized suggestions based on interests and grades.
- **Performance Prediction:** ML-based forecasting of student success.
- **Analytics:** Data visualization of enrollment and performance trends.

## 🛠 Tech Stack
- **Backend:** FastAPI (Python), Uvicorn
- **Frontend:** React, TypeScript, Vite, Recharts, Tailwind/CSS
- **AI/ML:** OpenAI API, Scikit-Learn, Pandas
- **Database:** MySQL (Production) / JSON (Fallback/Mock)

## 💻 Local Setup

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Backend Setup
```bash
# Create virtual environment
python -m venv venv
# Activate (Windows)
.\venv\Scripts\Activate
# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup Environment Variables
# Create a .env file based on .env.example
# Add your OPENAI_API_KEY
```

### 2. Frontend Setup
```bash
cd frontend
npm install
```

## 🔑 Environment Variables

### Backend (.env)
| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Key for AI features | Required |
| `FRONTEND_ORIGIN` | URL of deployed frontend | `http://localhost:5173` |
| `PORT` | Server Port | `8000` |
| `MOCK_MODE` | Use mock data/logic | `false` |
| `ENV` | Environment context | `development` |

### Frontend (.env)
| Variable | Description |
|----------|-------------|
| `VITE_API_BASE_URL` | Full URL of the backend API (e.g. `https://api.render.com`) |

## ▶️ Run Commands (Local)

**Backend:**
```bash
# Run on localhost:8000
python -m uvicorn api.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm run dev
# Open http://localhost:5173
```

## ☁️ Deployment Guide

### 1. Backend (Render)
1. Push code to GitHub.
2. Go to [Render Dashboard](https://dashboard.render.com/) -> New **Web Service**.
3. Connect your repository.
4. **Settings:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables:**
   - `PYTHON_VERSION`: `3.10.12` (or similar)
   - `OPENAI_API_KEY`: `sk-...`
   - `FRONTEND_ORIGIN`: `https://your-frontend.vercel.app` (Add this AFTER deploying frontend)
   - `MOCK_MODE`: `true` (if no DB provided)
6. Deploy and copy the **onrender.com URL**.

### 2. Frontend (Vercel)
1. Go to [Vercel Dashboard](https://vercel.com/dashboard) -> Add New Project.
2. Import the same repository.
3. **Project Settings:**
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend` (Important!)
4. **Environment Variables:**
   - `VITE_API_BASE_URL`: `https://your-backend.onrender.com` (Paste Render URL here)
5. Deploy.

### 3. Final Linking
1. Take the Vercel URL (e.g., `https://student-portal.vercel.app`).
2. Update the **Render** `FRONTEND_ORIGIN` variable with this URL.
3. Redeploy Render service (if needed to pick up the change).

## ✅ Verification
1. **Health Check:** Visit `https://your-backend.onrender.com/health`.
   - Should return `{"status": "ok", ...}`.
2. **Frontend Test:**
   - Open Vercel URL.
   - Login with `S002`.
   - Send a message in Chat.
   - Check Dashboard charts.

## 🔧 Troubleshooting
- **CORS Error (Access-Control-Allow-Origin):**
  - Ensure `FRONTEND_ORIGIN` in Render matches the Vercel URL exactly (no trailing slash).
- **404 Not Found on API calls:**
  - Check `VITE_API_BASE_URL` in Vercel. It must not have a trailing slash, or ensure your code handles it.
  - App uses `${API_BASE_URL}/api/...`, so base URL should be the root domain.
- **Connection Refused:**
  - Ensure Backend is running and Public.
  - Vercel cannot talk to `localhost`.
- **Build Failures:**
  - Check `requirements.txt` includes `uvicorn`.
  - Check Vercel Root Directory is `frontend`.

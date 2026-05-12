# NoteShare AI — Handwritten Note Scoring Platform

## Stack
- **Backend**: FastAPI (Python)
- **Frontend**: React + Vite
- **AI**: Gemini (vision/scoring), Groq (content), HuggingFace (embeddings), OpenRouter (fallback)
- **PDF parsing**: PyMuPDF (local, free)
- **DB**: SQLite via SQLAlchemy (zero setup)

## Project Structure
```
noteshare/
├── backend/
│   ├── main.py              # FastAPI app entry
│   ├── config.py            # API keys + settings
│   ├── database.py          # SQLite setup
│   ├── models/              # DB models
│   │   └── note.py
│   ├── routers/             # API routes
│   │   ├── notes.py         # Upload, list, get
│   │   └── search.py        # Semantic search
│   ├── services/            # AI logic
│   │   ├── pdf_extractor.py # PyMuPDF text extraction
│   │   ├── gemini_scorer.py # Gemini vision scoring
│   │   ├── groq_scorer.py   # Groq content scoring
│   │   ├── embedder.py      # HuggingFace embeddings
│   │   └── recommender.py   # Final score + ranking
│   └── utils/
│       └── helpers.py
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       ├── components/
│       │   ├── NoteCard.jsx
│       │   ├── UploadForm.jsx
│       │   ├── ScoreDisplay.jsx
│       │   └── SearchBar.jsx
│       ├── pages/
│       │   ├── Home.jsx
│       │   ├── Upload.jsx
│       │   └── Subject.jsx
│       └── utils/
│           └── api.js
├── requirements.txt
└── .env.example
```

## Quick Start

### 1. Clone & install backend
```bash
cd backend
pip install -r ../requirements.txt
```

### 2. Set API keys
```bash
cp ../.env.example .env
# Edit .env with your keys
```

### 3. Run backend
```bash
uvicorn main:app --reload --port 8000
```

### 4. Install & run frontend
```bash
cd ../frontend
npm install
npm run dev
```

Open http://localhost:5173

## Get Free API Keys
- **Gemini**: https://aistudio.google.com — no card needed
- **Groq**: https://console.groq.com — no card needed  
- **HuggingFace**: https://huggingface.co/settings/tokens — free tier
- **OpenRouter**: https://openrouter.ai — no card for free models

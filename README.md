# Receipt OCR System

A full-stack receipt extraction system using:

- FastAPI backend
- Tesseract OCR
- Qwen 3.5 0.8B LLM
- PostgreSQL
- Next.js frontend
- Docker support

## How to run locally
uvicorn app.main:app --reload

## How to run Docker
docker compose up --build
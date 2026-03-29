# Receipt OCR Extractor

A full-stack application that extracts structured data from shopping receipts using OCR and a lightweight LLM. Upload receipt images, extract text with Tesseract, then parse and structure the information using Qwen 3.5 0.8B – all exposed through a FastAPI backend and a modern Next.js frontend. Data is persisted in PostgreSQL. Fully containerized with Docker for easy deployment.

## Features

- **Receipt Image Upload** – Drag & drop or select receipt images (PNG, JPEG) via Next.js frontend.
- **OCR Text Extraction** – Uses Tesseract OCR to extract raw text from receipts.
- **LLM‑Powered Parsing** – Qwen 3.5 0.8B (quantized) converts raw OCR text into structured JSON: merchant, date, total amount, tax, line items (name, quantity, unit price, total price).
- **RESTful API** – FastAPI endpoints for health checks, image upload, OCR + parsing, and retrieving stored receipts.
- **Persistent Storage** – PostgreSQL stores receipt metadata, raw OCR text, and extracted structured data.
- **Web Dashboard** – Next.js frontend with Tailwind CSS: view all receipts, inspect OCR text and parsed results, delete entries.
- **Docker Support** – Docker Compose orchestrates backend, frontend, PostgreSQL, and optionally the LLM service.

## Tech Stack

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
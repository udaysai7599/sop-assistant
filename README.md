# SOP Assistant – Authenticated Full-Stack AI Application

## Overview
An AI-powered SOP search and guidance tool with authentication, CRUD, and RAG workflow.

## Tech Stack
- Frontend: React
- Backend: Flask (Python)
- Database: Postgres
- Vector Store: Pinecone/FAISS
- AI Model: GPT-4/Claude

## Setup
### Backend
1. Create virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Configure `.env`
4. Run: `python app.py`

### Frontend
1. `npm install`
2. `npm start`

## Features
- User authentication (JWT)
- SOP CRUD
- AI/RAG Q&A with source-backed answers
- Saved Q&A logs

## Deployment Notes
Use environment variables for secrets. Do not commit `.env`.

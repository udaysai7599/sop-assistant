# SOP Assistant – Authenticated Full-Stack AI Application

## Overview
A working MVP for an AI-powered SOP assistant with authentication, SOP creation, question answering, and saved Q&A history.

## Tech Stack
- Frontend: React
- Backend: Flask (Python)
- Database: SQLite for local development
- AI layer: rule-based retrieval over uploaded SOP content

## Run locally
### Backend
1. `cd backend`
2. `pip install -r requirements.txt`
3. `python app.py`

### Frontend
1. `cd frontend`
2. `npm install`
3. `npm start`

## What works now
- Sign up and login with JWT authentication
- Create SOPs with department labels
- Ask questions against an SOP and receive a source-backed answer
- Save and view answered questions in the dashboard

## Verification
The backend regression test passes with:
- `python -m pytest -q tests/test_end_to_end.py`

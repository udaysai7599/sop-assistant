# SOP Assistant

## Project description
SOP Assistant is a lightweight internal knowledge assistant for teams that need fast access to standard operating procedures. Admins can create and manage SOP documents, while employees can ask natural-language questions and receive guidance grounded in the stored SOP content.

## Problem and target user
Many organizations keep SOPs in scattered documents or static wikis, which makes it difficult for employees to find guidance quickly during time-sensitive work. This project targets operations teams, support staff, HR teams, and other internal users who need reliable answers without manually searching through long documents.

## Features
- Admin-managed SOP creation, editing, and deletion
- Authenticated question answering over stored SOP content
- Basic RAG-style retrieval using sentence scoring
- User-specific Q&A history
- Simple React frontend with a Flask backend

## Tech stack
- Frontend: React, Axios, CSS
- Backend: Flask, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-CORS
- Data store: SQLite by default, with support for PostgreSQL via DATABASE_URL
- Testing: Python unittest

## Setup instructions
1. Clone the repository.
2. Create a Python virtual environment and install backend dependencies:
   - `cd backend`
   - `python -m venv .venv`
   - `source .venv/bin/activate` (or `.venv\Scripts\activate` on Windows)
   - `pip install -r requirements.txt`
3. Install frontend dependencies:
   - `cd frontend`
   - `npm install`
4. Copy the backend example environment file and update the values:
   - `cp .env.example .env` (or copy the file in Windows)

## Run instructions
### Backend
- `cd backend`
- `python app.py`

### Frontend
- `cd frontend`
- `npm start`

The frontend uses the proxy setting in package.json and will communicate with the Flask backend on localhost:5000 by default.

## Required environment variables
Create a .env file in the backend folder with values similar to:
- `DATABASE_URL`: Optional database URI for PostgreSQL or SQLite override
- `JWT_SECRET_KEY`: Secret used to sign authentication tokens
- `ADMIN_SECRET`: Secret used for creating the first admin account
- `FLASK_DEBUG`: Set to `1` for local development debugging
- `APP_HOST` and `APP_PORT`: Optional host and port overrides

## API route descriptions
- `POST /auth/signup`: Create a user account; optionally grant admin role using `admin_secret`
- `POST /auth/login`: Authenticate and receive a JWT
- `GET /auth/me`: Return the current authenticated user profile
- `POST /sops/`: Create a new SOP (admin-only)
- `GET /sops/`: List all available SOPs
- `GET /sops/my-sops`: List only the current admin’s SOPs
- `PUT /sops/<id>` and `DELETE /sops/<id>`: Update or remove an SOP
- `POST /questions/`: Ask a question about a specific SOP
- `GET /questions/history`: Fetch the current user’s question history
- `GET /answers/`: Fetch saved answer history

## Data model description
- `User`: Stores account email, password hash, role, and relationships to SOPs and Q&A logs
- `Department`: Groups SOPs into departments such as IT, HR, or Finance
- `SOP`: Contains the SOP title, content, owner, and department
- `QnALog`: Stores asked questions, generated answers, source excerpts, and timestamps

## Auth flow explanation
Users sign up or log in through the frontend. The backend validates credentials, issues a JWT, and later verifies that token for protected routes. Admin privileges are granted when the provided `admin_secret` matches the configured value.

## AI/RAG workflow explanation
The question-answering flow loads the selected SOP’s content, splits it into sentences, and scores each sentence against the user’s question using token overlap and similarity heuristics. The best-matching sentence is returned as the answer, and the excerpt is saved as the source evidence for the Q&A log.

## Example questions or user tasks
- “How should I handle an incident?”
- “What is the approval workflow for expense reimbursement?”
- “Who should I contact when the production service is down?”

## Deployment notes
The current version is intended for internal use and local development. In production, you should replace the default secrets, use a managed database such as PostgreSQL, and consider a more robust retrieval engine or embedding-based search for large SOP collections.

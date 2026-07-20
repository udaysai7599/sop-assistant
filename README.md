# SOP Assistant

## 1) Project Brief Alignment and Scope

### Problem
Teams often store SOPs in long documents that are difficult to search during time-sensitive tasks. This slows response time and creates inconsistent execution.

### Target user
- Operations team members who need quick answers from SOPs
- Team leads/admins who maintain SOP quality and ownership

### MVP
- Authenticated users can sign up, log in, and ask SOP questions
- Admin users can create/update/delete SOPs
- System stores user-specific Q&A history with evidence sources

### Final scope (implemented)
- Role-based authentication (`admin`, `user`) with protected routes
- SQL relational model for users, SOPs, departments, and Q&A logs
- Source-backed RAG retrieval over SOP content with confidence signal
- Full React + Flask flow for auth, SOP management, asking, and history

## 2) Core Features

- Email/password signup and login
- Admin elevation via configured secret during signup
- Persistent JWT session handling in frontend
- Admin-only SOP CRUD with ownership checks on update/delete
- User question answering over SOP content
- Source-backed answers with top evidence snippets and confidence level
- User-scoped Q&A history and server-side history clearing

## 3) Tech Stack

### Backend
- Flask
- Flask-SQLAlchemy
- Flask-JWT-Extended
- Flask-CORS
- SQLite (default) or PostgreSQL via `DATABASE_URL`

### Frontend
- React (CRA)
- Axios

### Testing
- Python `unittest` end-to-end integration tests

## 4) Repository Structure

- `backend/app.py`: Flask app bootstrap and config
- `backend/models.py`: SQLAlchemy models and relationships
- `backend/routes/auth.py`: signup/login/me/logout
- `backend/routes/sops.py`: SOP CRUD + ownership authorization
- `backend/routes/questions.py`: question answering and history
- `backend/routes/answers.py`: answer history listing/detail/clear
- `backend/rag.py`: retrieval scoring + source-backed answer synthesis
- `backend/tests/test_end_to_end.py`: integration tests
- `frontend/src/components/*`: auth, dashboard, SOP CRUD UI, Ask AI

## 5) Environment Variables

Create `backend/.env`:

- `DATABASE_URL`: Optional. Example: `postgresql://user:pass@localhost/sop_db`
- `JWT_SECRET_KEY`: Required for production. Token signing secret
- `ADMIN_SECRET`: Required for controlled admin signup
- `JWT_ACCESS_TOKEN_EXPIRES_HOURS`: Optional, default `8`
- `FLASK_DEBUG`: Optional, set `1` in development
- `APP_HOST`: Optional host override
- `APP_PORT`: Optional port override

A template is provided in `backend/.env.example`.

## 6) Local Setup and Run

### Backend
1. `cd backend`
2. `python -m venv .venv`
3. Windows: `.venv\Scripts\activate`
4. `pip install -r requirements.txt`
5. `python app.py`

### Frontend
1. `cd frontend`
2. `npm install`
3. `npm start`

Default URLs:
- Backend: `http://localhost:5000`
- Frontend: `http://localhost:3000`

## 7) Authentication and Authorization Flow

1. User signs up with email/password.
2. If signup includes matching `admin_secret`, account is created as `admin`.
3. User logs in and receives JWT access token.
4. Frontend stores token and sends it on protected API requests.
5. Backend enforces:
- Auth required for SOP read/ask/history endpoints
- Admin required for SOP create
- Owner-admin required for SOP update/delete
- User-scoped access for Q&A history and answer detail

## 8) SQL Data Model

### `User`
- `id`, `email` (unique), `password_hash`, `role`
- Relationships: owns many `SOP`, owns many `QnALog`

### `Department`
- `id`, `name` (unique)
- Relationship: has many `SOP`

### `SOP`
- `id`, `title`, `content`, `department_id`, `owner_id`
- Relationship: has many `QnALog`

### `QnALog`
- `id`, `question`, `answer`, `sources`, `created_at`, `user_id`, `sop_id`
- Stores source evidence as JSON in `sources`

## 9) API Routes

### Auth
- `POST /auth/signup`
- `POST /auth/login`
- `GET /auth/me`
- `POST /auth/logout`

### SOPs
- `POST /sops/` (admin only)
- `GET /sops/`
- `GET /sops/my-sops` (admin only)
- `GET /sops/<id>`
- `PUT /sops/<id>` (owner-admin only)
- `DELETE /sops/<id>` (owner-admin only)

### Questions / Answers
- `POST /questions/` (ask question; supports `sop_id` or cross-SOP retrieval)
- `GET /questions/history`
- `GET /questions/<id>`
- `GET /answers/`
- `GET /answers/<id>`
- `DELETE /answers/` (clear current user history)

## 10) RAG Workflow (Source-Backed)

1. Collect candidate SOP content (selected SOP or all SOPs)
2. Split SOP text into sentence chunks
3. Score each chunk using:
- lexical overlap recall
- lexical overlap precision
- fuzzy similarity
4. Rank chunks and select top evidence (`top_k`)
5. Build response from highest-ranked chunk and include supporting SOP titles
6. Return answer + sources + confidence (`high` or `low`)
7. Persist question, answer, and sources in `QnALog`

Low-confidence behavior is explicit in the response so users can verify critical decisions.

## 11) Verification and Tests

Run backend integration tests:

1. `cd backend`
2. `python -m unittest tests/test_end_to_end.py`

Covered flows:
- Signup/login/create SOP/ask question/history
- Ownership authorization (admin cannot delete another admin's SOP)
- User-scoped history and clear-history behavior
- Source-backed response structure

## 12) Example User Tasks

- "I am a user. I can ask: How do I handle repeated service outages?"
- "I am an admin. I can create and edit IT, HR, and Finance SOPs."
- "I can review my previous answers and source evidence in history."

## 13) Known Limitations

- Retrieval is lexical/fuzzy and not embedding-based semantic search
- No token revocation list (logout is stateless)
- No production deployment included in this submission by requirement

## 14) Future Improvements

- Add embedding-based retrieval and vector index for larger SOP corpora
- Add refresh-token rotation and token revocation support
- Add pagination/search filters for SOPs and history
- Add CI pipeline with lint/test gates and coverage report
- Add migration tooling (Alembic) for schema evolution

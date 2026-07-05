# Implementation Guide: Role-Based SOP Management System

## Quick Start Guide

### 1. Update Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Backend configuration
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
ADMIN_SECRET=your-admin-secret-key-change-in-production
DATABASE_URL=sqlite:///sop_db.sqlite
# For PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/sop_db
FLASK_ENV=development
```

### 2. Reset Database (First Time Setup)

Since we added a new `role` column to the User table and made changes to QnALog, you need to reset:

```bash
# For SQLite (development)
cd backend
rm instance/sop_db.sqlite

# The database will be recreated automatically when you run the app
python app.py
```

### 3. Create Admin User

#### Option A: Via API (Recommended)
```bash
curl -X POST http://localhost:5000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@company.com",
    "password": "SecureAdminPassword123!",
    "admin_secret": "your-admin-secret-key-change-in-production"
  }'
```

#### Option B: Via Frontend UI
1. Start the frontend and backend
2. Click "Switch to sign up"
3. Enter email and password
4. In the admin secret field, enter: `your-admin-secret-key-change-in-production`
5. Click "Sign up"

### 4. Create Regular Users

#### Via API:
```bash
curl -X POST http://localhost:5000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@company.com",
    "password": "UserPassword123!",
    "admin_secret": ""  # Leave empty or omit for regular user
  }'
```

#### Via Frontend UI:
1. Click "Switch to sign up"
2. Enter email and password
3. Leave the admin secret field blank
4. Click "Sign up"

## Architecture Overview

### Role System
```
User (role: 'admin' or 'user')
├── Can Create SOPs         ✓ (admin only)
├── Can View All SOPs       ✓ (both)
├── Can Ask Questions       ✓ (both)
├── Can Delete Own SOPs     ✓ (admin only)
└── Can View Q&A History    ✓ (both)
```

### Database Schema Changes

#### User Table
```sql
- id (Primary Key)
- email (Unique)
- password_hash
- role (NEW) - 'admin' or 'user', default 'user'
- created_at (implicit)
```

#### QnALog Table
```sql
- id (Primary Key)
- question
- answer
- sources
- created_at (NEW) - timestamp
- user_id (Foreign Key) - now NOT NULL
- sop_id (Foreign Key) - now NOT NULL
```

## Complete API Reference

### Authentication Endpoints

#### Signup
```http
POST /auth/signup
Content-Type: application/json

{
  "email": "user@company.com",
  "password": "password123",
  "admin_secret": "admin-secret-key"  // optional - include to create admin
}

Response:
{
  "msg": "User created",
  "role": "admin",  // or "user"
  "email": "user@company.com"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@company.com",
  "password": "password123"
}

Response:
{
  "access_token": "eyJhbGc...",
  "user_id": 1,
  "email": "user@company.com",
  "role": "admin"
}
```

#### Get Current User
```http
GET /auth/me
Authorization: Bearer <access_token>

Response:
{
  "user_id": 1,
  "email": "user@company.com",
  "role": "admin",
  "is_admin": true
}
```

### SOP Endpoints

#### Create SOP (Admin Only)
```http
POST /sops/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "title": "Employee Onboarding Process",
  "content": "Step 1: HR verifies documents...",
  "department_name": "HR"
}

Response (201):
{
  "msg": "SOP created",
  "id": 1,
  "title": "Employee Onboarding Process"
}

Response (403 - If not admin):
{
  "msg": "Only admins can create SOPs"
}
```

#### List All SOPs
```http
GET /sops/
Authorization: Bearer <token>

Response:
[
  {
    "id": 1,
    "title": "Employee Onboarding Process",
    "content": "Step 1: HR verifies...",
    "department_name": "HR",
    "owner_email": "admin@company.com",
    "owner_id": 1,
    "is_owner": false
  },
  ...
]
```

#### Get My SOPs (Admin Only)
```http
GET /sops/my-sops
Authorization: Bearer <admin_token>

Response:
[
  {
    "id": 1,
    "title": "Employee Onboarding Process",
    "content": "...",
    "department_name": "HR"
  },
  ...
]
```

#### Get Single SOP
```http
GET /sops/<id>
Authorization: Bearer <token>

Response:
{
  "id": 1,
  "title": "Employee Onboarding Process",
  "content": "...",
  "department_name": "HR",
  "owner_email": "admin@company.com"
}
```

#### Delete SOP (Admin, Owner Only)
```http
DELETE /sops/<id>
Authorization: Bearer <admin_token>

Response (200):
{
  "msg": "SOP deleted"
}

Response (403 - If not owner or not admin):
{
  "msg": "Only the admin who created this SOP can delete it"
}
```

### Question Endpoints

#### Ask Question (All Users)
```http
POST /questions/
Authorization: Bearer <token>
Content-Type: application/json

{
  "sop_id": 1,
  "question": "What are the steps for employee onboarding?"
}

Response:
{
  "answer": "The onboarding process involves...",
  "sources": "Step 1: HR verifies documents...",
  "sop_title": "Employee Onboarding Process",
  "sop_owner": "admin@company.com"
}
```

#### Get Question History
```http
GET /questions/history
Authorization: Bearer <token>

Response:
[
  {
    "id": 1,
    "question": "What are the steps for employee onboarding?",
    "answer": "The onboarding process involves...",
    "sources": "Step 1: HR verifies...",
    "sop_title": "Employee Onboarding Process",
    "created_at": "2025-12-15T10:30:00"
  },
  ...
]
```

#### Get Single Question
```http
GET /questions/<id>
Authorization: Bearer <token>

Response:
{
  "id": 1,
  "question": "What are the steps for employee onboarding?",
  "answer": "The onboarding process involves...",
  "sources": "...",
  "sop_title": "Employee Onboarding Process",
  "created_at": "2025-12-15T10:30:00"
}
```

### Answer Endpoints

#### Get All Answers
```http
GET /answers/
Authorization: Bearer <token>

Response: (Same as /questions/history)
[
  {
    "id": 1,
    "question": "...",
    "answer": "...",
    "sources": "...",
    "sop_title": "...",
    "sop_id": 1,
    "created_at": "..."
  },
  ...
]
```

#### Get Single Answer
```http
GET /answers/<id>
Authorization: Bearer <token>

Response:
{
  "id": 1,
  "question": "...",
  "answer": "...",
  "sources": "...",
  "sop_title": "...",
  "created_at": "..."
}
```

## Frontend Components Changes

### Dashboard.js
- ✅ Fetches current user role on load
- ✅ Shows SOPForm only for admins
- ✅ Displays owner information for each SOP
- ✅ Shows delete button only for admin owners
- ✅ Updated user greeting based on role
- ✅ Added Q&A timestamp display
- ✅ Handles role-specific messaging

### Login.js
- ✅ Added admin_secret field in signup mode
- ✅ Shows role-specific messages
- ✅ Displays role upon successful login
- ✅ Improved error and success styling

### SOPForm.js
- ✅ Better error handling
- ✅ Shows loading state while creating
- ✅ Title indicates admin-only access
- ✅ Improved validation feedback

### AskAI.js
- ✅ Loading state during API call
- ✅ Enter key support for quick submission
- ✅ Better message styling
- ✅ Shows SOP owner information

## Testing Checklist

### Admin User Testing
- [ ] Can sign up with admin_secret
- [ ] Can create SOPs
- [ ] Can view all SOPs
- [ ] Can see "Delete" button on own SOPs
- [ ] Can delete own SOPs
- [ ] Cannot delete SOPs created by others
- [ ] Can ask questions on any SOP
- [ ] Can view Q&A history
- [ ] Dashboard shows admin-specific UI

### Regular User Testing
- [ ] Can sign up without admin_secret
- [ ] Cannot see "Create SOP" form
- [ ] Can view all available SOPs
- [ ] Can ask questions on any SOP
- [ ] Can view own Q&A history
- [ ] Cannot access `/sops/` POST endpoint
- [ ] Cannot delete SOPs
- [ ] Dashboard shows user-specific UI

### Error Handling Testing
- [ ] Non-admin cannot create SOP (403)
- [ ] User cannot view other's Q&A history
- [ ] User cannot delete Q&A history of others
- [ ] Invalid credentials return 401
- [ ] Missing SOP returns 404
- [ ] Missing question/answer returns proper error

## Production Deployment Checklist

- [ ] Change `ADMIN_SECRET` environment variable
- [ ] Change `JWT_SECRET_KEY` environment variable
- [ ] Set `FLASK_ENV=production`
- [ ] Configure PostgreSQL database
- [ ] Set up HTTPS
- [ ] Configure CORS properly for your domain
- [ ] Set up database backups
- [ ] Configure logging
- [ ] Set up monitoring/alerts

## Troubleshooting

### "Only admins can create SOPs" Error
**Solution**: Make sure you're logged in as a user with admin role. Check `role` field in login response.

### Database Migration Issues
**Solution**: 
```bash
# Delete old database
rm instance/sop_db.sqlite
# App will create new schema on next run
python app.py
```

### Token Expired
**Solution**: Re-login to get a new token. Frontend should handle this gracefully.

### CORS Issues
**Solution**: Check `CORS(app, resources={r'/*': {'origins': '*'}})` in app.py. Adjust origins for production.

## File Changes Summary

| File | Changes |
|------|---------|
| `backend/models.py` | Added `role` field to User, `created_at` to QnALog, `is_admin()` method |
| `backend/routes/auth.py` | Enhanced signup/login, added GET /auth/me |
| `backend/routes/sops.py` | Added admin check, list all SOPs, my SOPs endpoint, delete endpoint |
| `backend/routes/questions.py` | Allow any user to ask questions on any SOP |
| `backend/routes/answers.py` | Enhanced with timestamps and error handling |
| `frontend/src/components/Dashboard.js` | Role-based UI, admin-only SOP form, delete buttons |
| `frontend/src/components/Login.js` | Added admin_secret field, role feedback |
| `frontend/src/components/SOPForm.js` | Better validation and loading states |
| `frontend/src/components/AskAI.js` | Better UX, loading states, Enter key support |

## Security Notes

1. **Admin Secret**: Store in environment variables, not in code
2. **JWT Secret**: Generate a strong random key, change it regularly
3. **Password Hashing**: Already handled by Werkzeug
4. **HTTPS**: Use in production only
5. **CORS**: Restrict to your domain in production
6. **Rate Limiting**: Consider adding for auth endpoints
7. **Audit Logging**: Consider adding for admin actions

## Next Steps (Future Enhancements)

- [ ] Add password reset functionality
- [ ] Add email verification
- [ ] Add audit logs for SOP creation/deletion
- [ ] Add bulk SOP import
- [ ] Add SOP versioning
- [ ] Add user management dashboard for admins
- [ ] Add analytics/usage tracking
- [ ] Add SOP approval workflow
- [ ] Add collaborative SOP editing
- [ ] Add SOP search/tagging

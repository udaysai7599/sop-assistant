# Role-Based Access Control Implementation

## Overview
The SOP Assistant has been updated with a role-based authorization system that enforces the following access control:

- **Admins**: Can create, view, edit, and delete SOPs
- **Users**: Can view all SOPs and ask questions about them, but cannot create SOPs

## Changes Made

### 1. Database Models (`backend/models.py`)
- **User Model**: Added `role` field (default: 'user', values: 'admin' or 'user')
  - Added `is_admin()` method for role checking
  - Added relationship to `qna_logs` for better ORM structure
- **QnALog Model**: 
  - Added `created_at` timestamp field (auto-populated)
  - Made `user_id` non-nullable
  - Made `sop_id` non-nullable

### 2. Authentication Routes (`backend/routes/auth.py`)
- **Enhanced Signup** (`POST /auth/signup`):
  - Accepts optional `admin_secret` parameter
  - If `admin_secret` matches `ADMIN_SECRET` env variable, user is created as admin
  - Returns `role` in response
  
- **Enhanced Login** (`POST /auth/login`):
  - Returns user `role` and `user_id` in response
  - Returns full JWT token for subsequent requests

- **New Endpoint - Get Current User** (`GET /auth/me`):
  - Returns current authenticated user's details including role
  - Useful for frontend to determine UI features

### 3. SOP Management Routes (`backend/routes/sops.py`)
- **Create SOP** (`POST /sops/`):
  - ✅ NOW REQUIRES ADMIN ROLE
  - Returns 403 error if user is not admin

- **List All SOPs** (`GET /sops/`):
  - Now returns ALL SOPs in the system (not just user's own)
  - Shows owner information for each SOP
  - Both admins and users can access
  - Response includes: `owner_email`, `owner_id`, `is_owner` flag

- **New Endpoint - Get My SOPs** (`GET /sops/my-sops`):
  - Returns only SOPs created by the current admin user
  - Requires admin role

- **Get Single SOP** (`GET /sops/<id>`):
  - Any authenticated user can view any SOP
  - New endpoint for fetching individual SOP details

- **Delete SOP** (`DELETE /sops/<id>`):
  - Only the admin who created it can delete it
  - Returns 403 if user is not the owner or not admin

### 4. Questions Routes (`backend/routes/questions.py`)
- **Ask Question** (`POST /questions/`):
  - Now any authenticated user can ask questions on ANY SOP
  - Previously restricted to asking on own SOPs
  - Answer retrieved via RAG on SOP content
  - Returns SOP owner information

- **New Endpoint - Question History** (`GET /questions/history`):
  - Returns all questions asked by current user
  - Sorted by most recent first
  - Includes creation timestamp

- **New Endpoint - Get Single Question** (`GET /questions/<id>`):
  - Returns specific question details
  - Only accessible to the user who asked it

### 5. Answers Routes (`backend/routes/answers.py`)
- Enhanced with proper error handling and timestamp support
- Now includes `created_at` in responses
- Added individual answer retrieval endpoint

## How to Set Up

### 1. Update Database (First Time)
Since the `User` model now has a `role` column, you need to reset the database:

```bash
# Delete old database (if using SQLite)
rm backend/instance/sop_db.sqlite

# Or if using PostgreSQL, run migrations or recreate the database
```

### 2. Create Admin User
```bash
# Method 1: Via API with admin_secret
curl -X POST http://localhost:5000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@company.com",
    "password": "admin_password",
    "admin_secret": "admin-secret-key-change-me"
  }'

# Method 2: Update ADMIN_SECRET environment variable
export ADMIN_SECRET="your-secure-admin-secret"
```

### 3. Create Regular User
```bash
curl -X POST http://localhost:5000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@company.com",
    "password": "user_password"
  }'
```

### 4. Login
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@company.com",
    "password": "admin_password"
  }'

# Response includes:
# {
#   "access_token": "...",
#   "user_id": 1,
#   "email": "admin@company.com",
#   "role": "admin"
# }
```

## API Endpoints Summary

### Authentication
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/signup` | ❌ | Sign up new user (with optional admin_secret) |
| POST | `/auth/login` | ❌ | Login user, get JWT token |
| GET | `/auth/me` | ✅ | Get current user info |

### SOPs (Admin-Only Creation)
| Method | Endpoint | Auth | Role Required | Description |
|--------|----------|------|---------------|-------------|
| POST | `/sops/` | ✅ | Admin | Create new SOP |
| GET | `/sops/` | ✅ | Any | List all available SOPs |
| GET | `/sops/my-sops` | ✅ | Admin | List only my created SOPs |
| GET | `/sops/<id>` | ✅ | Any | Get single SOP |
| DELETE | `/sops/<id>` | ✅ | Admin (Owner) | Delete SOP |

### Questions & Answers (All Users)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/questions/` | ✅ | Ask question on any SOP |
| GET | `/questions/history` | ✅ | Get my question history |
| GET | `/questions/<id>` | ✅ | Get specific question (owner only) |
| GET | `/answers/` | ✅ | Get my answers (alias for history) |
| GET | `/answers/<id>` | ✅ | Get specific answer (owner only) |

## Frontend Updates Required

### For Admin Users
1. Show "Create SOP" form only if `role === 'admin'`
2. Add ability to view all SOPs and their owners
3. Allow deleting own SOPs
4. Show admin-specific dashboard

### For Regular Users
1. Display "Available SOPs" list (read-only)
2. Allow asking questions on any SOP
3. Show Q&A history
4. Hide SOP creation form

### Example: Check User Role Before Rendering
```javascript
// In frontend component
const [user, setUser] = useState(null);

// After login, fetch user info
const response = await axios.get('/auth/me', {
  headers: { Authorization: `Bearer ${token}` }
});
setUser(response.data);

// In JSX
{user?.is_admin ? <SOPForm /> : <ViewSOPsOnly />}
```

## Environment Variables
```bash
# Backend configuration
export JWT_SECRET_KEY="your-jwt-secret-key"
export ADMIN_SECRET="your-admin-secret-for-signup"
export DATABASE_URL="postgresql://user:pass@localhost/sop_db"  # Optional, defaults to SQLite
```

## Security Considerations

1. **Admin Secret**: Change the default `ADMIN_SECRET` immediately in production
   - Set via environment variable: `export ADMIN_SECRET="your-secure-key"`
   - Or hardcode in production deployment

2. **JWT Secret**: Change default `JWT_SECRET_KEY` 
   - Set via environment variable

3. **Role Validation**: All admin-only endpoints check user role before processing

4. **Ownership Verification**: Delete operations verify user ownership

## Testing the Flow

### As Admin:
1. Sign up with `admin_secret` → Role = 'admin'
2. Create SOPs (success)
3. View all SOPs
4. Delete own SOPs (success)
5. Ask questions on any SOP
6. View Q&A history

### As User:
1. Sign up without `admin_secret` → Role = 'user'
2. Try to create SOP → 403 Forbidden ✓
3. View all available SOPs (success)
4. Ask questions on any SOP (success)
5. View Q&A history (success)

## Migration from Old System
If you have existing SOPs:
1. All existing SOPs need an `owner_id` (admin user ID)
2. Run a SQL script to assign SOPs to admin users
3. Or delete database and start fresh with new role-based setup

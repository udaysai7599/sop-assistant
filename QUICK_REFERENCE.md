# Quick Reference Guide

## For Admins

### Setup
```bash
# 1. Set environment variable (or in .env)
export ADMIN_SECRET="your-secure-secret-key"

# 2. Start backend
cd backend
python app.py

# 3. Create admin account
curl -X POST http://localhost:5000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@company.com",
    "password": "password",
    "admin_secret": "your-secure-secret-key"
  }'

# 4. Login
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@company.com",
    "password": "password"
  }'
# Copy the access_token from response
```

### Key Operations
```bash
# Create a new SOP
curl -X POST http://localhost:5000/sops/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "IT Security Guidelines",
    "content": "All employees must...",
    "department_name": "IT"
  }'

# List all SOPs you created
curl -X GET http://localhost:5000/sops/my-sops \
  -H "Authorization: Bearer {token}"

# Delete a SOP
curl -X DELETE http://localhost:5000/sops/{sop_id} \
  -H "Authorization: Bearer {token}"
```

---

## For Regular Users

### Setup
```bash
# 1. Start frontend and backend

# 2. Sign up (without admin_secret)
curl -X POST http://localhost:5000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@company.com",
    "password": "password"
  }'

# 3. Login
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@company.com",
    "password": "password"
  }'
```

### Key Operations
```bash
# List all available SOPs
curl -X GET http://localhost:5000/sops/ \
  -H "Authorization: Bearer {token}"

# Ask a question
curl -X POST http://localhost:5000/questions/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "sop_id": 1,
    "question": "What is the IT security policy?"
  }'

# View your Q&A history
curl -X GET http://localhost:5000/questions/history \
  -H "Authorization: Bearer {token}"
```

---

## Environment Variables

### Backend (.env file or export)
```bash
# Security
JWT_SECRET_KEY=your-random-secret-key-here
ADMIN_SECRET=your-admin-secret-key-here

# Database
DATABASE_URL=sqlite:///sop_db.sqlite
# Or for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/sop_db

# Flask
FLASK_ENV=development
FLASK_DEBUG=1
```

### Frontend (.env file)
```bash
# If backend is on different host/port
REACT_APP_API_URL=http://localhost:5000
```

---

## Common Errors and Solutions

### "Only admins can create SOPs" (403)
**Problem**: You're not logged in as an admin  
**Solution**: 
1. Check your login response includes `"role": "admin"`
2. Re-login as admin user
3. Ensure you used `admin_secret` during signup

### "SOP not found" (404)
**Problem**: SOP ID doesn't exist or was deleted  
**Solution**: 
1. Get list of SOPs: `GET /sops/`
2. Use correct SOP ID

### "Invalid credentials" (401)
**Problem**: Email or password is wrong  
**Solution**: 
1. Make sure email is correct
2. Re-check password
3. Create new account if needed

### "You can only view your own questions" (403)
**Problem**: Trying to access another user's Q&A  
**Solution**: Only use your own question IDs

### Database errors on startup
**Problem**: New schema columns don't match  
**Solution**: 
```bash
# For SQLite
rm backend/instance/sop_db.sqlite

# For PostgreSQL
# Drop and recreate database
```

---

## Role Comparison

| Feature | Admin | User |
|---------|-------|------|
| Create SOP | ✅ Yes | ❌ No |
| View all SOPs | ✅ Yes | ✅ Yes |
| Edit SOP | ❌ No | ❌ No |
| Delete own SOP | ✅ Yes | ❌ No |
| Ask questions | ✅ Yes | ✅ Yes |
| View own Q&A | ✅ Yes | ✅ Yes |
| View others' Q&A | ❌ No | ❌ No |

---

## API Response Examples

### Successful Login
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": 1,
  "email": "admin@company.com",
  "role": "admin"
}
```

### List SOPs
```json
[
  {
    "id": 1,
    "title": "Employee Onboarding",
    "content": "Step 1: Verify documents...",
    "department_name": "HR",
    "owner_email": "admin@company.com",
    "owner_id": 1,
    "is_owner": true
  }
]
```

### Ask Question Response
```json
{
  "answer": "Employee onboarding involves verification of documents, orientation, and training.",
  "sources": "Step 1: Verify documents",
  "sop_title": "Employee Onboarding",
  "sop_owner": "admin@company.com"
}
```

### Q&A History
```json
[
  {
    "id": 1,
    "question": "What is employee onboarding?",
    "answer": "Employee onboarding involves...",
    "sources": "Step 1: Verify documents",
    "sop_title": "Employee Onboarding",
    "created_at": "2025-12-15T10:30:00"
  }
]
```

---

## Admin Setup Checklist

1. [ ] Set ADMIN_SECRET environment variable
2. [ ] Start backend (`python app.py`)
3. [ ] Create admin user with admin_secret
4. [ ] Test admin login (should return role="admin")
5. [ ] Create first SOP
6. [ ] Verify SOP appears in `/sops/` list
7. [ ] Create a regular user account
8. [ ] Test user login (should return role="user")
9. [ ] Verify user can see all SOPs
10. [ ] Test user asking a question on SOP
11. [ ] Verify user cannot create SOP (should get 403)

---

## Troubleshooting Commands

```bash
# Check current user info
curl -X GET http://localhost:5000/auth/me \
  -H "Authorization: Bearer {token}"

# Get all SOPs with details
curl -X GET http://localhost:5000/sops/ \
  -H "Authorization: Bearer {token}" | jq '.'

# Get single SOP
curl -X GET http://localhost:5000/sops/1 \
  -H "Authorization: Bearer {token}" | jq '.'

# Check Q&A history
curl -X GET http://localhost:5000/answers/ \
  -H "Authorization: Bearer {token}" | jq '.'

# Get backend health
curl http://localhost:5000/ -v
```

---

## Support

For issues, check:
1. Backend logs for API errors
2. Frontend console (F12) for client errors
3. Database connection
4. Environment variables set correctly
5. Tokens not expired (re-login if needed)

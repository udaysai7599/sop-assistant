# Frontend Testing Guide - Run Manually

## Backend Status ✓
- Backend is running on http://localhost:5000
- All 15 API tests PASSED
- Database is operational
- Ready for frontend testing

---

## How to Start Frontend (Run in Your Own Terminal)

### Option 1: PowerShell (Administrator)
```powershell
# Run PowerShell as Administrator, then:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
cd C:\uday\sop-assistant\frontend
npm install
npm start
```

### Option 2: Command Prompt (cmd.exe)
```cmd
cd C:\uday\sop-assistant\frontend
npm install
npm start
```

### Option 3: Git Bash
```bash
cd /c/uday/sop-assistant/frontend
npm install
npm start
```

---

## Frontend will open at: http://localhost:3000

---

## Test Scenarios Once Frontend Loads

### Test 1: Admin Workflow

**Step 1: Create Admin Account**
1. Click "Switch to sign up"
2. Fill in:
   - Email: `admin@company.com`
   - Password: `admin123`
   - Admin Secret: `admin-secret-key-change-me`
3. Click "Sign up"
4. You should see: ✓ "Account created as Admin. Now logging in..."

**Step 2: Dashboard Loads (Admin View)**
- [ ] Title: "SOP Assistant Dashboard"
- [ ] Shows: "You are an Admin..."
- [ ] "Logged in as: admin@company.com (admin)"
- [ ] "Create new SOP" form IS visible
- [ ] Empty "All SOPs" section

**Step 3: Create SOP**
1. Fill SOP form:
   - Title: `Employee Handbook`
   - Department: `HR`
   - Content: `Welcome to our company! 
     Section 1: Work Hours - 9AM to 5PM daily
     Section 2: Dress Code - Business casual required
     Section 3: Code of Conduct - Professional behavior at all times
     Section 4: Benefits - Health insurance included`
2. Click "Save SOP"
3. You should see: ✓ "✓ SOP created successfully"
4. SOP appears in "All SOPs" section:
   - [ ] Title shows: "Employee Handbook"
   - [ ] Department shows: "HR"
   - [ ] Owner shows: "admin@company.com"
   - [ ] You see "Delete" button
   - [ ] Question input box appears

**Step 4: Ask Question (as Admin)**
1. In the question box, type: `What are the work hours?`
2. Click "Ask" or press Enter
3. You should see: ✓ "✓ Answer saved to your history"
4. Answer appears below: "...9AM to 5PM..."
5. Answer appears in "Your Q&A History" section

---

### Test 2: User Workflow

**Step 1: Logout and Create User Account**
1. Click "Logout" button
2. Browser returns to login page
3. Click "Switch to sign up"
4. Fill in:
   - Email: `user@company.com`
   - Password: `user123`
   - **Leave Admin Secret BLANK**
5. Click "Sign up"
6. You should see: ✓ "Account created as User. Now logging in..."

**Step 2: Dashboard Loads (User View)**
- [ ] Title: "SOP Assistant Dashboard"
- [ ] Shows: "Ask questions against available SOPs..."
- [ ] "Logged in as: user@company.com (user)"
- [ ] "Create new SOP" form is **NOT visible** (hidden for users)
- [ ] "Available SOPs" shows the SOP created by admin:
  - [ ] Title: "Employee Handbook"
  - [ ] Owner: "admin@company.com"
  - [ ] **No Delete button** (users can't delete)

**Step 3: Ask Question (as User)**
1. In the question box for the SOP, type: `What is the dress code?`
2. Click "Ask" or press Enter
3. You should see: ✓ "✓ Answer saved to your history"
4. Answer appears: "...Business casual..."
5. Answer appears in "Your Q&A History"

**Step 4: Ask Another Question**
1. Type: `What time do we start work?`
2. Click "Ask"
3. Answer appears: "...9AM..."
4. Your Q&A History now shows 2 questions
5. Dates are displayed for each Q&A entry

---

### Test 3: Permission Tests

**Test 3a: User Cannot Create SOP**
1. Logged in as user (user@company.com)
2. Try to navigate to SOP creation (it's hidden, but if you try via console)
3. Should see error: ✗ "Only admins can create SOPs"

**Test 3b: User Cannot Delete SOP**
1. Logged in as user
2. Looking at "Available SOPs"
3. Should **NOT see** a Delete button on the SOP
4. Only admin owner sees Delete button

---

### Test 4: Cross-User Data Privacy

**Test 4a: Users Cannot See Other's Q&A**
1. Logout from user account
2. Login as admin (admin@company.com)
3. Go to "Your Q&A History"
4. Should see **only 1 question** (your own "What are the work hours?")
5. Should **NOT see** user's questions

**Test 4b: User Cannot See Admin's Q&A**
1. Logout from admin account
2. Login as user (user@company.com)
3. Go to "Your Q&A History"
4. Should see **2 questions** (your own "What is the dress code?" and "What time...")
5. Should **NOT see** admin's question

---

### Test 5: Admin Delete Functionality

**Test 5a: Admin Can Delete SOP**
1. Login as admin (admin@company.com)
2. In "All SOPs" section, find the SOP
3. Click "Delete" button
4. Confirm deletion
5. SOP disappears from list
6. You should see: ✓ "✓ SOP deleted"

**Test 5b: Verify SOP is Deleted**
1. Still logged in as admin
2. Should see empty "All SOPs" section
3. Logout and login as user
4. User also sees empty "Available SOPs" section

---

### Test 6: Multiple SOPs

**Optional: Test with Multiple SOPs**
1. Login as admin
2. Create multiple SOPs:
   - "IT Security Guidelines"
   - "Finance Procedures"
   - "Marketing Guidelines"
3. Login as user
4. Should see all 3 SOPs
5. Ask questions on different SOPs
6. Each SOP tracks questions separately
7. Q&A History shows all questions across all SOPs

---

## Expected UI Elements

### Admin Dashboard Should Show:
```
┌─ SOP Assistant Dashboard ──────────────────┐
│ "You are an Admin. Create and manage SOPs" │
│ Logged in as: admin@company.com (admin)    │
│ [Logout]                                   │
├────────────────────────────────────────────┤
│ 📝 Create New SOP (Admin Only)             │
│ [SOP Title Input]                          │
│ [Department Input]                         │
│ [Content TextArea]                         │
│ [Save SOP]                                 │
├────────────────────────────────────────────┤
│ All SOPs                                   │
│ ┌─ Employee Handbook (HR) ─────────────┐  │
│ │ Owner: admin@company.com             │  │
│ │ [Ask About SOP Input] [Ask]          │  │
│ │ [Delete]                             │  │
│ └──────────────────────────────────────┘  │
├────────────────────────────────────────────┤
│ Your Q&A History                           │
│ Q: "What are the work hours?"              │
│ A: "...9AM to 5PM..."                      │
│ Source: "Work Hours - 9AM to 5PM daily"    │
└────────────────────────────────────────────┘
```

### User Dashboard Should Show:
```
┌─ SOP Assistant Dashboard ──────────────────┐
│ "Ask questions against available SOPs..."  │
│ Logged in as: user@company.com (user)      │
│ [Logout]                                   │
├────────────────────────────────────────────┤
│ Available SOPs                             │
│ ┌─ Employee Handbook (HR) ─────────────┐  │
│ │ Owner: admin@company.com             │  │
│ │ [Ask About SOP Input] [Ask]          │  │
│ └──────────────────────────────────────┘  │
├────────────────────────────────────────────┤
│ Your Q&A History                           │
│ Q: "What is the dress code?"               │
│ A: "...Business casual..."                 │
│ Q: "What time do we start work?"           │
│ A: "...9AM..."                             │
└────────────────────────────────────────────┘
```

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Cannot connect to server" | Backend not running - check terminal 1 |
| "Only admins can create SOPs" | You're logged in as user, not admin |
| SOP not appearing | Refresh page or check backend is running |
| Answers showing wrong content | Check SOP content in database |
| Role shows as "user" for admin | Try logging out and back in |
| Cannot see Delete button | You're not the SOP owner |

---

## Test Checklist

### Admin Functionality
- [ ] Can sign up as admin with admin_secret
- [ ] Can see "Create New SOP" form
- [ ] Can create SOP successfully
- [ ] Can see all SOPs in dashboard
- [ ] Can see Delete button on own SOPs
- [ ] Can ask questions
- [ ] Can see own Q&A history
- [ ] Cannot see other user's Q&A

### User Functionality
- [ ] Can sign up without admin_secret
- [ ] Cannot see "Create New SOP" form
- [ ] Can see all available SOPs
- [ ] Cannot see Delete button
- [ ] Can ask questions on any SOP
- [ ] Can see own Q&A history
- [ ] Cannot see admin's Q&A history

### Security
- [ ] User cannot create SOP (gets 403 error)
- [ ] User cannot delete SOP
- [ ] User cannot access other user's Q&A
- [ ] Admin can only delete own SOPs
- [ ] Timestamps are recorded

### Integration
- [ ] Backend and Frontend communicate correctly
- [ ] Answers are generated via RAG
- [ ] Q&A stored in database
- [ ] Role-based UI works correctly
- [ ] Authorization enforced on all operations

---

## Once Frontend Loads Successfully

You should see:
1. Login page with email/password fields
2. "Switch to sign up" button
3. Beautiful UI with sections for SOPs and Q&A history
4. Role-specific features based on user type

**Status**: Backend 100% Ready ✓
**Next**: Start frontend manually and test scenarios above

All backend API endpoints verified and working!

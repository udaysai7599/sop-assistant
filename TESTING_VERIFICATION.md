# Testing Verification Checklist

## Pre-Deployment Verification

### 1. Database Setup
- [ ] Delete old SQLite database or backup existing one
- [ ] Confirm new schema has `role` column in user table
- [ ] Confirm QnALog has `created_at` column

```bash
# Verify schema (SQLite)
sqlite3 backend/instance/sop_db.sqlite ".schema user"
sqlite3 backend/instance/sop_db.sqlite ".schema qna_log"
```

### 2. Backend API Testing

#### Authentication
- [ ] Signup as admin with admin_secret
  ```bash
  curl -X POST http://localhost:5000/auth/signup \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@test.com","password":"test123","admin_secret":"admin-secret-key-change-me"}'
  # Expected: 201, role=admin
  ```

- [ ] Signup as user without admin_secret
  ```bash
  curl -X POST http://localhost:5000/auth/signup \
    -H "Content-Type: application/json" \
    -d '{"email":"user@test.com","password":"test123"}'
  # Expected: 201, role=user
  ```

- [ ] Login as admin and verify role in response
  ```bash
  curl -X POST http://localhost:5000/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@test.com","password":"test123"}'
  # Expected: 200, includes role="admin"
  ```

- [ ] GET /auth/me returns user info with role
  ```bash
  curl -X GET http://localhost:5000/auth/me \
    -H "Authorization: Bearer {admin_token}"
  # Expected: 200, includes is_admin=true
  ```

#### SOP Management (Admin)
- [ ] Create SOP as admin (should succeed)
  ```bash
  curl -X POST http://localhost:5000/sops/ \
    -H "Authorization: Bearer {admin_token}" \
    -H "Content-Type: application/json" \
    -d '{"title":"Test SOP","content":"Test content","department_name":"IT"}'
  # Expected: 201, returns SOP id
  ```

- [ ] Create SOP as user (should fail)
  ```bash
  curl -X POST http://localhost:5000/sops/ \
    -H "Authorization: Bearer {user_token}" \
    -H "Content-Type: application/json" \
    -d '{"title":"Test","content":"Test"}'
  # Expected: 403, "Only admins can create SOPs"
  ```

#### SOP Management (View)
- [ ] GET /sops/ returns all SOPs for admin
  ```bash
  curl -X GET http://localhost:5000/sops/ \
    -H "Authorization: Bearer {admin_token}"
  # Expected: 200, returns list with owner info
  ```

- [ ] GET /sops/ returns all SOPs for user
  ```bash
  curl -X GET http://localhost:5000/sops/ \
    -H "Authorization: Bearer {user_token}"
  # Expected: 200, same list as admin
  ```

- [ ] GET /sops/my-sops returns only admin's SOPs
  ```bash
  curl -X GET http://localhost:5000/sops/my-sops \
    -H "Authorization: Bearer {admin_token}"
  # Expected: 200, returns only SOPs created by this admin
  ```

- [ ] GET /sops/my-sops fails for user
  ```bash
  curl -X GET http://localhost:5000/sops/my-sops \
    -H "Authorization: Bearer {user_token}"
  # Expected: 403
  ```

- [ ] GET /sops/<id> works for any user
  ```bash
  curl -X GET http://localhost:5000/sops/1 \
    -H "Authorization: Bearer {user_token}"
  # Expected: 200
  ```

#### SOP Deletion
- [ ] Admin can delete own SOP
  ```bash
  curl -X DELETE http://localhost:5000/sops/1 \
    -H "Authorization: Bearer {admin_token}"
  # Expected: 200, "SOP deleted"
  ```

- [ ] Admin cannot delete other admin's SOP
  ```bash
  # Create SOP with admin1, try to delete with admin2
  # Expected: 403
  ```

- [ ] User cannot delete any SOP
  ```bash
  curl -X DELETE http://localhost:5000/sops/1 \
    -H "Authorization: Bearer {user_token}"
  # Expected: 403
  ```

#### Questions
- [ ] User can ask question on any SOP
  ```bash
  curl -X POST http://localhost:5000/questions/ \
    -H "Authorization: Bearer {user_token}" \
    -H "Content-Type: application/json" \
    -d '{"sop_id":1,"question":"What is this SOP?"}'
  # Expected: 200, returns answer
  ```

- [ ] Admin can ask question on any SOP
  ```bash
  curl -X POST http://localhost:5000/questions/ \
    -H "Authorization: Bearer {admin_token}" \
    -H "Content-Type: application/json" \
    -d '{"sop_id":1,"question":"What is this SOP?"}'
  # Expected: 200, returns answer
  ```

- [ ] GET /questions/history returns user's questions
  ```bash
  curl -X GET http://localhost:5000/questions/history \
    -H "Authorization: Bearer {user_token}"
  # Expected: 200, list of questions asked by this user
  ```

- [ ] GET /questions/history includes created_at
  ```bash
  # Check response has created_at timestamp for each question
  ```

- [ ] User can only view own question
  ```bash
  curl -X GET http://localhost:5000/questions/1 \
    -H "Authorization: Bearer {other_user_token}"
  # Expected: 403
  ```

#### Answers
- [ ] GET /answers/ returns user's answers
  ```bash
  curl -X GET http://localhost:5000/answers/ \
    -H "Authorization: Bearer {user_token}"
  # Expected: 200, same as /questions/history
  ```

- [ ] GET /answers/<id> works for owner only
  ```bash
  curl -X GET http://localhost:5000/answers/1 \
    -H "Authorization: Bearer {user_token}"
  # Expected: 200 if user is owner, 403 otherwise
  ```

### 3. Frontend Verification

#### Dashboard Component
- [ ] Admin sees "Create SOP" form
  - [ ] Login as admin
  - [ ] Verify SOPForm is visible
  - [ ] Title says "Create New SOP (Admin Only)"

- [ ] User does NOT see "Create SOP" form
  - [ ] Login as user
  - [ ] Verify SOPForm is NOT visible

- [ ] Both see all SOPs
  - [ ] SOPs list shows owner information
  - [ ] Both admin and user see same SOP list

- [ ] Only admin sees delete button
  - [ ] Admin sees delete button on own SOPs
  - [ ] User does NOT see delete button
  - [ ] Admin does NOT see delete on other admin's SOPs

- [ ] Q&A history shows timestamps
  - [ ] Each answer shows created_at date/time

#### Login Component
- [ ] Signup form shows admin_secret field
  - [ ] Click "Switch to sign up"
  - [ ] Verify admin_secret input appears

- [ ] Role is displayed after login
  - [ ] Login response shows role
  - [ ] Message indicates "signed in as Admin" or "signed in as User"

#### SOPForm Component
- [ ] Loading state works
  - [ ] Button shows "Creating..." while submitting
  - [ ] Form is disabled during submission

- [ ] Success message shows
  - [ ] After creation, shows "✓ SOP created successfully"

- [ ] Error message shows for non-admin
  - [ ] Non-admin sees "✗ Only admins can create SOPs"

#### AskAI Component
- [ ] Loading state works
  - [ ] Button shows "Thinking..." while processing

- [ ] Enter key submits question
  - [ ] Press Enter in question input → submits

- [ ] Success message shows
  - [ ] After answer, shows "✓ Answer saved to your history"

### 4. Integration Testing

#### Complete Admin Flow
1. [ ] Create new admin account with admin_secret
2. [ ] Login as admin
3. [ ] Create multiple SOPs in different departments
4. [ ] List SOPs and verify they appear
5. [ ] Ask a question on one SOP
6. [ ] View answer in history
7. [ ] Delete the SOP
8. [ ] Verify SOP no longer appears

#### Complete User Flow
1. [ ] Create new user account without admin_secret
2. [ ] Login as user
3. [ ] Try to create SOP (should fail) - verify error message
4. [ ] View list of SOPs created by admin
5. [ ] Ask questions on multiple SOPs
6. [ ] View Q&A history
7. [ ] Verify user cannot delete any SOP
8. [ ] Verify user cannot view other users' Q&A

#### Cross-User Scenario
1. [ ] Create Admin1 and Admin2
2. [ ] Admin1 creates SOP1
3. [ ] Admin2 creates SOP2
4. [ ] Create User1
5. [ ] User1 asks questions on both SOP1 and SOP2
6. [ ] Admin1 can delete SOP1 but not SOP2
7. [ ] Admin2 can delete SOP2 but not SOP1
8. [ ] Admin1 can see SOP2 in list but cannot delete
9. [ ] User1 sees both SOPs and can ask questions on both

### 5. Error Scenarios

- [ ] Missing required fields return 400
  ```bash
  curl -X POST http://localhost:5000/sops/ \
    -H "Authorization: Bearer {token}" \
    -H "Content-Type: application/json" \
    -d '{"title":"","content":""}'
  # Expected: 400, "Title and content are required"
  ```

- [ ] Non-existent resource returns 404
  ```bash
  curl -X GET http://localhost:5000/sops/9999 \
    -H "Authorization: Bearer {token}"
  # Expected: 404, "SOP not found"
  ```

- [ ] Invalid token returns 401
  ```bash
  curl -X GET http://localhost:5000/sops/ \
    -H "Authorization: Bearer invalid-token"
  # Expected: 401, "Unauthorized"
  ```

- [ ] Missing authorization header returns 401
  ```bash
  curl -X GET http://localhost:5000/sops/
  # Expected: 401
  ```

### 6. Performance Verification

- [ ] List SOPs with 100+ SOPs loads in reasonable time
- [ ] Q&A history is paginated if many entries
- [ ] No N+1 query issues when listing SOPs with owner info

### 7. Security Verification

- [ ] Admin secret not logged in plain text
  - [ ] Check backend logs don't contain admin_secret
  
- [ ] Passwords are hashed
  - [ ] Check database: password_hash in user table
  
- [ ] JWT token validation works
  - [ ] Expired tokens are rejected
  - [ ] Invalid tokens are rejected
  
- [ ] Role is enforced on all protected endpoints
  - [ ] Each admin-only endpoint properly checks role

### 8. Browser Console Check

- [ ] No JavaScript errors on Dashboard
- [ ] No warnings about missing props
- [ ] Network tab shows all requests succeeding (or expected failures)

---

## Rollback Plan (if issues occur)

1. Restore database from backup
2. Revert code changes from git
3. Restart backend and frontend
4. Test with previous version

---

## Sign-Off Checklist

- [ ] All API endpoints tested and working
- [ ] Frontend displays correctly for both roles
- [ ] Admin can create SOPs
- [ ] User cannot create SOPs
- [ ] All users can ask questions
- [ ] All users can view their own Q&A history
- [ ] No security vulnerabilities identified
- [ ] Documentation is clear and complete
- [ ] Performance is acceptable
- [ ] Error handling is appropriate
- [ ] Ready for production deployment

---

## Common Issues and Solutions

### Issue: "Only admins can create SOPs" for admin user
**Solution**: Check that user has role='admin' in database

### Issue: Users don't see SOPs created by admins
**Solution**: Check that GET /sops/ returns all SOPs (query should not filter by owner_id)

### Issue: Admin can delete other admin's SOPs
**Solution**: Check DELETE endpoint verifies sop.owner_id == user_id

### Issue: User can see other user's Q&A history
**Solution**: Check question/answer retrieval verifies log.user_id == current_user_id

### Issue: Frontend not showing role correctly
**Solution**: Check that Dashboard fetches /auth/me and stores user.role

### Issue: Admin secret not working
**Solution**: 
1. Verify ADMIN_SECRET environment variable is set
2. Check it matches what you're sending in signup
3. Verify signup endpoint is checking admin_secret correctly

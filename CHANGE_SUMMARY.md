# Change Summary: Role-Based Access Control

## What Changed and Why

### The Requirement
**Before**: Any logged-in user could create and store SOPs. Users could only ask questions on their own SOPs.

**After**: Only admins can create/store SOPs. All users can ask questions on any SOP and retrieve answers from the database.

---

## Detailed Changes

### 1. **Backend - Database Model Changes**

#### User Model
```python
# BEFORE
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    sops = db.relationship('SOP', backref='owner', lazy=True)

# AFTER
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)  # ← NEW
    sops = db.relationship('SOP', backref='owner', lazy=True)
    qna_logs = db.relationship('QnALog', backref='user', lazy=True)  # ← IMPROVED
    
    def is_admin(self):  # ← NEW METHOD
        return self.role == 'admin'
```

**Why**: 
- `role` field distinguishes between admins and regular users
- `is_admin()` method provides easy role checking throughout the app
- Better ORM relationship for QnALog

#### QnALog Model
```python
# BEFORE
class QnALog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    sources = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sop_id = db.Column(db.Integer, db.ForeignKey('sop.id'))

# AFTER
class QnALog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    sources = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.now())  # ← NEW
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # ← MADE NOT NULL
    sop_id = db.Column(db.Integer, db.ForeignKey('sop.id'), nullable=False)  # ← MADE NOT NULL
```

**Why**:
- `created_at` allows sorting and displaying when questions were asked
- NOT NULL constraints ensure data integrity

---

### 2. **Authentication Routes** (`backend/routes/auth.py`)

#### New Features
```python
# NEW: Admin creation via admin_secret
@auth_bp.route('/signup', methods=['POST'])
def signup():
    # Now accepts optional admin_secret parameter
    # If provided and matches ADMIN_SECRET env var, user is created as admin
    # Otherwise, user is created as regular user

# ENHANCED: Login now returns role
@auth_bp.route('/login', methods=['POST'])
def login():
    # Returns: access_token, user_id, email, role
    # Previously only returned: access_token

# NEW: Get current user endpoint
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    # Frontend can call this to determine user role
    # Used to show/hide admin-only UI elements
```

**Why**:
- Admin creation allows secure setup of admin users
- Login response includes role so frontend knows user type immediately
- `/auth/me` endpoint allows frontend to fetch user info after token validation

---

### 3. **SOP Management Routes** (`backend/routes/sops.py`)

#### Access Control Changes

```python
# BEFORE: Any authenticated user could create SOP
@sops_bp.route('/', methods=['POST'])
@jwt_required()
def create_sop():
    # Created SOP owned by current user
    owner_id=int(get_jwt_identity())

# AFTER: Only admins can create SOP
@sops_bp.route('/', methods=['POST'])
@jwt_required()
def create_sop():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user or not user.is_admin():  # ← ADMIN CHECK
        return jsonify({"msg": "Only admins can create SOPs"}), 403
```

#### New Endpoints

```python
# BEFORE: List only current user's SOPs
@sops_bp.route('/', methods=['GET'])
def list_sops():
    sops = SOP.query.filter_by(owner_id=user_id).all()
    # Returns only user's own SOPs

# AFTER: List all SOPs (available to everyone)
@sops_bp.route('/', methods=['GET'])
def list_all_sops():
    sops = SOP.query.all()  # ← NOW RETURNS ALL
    # Includes owner_email, owner_id, is_owner flag
    # Both admins and users can see all SOPs

# NEW: Admin can list only their SOPs
@sops_bp.route('/my-sops', methods=['GET'])
def list_my_sops():
    # For admins to see only SOPs they created

# NEW: Get single SOP
@sops_bp.route('/<int:sop_id>', methods=['GET'])
def get_sop(sop_id):
    # Any authenticated user can view any SOP

# NEW: Delete SOP (owner only)
@sops_bp.route('/<int:sop_id>', methods=['DELETE'])
def delete_sop(sop_id):
    # Only admin owner can delete
```

**Why**:
- Admin-only creation enforces centralized SOP management
- All users seeing all SOPs enables Q&A on any SOP
- Separate `/my-sops` for admin's personal management
- Delete endpoint with ownership verification prevents unauthorized deletion

---

### 4. **Question Routes** (`backend/routes/questions.py`)

#### Access Control Changes

```python
# BEFORE: User could only ask questions on SOPs they owned
@questions_bp.route('/', methods=['POST'])
def ask_question():
    # Only worked if current user was the SOP owner
    # (implicitly, since users could only see their own SOPs)

# AFTER: User can ask questions on ANY SOP
@questions_bp.route('/', methods=['POST'])
def ask_question():
    # Any authenticated user can ask about any SOP
    # RAG processes the question against SOP content
    # Answer stored in QnALog with user_id and sop_id
```

#### New Endpoints

```python
# NEW: Get user's question history
@questions_bp.route('/history', methods=['GET'])
def get_question_history():
    # Returns all questions asked by current user
    # Sorted by most recent

# NEW: Get single question
@questions_bp.route('/<int:question_id>', methods=['GET'])
def get_question(question_id):
    # Only the user who asked can view it
```

**Why**:
- All users can now leverage all SOPs in the system
- Q&A history tracking provides audit trail
- Single question endpoint allows detailed view

---

### 5. **Answer Routes** (`backend/routes/answers.py`)

```python
# ENHANCED: Better error handling and timestamps
@answers_bp.route('/', methods=['GET'])
def list_answers():
    # Now includes created_at timestamp
    # Better response structure

# NEW: Get single answer
@answers_bp.route('/<int:answer_id>', methods=['GET'])
def get_answer(answer_id):
    # Only owner can view
    # Detailed answer information
```

**Why**:
- Timestamps help track when questions were asked
- Consistent API structure across endpoints

---

### 6. **Frontend Component Changes**

#### Dashboard.js
```javascript
// BEFORE: Simple list of user's own SOPs

// AFTER: Role-aware dashboard
- Fetches user role on load
- Shows SOPForm only if user.is_admin === true
- Displays owner info for each SOP
- Shows delete button only for admin owners
- Shows role-specific greeting
- Handles both admin and user workflows
```

#### Login.js
```javascript
// BEFORE: Simple email/password form

// AFTER: Role-aware authentication
- Added admin_secret field in signup mode
- Shows role upon successful login
- Better error/success messaging
- Helps user understand their access level
```

#### SOPForm.js
```javascript
// BEFORE: Simple form for any user

// AFTER: Enhanced form
- Title indicates admin-only access
- Better validation
- Loading states
- Improved error handling
```

#### AskAI.js
```javascript
// BEFORE: Basic question input

// AFTER: Enhanced UI
- Loading states
- Enter key support
- Better message styling
- Shows SOP owner information
```

**Why**: Frontend needs to adapt to role-based access to provide correct UX for different user types.

---

## Data Flow Comparison

### Before
```
User (any role)
├── Sign up → All users get "user" role (no role field)
├── Create SOP → Own SOP
├── View SOPs → Only own SOPs
└── Ask Question → On own SOPs only
    └── Answer stored in QnALog
```

### After
```
User (with explicit role)
├── Sign up with admin_secret → Role = "admin"
├── Sign up without admin_secret → Role = "user"
│
├── If Admin:
│   ├── Create SOP ✓
│   ├── View all SOPs ✓
│   ├── Delete own SOPs ✓
│   └── Ask questions on any SOP ✓
│
└── If User:
    ├── Cannot create SOPs ✗
    ├── View all SOPs (read-only) ✓
    ├── Cannot delete SOPs ✗
    └── Ask questions on any SOP ✓
```

---

## Migration Path

### For Fresh Installation
1. Delete old database
2. Run app → New schema created with role column
3. Create admin user with admin_secret
4. Create regular users
5. Admin uploads SOPs
6. All users can ask questions

### For Existing Installation
1. Create backup of existing database
2. Run app → SQLAlchemy will attempt to create missing columns
3. If errors occur:
   ```bash
   # Option A: Manual update
   ALTER TABLE user ADD COLUMN role VARCHAR(20) DEFAULT 'user';
   ALTER TABLE qna_log ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP;
   ALTER TABLE qna_log MODIFY user_id INTEGER NOT NULL;
   ALTER TABLE qna_log MODIFY sop_id INTEGER NOT NULL;
   ```
4. Assign admin role to trusted users:
   ```bash
   UPDATE user SET role = 'admin' WHERE email IN ('admin1@company.com', 'admin2@company.com');
   ```

---

## Error Handling

### New Error Responses

| Endpoint | Error | Status | Reason |
|----------|-------|--------|--------|
| POST /sops/ | "Only admins can create SOPs" | 403 | Non-admin tried to create SOP |
| DELETE /sops/<id> | "Only the admin who created this SOP can delete it" | 403 | User tried to delete others' SOP |
| GET /questions/<id> | "You can only view your own questions" | 403 | User tried to view others' questions |

---

## Security Improvements

1. **Centralized SOP Management**: Admins control what SOPs exist (prevents spam/invalid SOPs)
2. **Role-based Access**: Clear separation of concerns
3. **Ownership Verification**: Users can only delete/modify their own content
4. **Audit Trail**: created_at timestamps in QnALog for tracking
5. **Admin Secret**: Secure way to create admin users without backend access

---

## Performance Implications

| Operation | Before | After | Impact |
|-----------|--------|-------|--------|
| List SOPs | Filter by owner_id | No filter | Slightly slower as data grows, but acceptable |
| Create SOP | One user owns | Admin only | Fewer writes overall |
| Ask Question | Limited to own SOPs | Any SOP | More Q&A activity expected |

---

## Backward Compatibility

⚠️ **NOT backward compatible** with existing databases. You must:
1. Migrate data OR
2. Start fresh (recommended for new deployments)

---

## Testing Strategy

### Unit Tests Needed
```python
# Authentication
- test_admin_signup_with_secret
- test_user_signup_without_secret
- test_login_returns_role

# SOP Management
- test_admin_can_create_sop
- test_user_cannot_create_sop
- test_all_users_see_all_sops
- test_admin_can_delete_own_sop
- test_user_cannot_delete_sop

# Questions
- test_user_can_ask_on_any_sop
- test_user_can_see_own_qna_history
- test_user_cannot_see_others_qna
```

### Integration Tests Needed
```python
# Admin workflow
- Signup as admin, create SOP, verify users see it

# User workflow
- Signup as user, ask question on admin's SOP, verify in history

# Permission tests
- User tries to create/delete SOP → 403
- User tries to view others' Q&A → 403
```

---

## Deployment Checklist

- [ ] Update environment variables (ADMIN_SECRET, JWT_SECRET_KEY)
- [ ] Backup existing database
- [ ] Run migration script or reset database
- [ ] Create admin user
- [ ] Test all endpoints with both admin and user roles
- [ ] Update frontend environment variables
- [ ] Test full workflow as admin
- [ ] Test full workflow as regular user
- [ ] Configure CORS for production domain
- [ ] Enable HTTPS
- [ ] Set up logging/monitoring
- [ ] Create admin and user documentation

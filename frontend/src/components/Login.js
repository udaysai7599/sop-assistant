import React, { useState } from 'react';
import axios from '../api';

function Login({ setToken }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [adminSecret, setAdminSecret] = useState('');
  const [isSignup, setIsSignup] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState(''); // 'success', 'error', 'info'

  const submit = async () => {
    try {
      setMessage('');
      const normalizedEmail = email.trim().toLowerCase();
      if (!normalizedEmail || !password) {
        setMessage('✗ Email and password are required');
        setMessageType('error');
        return;
      }

      if (isSignup && password.length < 8) {
        setMessage('✗ Password must be at least 8 characters');
        setMessageType('error');
        return;
      }

      if (isSignup) {
        const signupPayload = { email: normalizedEmail, password };
        if (adminSecret) {
          signupPayload.admin_secret = adminSecret;
        }
        await axios.post('/auth/signup', signupPayload);

        setIsSignup(false);
        setPassword('');
        setAdminSecret('');
        setMessage('✓ Account created successfully. Please login with your credentials.');
        setMessageType('success');
        return;
      }

      const loginRes = await axios.post('/auth/login', { email: normalizedEmail, password });
      setToken(loginRes.data.access_token);
      const roleText = loginRes.data.role === 'admin' ? 'Admin' : 'User';
      setMessage(`✓ Signed in successfully as ${roleText}`);
      setMessageType('success');
    } catch (error) {
      const errorMsg = error.response?.data?.msg ||
        'Cannot reach backend server at http://localhost:5000. Please start backend first.';
      setMessage(`✗ ${errorMsg}`);
      setMessageType('error');
    }
  };

  return (
    <div className="auth-layout">
      <div className="auth-hero-panel">
        <span className="eyebrow">Internal Knowledge Hub</span>
        <h1>SOP Assistant</h1>
        <p>
          Centralize operating procedures, attach supporting documents, and let teams retrieve the right answer in seconds.
        </p>
        <div className="hero-points">
          <div className="hero-point">
            <strong>Admin control</strong>
            <span>Create SOPs, attach documents, and keep guidance current.</span>
          </div>
          <div className="hero-point">
            <strong>Fast retrieval</strong>
            <span>Users ask plain-language questions and get sourced answers.</span>
          </div>
          <div className="hero-point">
            <strong>Audit trail</strong>
            <span>Saved Q&A history makes recurring operational questions visible.</span>
          </div>
        </div>
      </div>

      <div className="auth-card auth-panel">
        <div className="auth-panel-header">
          <span className="status-pill">Secure workspace</span>
          <h2>{isSignup ? 'Create account' : 'Welcome back'}</h2>
          <p className="muted">
            {isSignup
              ? 'Create a new account to get started. Admins can enter the admin secret during sign up.'
              : 'Sign in to manage SOPs, upload supporting files, or ask AI for guidance.'}
          </p>
        </div>
        <div className="form-grid">
          <input
            placeholder="Work email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            type="email"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={e => setPassword(e.target.value)}
          />
          {isSignup && (
            <input
              type="password"
              placeholder="Admin Secret (optional)"
              value={adminSecret}
              onChange={e => setAdminSecret(e.target.value)}
            />
          )}
        </div>
        <div className="action-row">
          <button onClick={submit}>{isSignup ? 'Create account' : 'Login'}</button>
          <button className="secondary" onClick={() => {
            setIsSignup(!isSignup);
            setMessage('');
            setAdminSecret('');
          }}>
            {isSignup ? 'Switch to login' : 'Switch to sign up'}
          </button>
        </div>
        {message && (
          <p className={`message banner-message ${messageType}`} style={{
            color: messageType === 'error' ? '#fecaca' : messageType === 'success' ? '#bbf7d0' : '#bfdbfe'
          }}>
            {message}
          </p>
        )}
      </div>
    </div>
  );
}

export default Login;

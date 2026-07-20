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
    <div className="auth-card">
      <h2>{isSignup ? 'Create account' : 'Welcome back'}</h2>
      <p className="muted">
        {isSignup 
          ? 'Create a new account to get started. (Admins: enter admin secret for admin privileges)'
          : 'Access SOP guidance, ask questions, and save answers.'}
      </p>
      <input 
        placeholder="Email" 
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
          placeholder="Admin Secret (optional, leave blank for regular user)" 
          value={adminSecret} 
          onChange={e => setAdminSecret(e.target.value)}
        />
      )}
      <button onClick={submit}>{isSignup ? 'Sign up' : 'Login'}</button>
      <button className="secondary" onClick={() => {
        setIsSignup(!isSignup);
        setMessage('');
        setAdminSecret('');
      }}>
        {isSignup ? 'Switch to login' : 'Switch to sign up'}
      </button>
      {message && (
        <p className={`message ${messageType}`} style={{
          color: messageType === 'error' ? '#d32f2f' : messageType === 'success' ? '#388e3c' : '#1976d2'
        }}>
          {message}
        </p>
      )}
    </div>
  );
}

export default Login;

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
      if (isSignup) {
        const signupPayload = { email, password };
        if (adminSecret) {
          signupPayload.admin_secret = adminSecret;
        }
        const signupRes = await axios.post('/auth/signup', signupPayload);
        setMessage(
          `Account created as ${signupRes.data.role === 'admin' ? 'Admin' : 'User'}. Now logging in...`,
          'success'
        );
        setMessageType('success');
      }
      const loginRes = await axios.post('/auth/login', { email, password });
      setToken(loginRes.data.access_token);
      const roleText = loginRes.data.role === 'admin' ? 'Admin' : 'User';
      setMessage(`Signed in successfully as ${roleText}`, 'success');
      setMessageType('success');
    } catch (error) {
      const errorMsg = error.response?.data?.msg || 'Authentication failed';
      setMessage(errorMsg, 'error');
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

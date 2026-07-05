import React, { useState } from 'react';
import axios from '../api';

function Login({ setToken }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSignup, setIsSignup] = useState(false);
  const [message, setMessage] = useState('');

  const submit = async () => {
    try {
      if (isSignup) {
        await axios.post('/auth/signup', { email, password });
      }
      const loginRes = await axios.post('/auth/login', { email, password });
      setToken(loginRes.data.access_token);
      setMessage(isSignup ? 'Account created and signed in' : 'Signed in successfully');
    } catch (error) {
      setMessage(error.response?.data?.msg || 'Authentication failed');
    }
  };

  return (
    <div className="auth-card">
      <h2>{isSignup ? 'Create account' : 'Welcome back'}</h2>
      <p className="muted">Access SOP guidance, ask questions, and save answers.</p>
      <input placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />
      <input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />
      <button onClick={submit}>{isSignup ? 'Sign up' : 'Login'}</button>
      <button className="secondary" onClick={() => setIsSignup(!isSignup)}>
        {isSignup ? 'Switch to login' : 'Switch to sign up'}
      </button>
      {message && <p className="message">{message}</p>}
    </div>
  );
}

export default Login;

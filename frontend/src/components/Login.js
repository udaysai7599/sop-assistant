import React, { useState } from 'react';
import axios from 'axios';

function Login({ setToken }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const login = async () => {
    const res = await axios.post('/auth/login', { email, password });
    setToken(res.data.access_token);
  };

  return (
    <div>
      <h2>Login</h2>
      <input placeholder="Email" onChange={e => setEmail(e.target.value)} />
      <input type="password" placeholder="Password" onChange={e => setPassword(e.target.value)} />
      <button onClick={login}>Login</button>
    </div>
  );
}

export default Login;

import React, { useState } from 'react';
import axios from './api';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import './styles.css';

function App() {
  const [token, setTokenState] = useState(() => localStorage.getItem('sop_token'));

  const setToken = (newToken) => {
    if (newToken) {
      localStorage.setItem('sop_token', newToken);
      axios.defaults.headers.common.Authorization = `Bearer ${newToken}`;
    } else {
      localStorage.removeItem('sop_token');
      delete axios.defaults.headers.common.Authorization;
    }
    setTokenState(newToken);
  };

  if (token && !axios.defaults.headers.common.Authorization) {
    axios.defaults.headers.common.Authorization = `Bearer ${token}`;
  }

  return (
    <div className="app-shell">
      {!token ? <Login setToken={setToken} /> : <Dashboard token={token} onLogout={() => setToken(null)} />}
    </div>
  );
}

export default App;

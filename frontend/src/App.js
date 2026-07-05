import React, { useEffect, useState } from 'react';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import './styles.css';

function App() {
  const [token, setToken] = useState(() => localStorage.getItem('sop_token'));

  useEffect(() => {
    if (token) {
      localStorage.setItem('sop_token', token);
    } else {
      localStorage.removeItem('sop_token');
    }
  }, [token]);

  return (
    <div className="app-shell">
      {!token ? <Login setToken={setToken} /> : <Dashboard token={token} onLogout={() => setToken(null)} />}
    </div>
  );
}

export default App;

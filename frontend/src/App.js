import React, { useEffect, useState } from 'react';
import axios from './api';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import './styles.css';

function App() {
  const [token, setTokenState] = useState(null);
  const [authReady, setAuthReady] = useState(false);
  const forceLoginOnStartup = (process.env.REACT_APP_FORCE_LOGIN_ON_STARTUP || 'true').toLowerCase() === 'true';

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

  useEffect(() => {
    const bootstrapAuth = async () => {
      if (forceLoginOnStartup) {
        localStorage.removeItem('sop_token');
        delete axios.defaults.headers.common.Authorization;
        setTokenState(null);
        setAuthReady(true);
        return;
      }

      const persistedToken = localStorage.getItem('sop_token');
      if (!persistedToken) {
        setAuthReady(true);
        return;
      }

      try {
        axios.defaults.headers.common.Authorization = `Bearer ${persistedToken}`;
        await axios.get('/auth/me');
        setTokenState(persistedToken);
      } catch (_) {
        localStorage.removeItem('sop_token');
        delete axios.defaults.headers.common.Authorization;
        setTokenState(null);
      } finally {
        setAuthReady(true);
      }
    };

    bootstrapAuth();
  }, [forceLoginOnStartup]);

  if (!authReady) {
    return (
      <div className="app-shell">
        <div className="auth-card">
          <h2>Checking session...</h2>
          <p className="muted">Please wait while we validate your login.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="app-shell">
      {!token ? <Login setToken={setToken} /> : <Dashboard token={token} onLogout={() => setToken(null)} />}
    </div>
  );
}

export default App;

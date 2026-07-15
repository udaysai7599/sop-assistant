import React, { useState, useEffect } from 'react';
import axios from '../api';
import SOPForm from './SOPForm';
import AskAI from './AskAI';
import SOPEditor from './SOPEditor';

function Dashboard({ token, onLogout }) {
  const [sops, setSops] = useState([]);
  const [answers, setAnswers] = useState([]);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedSop, setSelectedSop] = useState(null);

  // Fetch current user info to check role
  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }
    axios.get('/auth/me')
      .then(res => {
        setUser(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to fetch user info:', err);
        if (err.response?.status === 401 || err.response?.status === 422) {
          onLogout();
        }
        setLoading(false);
      });
  }, [token, onLogout]);

  const refreshSOPs = () => {
    axios.get('/sops/')
      .then(res => setSops(res.data))
      .catch(() => setSops([]));
  };

  const refreshAnswers = () => {
    axios.get('/answers/')
      .then(res => setAnswers(res.data))
      .catch(() => setAnswers([]));
  };

  useEffect(() => {
    if (user) {
      refreshSOPs();
      refreshAnswers();
    }
  }, [user, token]);

  const handleDeleteSOP = async (sopId) => {
    if (window.confirm('Are you sure you want to delete this SOP?')) {
      try {
        await axios.delete(`/sops/${sopId}`, { headers: { Authorization: `Bearer ${token}` } });
        refreshSOPs();
      } catch (error) {
        alert(error.response?.data?.msg || 'Failed to delete SOP');
      }
    }
  };

  const handleClearHistory = () => {
    if (window.confirm('Are you sure you want to clear all Q&A history?')) {
      setAnswers([]);
    }
  };

  if (loading) {
    return <div className="dashboard"><p>Loading...</p></div>;
  }

  if (!user) {
    return <div className="dashboard"><p>Error loading user information. Please login again.</p></div>;
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div>
          <h2>SOP Assistant Dashboard</h2>
          <p className="muted">
            {user.is_admin 
              ? 'You are an Admin. Create and manage SOPs. Users can ask questions about them.'
              : 'Ask questions against available SOPs and keep the answers for later.'}
          </p>
          <p className="muted">Logged in as: <strong>{user.email}</strong> ({user.role})</p>
        </div>
        <button className="secondary" onClick={onLogout}>Logout</button>
      </div>

      {/* Admin-only: SOP Creation Form */}
      {user.is_admin && (
        <SOPForm onCreated={() => { refreshSOPs(); refreshAnswers(); }} />
      )}

      {/* Available SOPs Section */}
      <div className="section-card">
        <h3>{user.is_admin ? 'All SOPs' : 'Available SOPs'}</h3>
        {sops.length === 0 ? (
          <p className="muted">{user.is_admin ? 'No SOPs created yet.' : 'No SOPs available yet.'}</p>
        ) : (
          sops.map(s => (
            <div key={s.id} className="sop-card" style={{ flexDirection: 'column', gap: '12px' }}>
              <div className="sop-info">
                <div style={{ flex: 1 }}>
                  <h4 style={{ margin: '0 0 8px 0' }}>{s.title}</h4>
                  <p className="muted" style={{ margin: '4px 0' }}>Department: {s.department_name}</p>
                  {s.owner_email && <p className="muted" style={{ margin: '4px 0' }}>Owner: {s.owner_email}</p>}
                  {user.is_admin && s.is_owner && (
                    <p className="muted" style={{ margin: '4px 0' }}><em>(You created this)</em></p>
                  )}
                </div>
                {user.is_admin && s.is_owner && (
                  <div className="sop-actions">
                    <button 
                      className="icon-btn"
                      title="View/Edit SOP"
                      onClick={() => setSelectedSop(s)}
                    >
                      ✎
                    </button>
                    <button 
                      className="icon-btn danger"
                      title="Delete SOP"
                      onClick={() => handleDeleteSOP(s.id)}
                    >
                      🗑
                    </button>
                  </div>
                )}
              </div>
              <div className="sop-ask">
                <AskAI token={token} sopId={s.id} onAnswered={refreshAnswers} />
              </div>
            </div>
          ))
        )}
      </div>

      {/* Answers/Q&A History Section */}
      <div className="section-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3>Your Q&A History</h3>
          {answers.length > 0 && (
            <button className="danger" onClick={handleClearHistory} style={{ padding: '8px 15px' }}>
              Clear History
            </button>
          )}
        </div>
        {answers.length === 0 ? (
          <p className="muted">No saved answers yet. Ask a question above to begin.</p>
        ) : (
          answers.map(item => (
            <div key={item.id} className="answer-item">
              <strong>{item.sop_title}</strong>
              <p className="muted">Asked at: {item.created_at ? new Date(item.created_at).toLocaleString() : 'N/A'}</p>
              <p><em>Q:</em> {item.question}</p>
              <p><em>A:</em> {item.answer}</p>
            </div>
          ))
        )}
      </div>

      {/* SOP Editor Modal */}
      {selectedSop && (
        <SOPEditor 
          sop={selectedSop} 
          onClose={() => setSelectedSop(null)}
          onUpdated={refreshSOPs}
        />
      )}
    </div>
  );
}

export default Dashboard;

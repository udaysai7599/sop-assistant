import React, { useState, useEffect } from 'react';
import axios from '../api';
import SOPForm from './SOPForm';
import AskAI from './AskAI';

function Dashboard({ token, onLogout }) {
  const [sops, setSops] = useState([]);
  const [answers, setAnswers] = useState([]);

  const refreshSOPs = () => {
    axios.get('/sops/', { headers: { Authorization: `Bearer ${token}` } })
      .then(res => setSops(res.data))
      .catch(() => setSops([]));
  };

  const refreshAnswers = () => {
    axios.get('/answers/', { headers: { Authorization: `Bearer ${token}` } })
      .then(res => setAnswers(res.data))
      .catch(() => setAnswers([]));
  };

  useEffect(() => {
    refreshSOPs();
    refreshAnswers();
  }, [token]);

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div>
          <h2>SOP Assistant Dashboard</h2>
          <p className="muted">Ask questions against your uploaded SOPs and keep the answers for later.</p>
        </div>
        <button className="secondary" onClick={onLogout}>Logout</button>
      </div>

      <SOPForm token={token} onCreated={() => { refreshSOPs(); refreshAnswers(); }} />

      <div className="section-card">
        <h3>Your SOPs</h3>
        {sops.length === 0 ? <p className="muted">No SOPs yet. Create one to begin.</p> : sops.map(s => (
          <div key={s.id} className="sop-card">
            <div>
              <h4>{s.title}</h4>
              <p className="muted">Department: {s.department_name}</p>
            </div>
            <AskAI token={token} sopId={s.id} onAnswered={refreshAnswers} />
          </div>
        ))}
      </div>

      <div className="section-card">
        <h3>Saved answers</h3>
        {answers.length === 0 ? <p className="muted">No saved answers yet.</p> : answers.map(item => (
          <div key={item.id} className="answer-item">
            <strong>{item.sop_title}</strong>
            <p><em>Q:</em> {item.question}</p>
            <p><em>A:</em> {item.answer}</p>
            {item.sources && <p className="sources">Source: {item.sources}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}

export default Dashboard;

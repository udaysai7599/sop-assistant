import React, { useState, useEffect } from 'react';
import axios from 'axios';
import SOPForm from './SOPForm';
import AskAI from './AskAI';

function Dashboard({ token }) {
  const [sops, setSops] = useState([]);

  useEffect(() => {
    axios.get('/sops/', { headers: { Authorization: `Bearer ${token}` } })
      .then(res => setSops(res.data));
  }, [token]);

  return (
    <div>
      <h2>Dashboard</h2>
      <SOPForm token={token} />
      {sops.map(s => (
        <div key={s.id}>
          <h3>{s.title}</h3>
          <AskAI token={token} sopId={s.id} />
        </div>
      ))}
    </div>
  );
}

export default Dashboard;

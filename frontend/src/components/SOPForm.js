import React, { useState } from 'react';
import axios from '../api';

function SOPForm({ token, onCreated }) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [departmentName, setDepartmentName] = useState('IT');
  const [message, setMessage] = useState('');

  const createSOP = async () => {
    try {
      await axios.post('/sops/',
        { title, content, department_name: departmentName },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setTitle('');
      setContent('');
      setDepartmentName('IT');
      if (onCreated) onCreated();
      setMessage('SOP created successfully');
    } catch (error) {
      setMessage(error.response?.data?.msg || 'Failed to create SOP');
    }
  };

  return (
    <div className="section-card">
      <h3>Create new SOP</h3>
      <input placeholder="SOP title" value={title} onChange={e => setTitle(e.target.value)} />
      <input placeholder="Department" value={departmentName} onChange={e => setDepartmentName(e.target.value)} />
      <textarea placeholder="Paste SOP content or guidance here" value={content} onChange={e => setContent(e.target.value)} />
      <button onClick={createSOP}>Save SOP</button>
      {message && <p className="message">{message}</p>}
    </div>
  );
}

export default SOPForm;

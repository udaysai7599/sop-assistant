import React, { useState } from 'react';
import axios from '../api';

function SOPForm({ token }) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');

  const createSOP = async () => {
    await axios.post('/sops/', 
      { title, content, department_id: 1 }, 
      { headers: { Authorization: `Bearer ${token}` } }
    );
    alert("SOP created!");
  };

  return (
    <div>
      <h3>Create SOP</h3>
      <input placeholder="Title" onChange={e => setTitle(e.target.value)} />
      <textarea placeholder="Content" onChange={e => setContent(e.target.value)} />
      <button onClick={createSOP}>Save</button>
    </div>
  );
}

export default SOPForm;

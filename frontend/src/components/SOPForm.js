import React, { useState } from 'react';
import axios from '../api';

function SOPForm({ onCreated }) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [departmentName, setDepartmentName] = useState('IT');
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const createSOP = async () => {
    if (!title.trim() || !content.trim()) {
      setMessage('Title and content are required');
      return;
    }

    setIsLoading(true);
    try {
      await axios.post('/sops/', { title, content, department_name: departmentName });
      setTitle('');
      setContent('');
      setDepartmentName('IT');
      if (onCreated) onCreated();
      setMessage('✓ SOP created successfully');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      const errorMsg = error.response?.data?.msg || 'Failed to create SOP';
      setMessage(`✗ ${errorMsg}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="section-card">
      <h3>📝 Create New SOP (Admin Only)</h3>
      <p className="muted" style={{ marginTop: 0 }}>
        Step 1: Create and save SOP text here. Step 2: Use the Upload document panel shown in that SOP card below.
      </p>
      <input 
        placeholder="SOP title" 
        value={title} 
        onChange={e => setTitle(e.target.value)}
        disabled={isLoading}
      />
      <input 
        placeholder="Department (e.g., IT, HR, Finance)" 
        value={departmentName} 
        onChange={e => setDepartmentName(e.target.value)}
        disabled={isLoading}
      />
      <textarea 
        placeholder="Paste SOP content or guidance here" 
        value={content} 
        onChange={e => setContent(e.target.value)}
        disabled={isLoading}
        rows={6}
      />
      <button 
        onClick={createSOP}
        disabled={isLoading}
      >
        {isLoading ? 'Creating...' : 'Save SOP'}
      </button>
      {message && (
        <p className="message" style={{
          color: message.startsWith('✓') ? '#388e3c' : '#d32f2f'
        }}>
          {message}
        </p>
      )}
    </div>
  );
}

export default SOPForm;

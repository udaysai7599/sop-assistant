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
    <div className="section-card creation-panel">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">Admin authoring</span>
          <h3>Create New SOP</h3>
        </div>
        <span className="status-pill">Admin only</span>
      </div>
      <p className="muted intro-copy">
        Draft the procedure here first. After saving, the SOP appears in the management list below where you can upload supporting documents for the same workflow.
      </p>

      <div className="form-grid two-column-grid">
        <div className="field-shell">
          <label>SOP Title</label>
          <input
            placeholder="Example: Employee Onboarding Procedure"
            value={title}
            onChange={e => setTitle(e.target.value)}
            disabled={isLoading}
          />
        </div>
        <div className="field-shell">
          <label>Department</label>
          <input
            placeholder="Example: HR, IT, Finance"
            value={departmentName}
            onChange={e => setDepartmentName(e.target.value)}
            disabled={isLoading}
          />
        </div>
      </div>

      <div className="field-shell">
        <label>Procedure Content</label>
        <textarea
          placeholder="Paste the operational steps, exceptions, approvals, and escalation guidance here."
          value={content}
          onChange={e => setContent(e.target.value)}
          disabled={isLoading}
          rows={8}
        />
      </div>

      <div className="panel-footer">
        <div className="muted helper-copy">Supported document upload becomes available immediately after this SOP is saved.</div>
        <button
          onClick={createSOP}
          disabled={isLoading}
          className="compact-btn"
        >
          {isLoading ? 'Creating...' : 'Save SOP'}
        </button>
      </div>
      {message && (
        <p className="message banner-message" style={{
          color: message.startsWith('✓') ? '#388e3c' : '#d32f2f'
        }}>
          {message}
        </p>
      )}
    </div>
  );
}

export default SOPForm;

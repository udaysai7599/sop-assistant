import React, { useState } from 'react';
import axios from '../api';

function SOPEditor({ sop, onClose, onUpdated }) {
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    title: sop.title,
    content: sop.content,
    department_name: sop.department_name
  });
  const [message, setMessage] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSave = async () => {
    if (!formData.title.trim() || !formData.content.trim()) {
      setMessage('✗ Title and content are required');
      return;
    }

    setIsSaving(true);
    setMessage('');
    try {
      const res = await axios.put(`/sops/${sop.id}`, {
        title: formData.title.trim(),
        content: formData.content.trim(),
        department_name: formData.department_name.trim()
      });
      setMessage('✓ SOP updated successfully');
      setIsEditing(false);
      if (onUpdated) onUpdated();
      setTimeout(() => onClose(), 2000);
    } catch (error) {
      setMessage(`✗ ${error.response?.data?.msg || 'Failed to update SOP'}`);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{isEditing ? 'Edit SOP' : 'View SOP'}</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          {isEditing ? (
            <>
              <div className="form-group">
                <label>SOP Title</label>
                <input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleChange}
                  placeholder="Enter SOP title"
                />
              </div>

              <div className="form-group">
                <label>Department</label>
                <input
                  type="text"
                  name="department_name"
                  value={formData.department_name}
                  onChange={handleChange}
                  placeholder="Enter department name"
                />
              </div>

              <div className="form-group">
                <label>Content</label>
                <textarea
                  name="content"
                  value={formData.content}
                  onChange={handleChange}
                  placeholder="Enter SOP content"
                  rows="12"
                  style={{ fontFamily: 'monospace', fontSize: '12px' }}
                />
              </div>

              {message && (
                <p className="message" style={{
                  color: message.startsWith('✓') ? '#388e3c' : '#d32f2f'
                }}>
                  {message}
                </p>
              )}

              <div className="modal-actions">
                <button 
                  onClick={handleSave}
                  disabled={isSaving}
                  style={{ backgroundColor: '#388e3c' }}
                >
                  {isSaving ? 'Saving...' : 'Save Changes'}
                </button>
                <button 
                  onClick={() => {
                    setIsEditing(false);
                    setFormData({
                      title: sop.title,
                      content: sop.content,
                      department_name: sop.department_name
                    });
                    setMessage('');
                  }}
                  className="secondary"
                >
                  Cancel
                </button>
              </div>
            </>
          ) : (
            <>
              <div className="sop-details">
                <div className="detail-row">
                  <strong>Title:</strong>
                  <p>{sop.title}</p>
                </div>

                <div className="detail-row">
                  <strong>Department:</strong>
                  <p>{sop.department_name}</p>
                </div>

                <div className="detail-row">
                  <strong>Content:</strong>
                  <pre style={{
                    backgroundColor: '#f5f5f5',
                    padding: '15px',
                    borderRadius: '4px',
                    overflow: 'auto',
                    maxHeight: '400px',
                    fontSize: '12px',
                    lineHeight: '1.5'
                  }}>
                    {sop.content}
                  </pre>
                </div>
              </div>

              <div className="modal-actions">
                <button 
                  onClick={() => setIsEditing(true)}
                  style={{ backgroundColor: '#1976d2' }}
                >
                  Edit SOP
                </button>
                <button onClick={onClose} className="secondary">
                  Close
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default SOPEditor;

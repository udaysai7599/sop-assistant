import React, { useState } from 'react';
import axios from '../api';

function DocumentUpload({ onUploaded }) {
  const [title, setTitle] = useState('');
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');
  const [isUploading, setIsUploading] = useState(false);

  const handleUpload = async () => {
    if (!file) {
      setMessage('Please choose a file first');
      return;
    }

    const formData = new FormData();
    formData.append('title', title || file.name);
    formData.append('file', file);

    setIsUploading(true);
    try {
      await axios.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setMessage('✓ Document uploaded and indexed');
      setTitle('');
      setFile(null);
      if (onUploaded) onUploaded();
    } catch (error) {
      setMessage(error.response?.data?.msg || 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="section-card">
      <h3>📄 Upload a document</h3>
      <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Document title" />
      <input type="file" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={handleUpload} disabled={isUploading}>
        {isUploading ? 'Uploading...' : 'Upload and index'}
      </button>
      {message && <p className="message">{message}</p>}
    </div>
  );
}

export default DocumentUpload;

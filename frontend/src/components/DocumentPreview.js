import React from 'react';

function DocumentPreview({ documents }) {
  if (!documents || documents.length === 0) {
    return null;
  }

  return (
    <div className="section-card">
      <h3>📚 Uploaded documents</h3>
      {documents.map((doc) => (
        <div key={doc.id} className="answer-item">
          <strong>{doc.title}</strong>
          <p className="muted">Chunks indexed: {doc.chunk_count}</p>
        </div>
      ))}
    </div>
  );
}

export default DocumentPreview;

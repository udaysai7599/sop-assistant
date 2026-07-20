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
  const [uploadFiles, setUploadFiles] = useState({});
  const [uploadTitles, setUploadTitles] = useState({});
  const [uploadMessages, setUploadMessages] = useState({});

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
      if (user.is_admin) {
        refreshSOPs();
      }
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
      axios.delete('/answers/')
        .then(() => refreshAnswers())
        .catch((error) => {
          alert(error.response?.data?.msg || 'Failed to clear history');
        });
    }
  };

  const downloadDocument = async (downloadUrl, fallbackName = 'document') => {
    try {
      const response = await axios.get(downloadUrl, { responseType: 'blob' });
      const blobUrl = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = blobUrl;
      link.setAttribute('download', fallbackName);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(blobUrl);
    } catch (error) {
      alert(error.response?.data?.msg || 'Failed to download document');
    }
  };

  const handleUploadFileChange = (sopId, file) => {
    setUploadFiles(prev => ({ ...prev, [sopId]: file }));
  };

  const handleUploadTitleChange = (sopId, value) => {
    setUploadTitles(prev => ({ ...prev, [sopId]: value }));
  };

  const uploadDocument = async (sopId) => {
    const file = uploadFiles[sopId];
    if (!file) {
      setUploadMessages(prev => ({ ...prev, [sopId]: 'Please choose a document file to upload.' }));
      return;
    }

    const formData = new FormData();
    formData.append('document_file', file);
    formData.append('document_title', uploadTitles[sopId] || file.name);

    try {
      await axios.post(`/sops/${sopId}/documents`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setUploadFiles(prev => ({ ...prev, [sopId]: null }));
      setUploadTitles(prev => ({ ...prev, [sopId]: '' }));
      setUploadMessages(prev => ({ ...prev, [sopId]: 'Document uploaded successfully.' }));
      refreshSOPs();
      setTimeout(() => setUploadMessages(prev => ({ ...prev, [sopId]: '' })), 3000);
    } catch (error) {
      setUploadMessages(prev => ({ ...prev, [sopId]: error.response?.data?.msg || 'Upload failed.' }));
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

      {/* Questioning experience */}
      {user.is_admin ? (
        <div className="section-card">
          <h3>All SOPs</h3>
          <p className="muted" style={{ marginTop: 0 }}>
            Document upload is available inside each SOP card after the SOP is created. Only the admin who created the SOP can upload documents for it.
          </p>
          {sops.length === 0 ? (
            <p className="muted">No SOPs created yet. Create one above, then use its Upload document panel.</p>
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
                {Array.isArray(s.documents) && s.documents.length > 0 && (
                  <div className="document-list">
                    <strong>Documents</strong>
                    <ul>
                      {s.documents.map(doc => (
                        <li key={doc.id}>
                          <span>{doc.title || doc.original_filename}</span>
                          {' '}
                          <button
                            className="secondary"
                            style={{ width: 'auto', padding: '6px 10px', marginLeft: 8 }}
                            onClick={() => downloadDocument(doc.download_url, doc.original_filename || doc.title || 'document')}
                          >
                            Download
                          </button>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {user.is_admin && s.is_owner && (
                  <div className="document-upload-panel">
                    <h4 style={{ margin: '0 0 8px 0' }}>Upload document</h4>
                    <input
                      type="text"
                      placeholder="Document title"
                      value={uploadTitles[s.id] || ''}
                      onChange={e => handleUploadTitleChange(s.id, e.target.value)}
                    />
                    <input
                      type="file"
                      accept=".txt,.md,.csv,.pdf,.doc,.docx"
                      onChange={e => handleUploadFileChange(s.id, e.target.files[0])}
                    />
                    <button onClick={() => uploadDocument(s.id)}>Upload</button>
                    {uploadMessages[s.id] && (
                      <p className="message" style={{
                        color: uploadMessages[s.id].startsWith('Document uploaded') ? '#388e3c' : '#d32f2f'
                      }}>
                        {uploadMessages[s.id]}
                      </p>
                    )}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      ) : (
        <div className="section-card">
          <h3>Ask AI</h3>
          <p className="muted">Ask your question directly. The assistant will fetch the most relevant SOP guidance automatically.</p>
          <AskAI token={token} onAnswered={refreshAnswers} />
        </div>
      )}

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
              {Array.isArray(item.sources) && item.sources.length > 0 && (
                <div>
                  <p><em>Sources:</em></p>
                  {item.sources.map((source, index) => (
                    <p key={`${item.id}-src-${index}`} className="muted">
                      [{index + 1}] {source.sop_title || 'SOP'}: {source.excerpt}
                      {source.download_url ? (
                        <>
                          {' '}
                          <button
                            className="secondary"
                            style={{ width: 'auto', padding: '6px 10px', marginLeft: 8 }}
                            onClick={() => downloadDocument(source.download_url, source.document_title || 'source-document')}
                          >
                            Download source document
                          </button>
                        </>
                      ) : null}
                    </p>
                  ))}
                </div>
              )}
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

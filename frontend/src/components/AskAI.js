import React, { useState, useEffect } from 'react';
import axios from '../api';

function AskAI({ token, sopId, onAnswered }) {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState([]);
  const [confidence, setConfidence] = useState('');
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setAnswer('');
    setSources([]);
    setConfidence('');
    setQuestion('');
    setMessage('');
  }, [sopId]);

  const ask = async () => {
    if (!question.trim()) {
      setMessage('Please enter a question');
      return;
    }

    setIsLoading(true);
    setMessage('');
    try {
      const payload = { question };
      if (sopId) payload.sop_id = sopId;

      const res = await axios.post('/questions/', payload);
      setAnswer(res.data.answer);
      setSources(Array.isArray(res.data.sources) ? res.data.sources : []);
      setConfidence(res.data.confidence || '');
      setQuestion('');
      setMessage('✓ Answer saved to your history');
      if (onAnswered) onAnswered();
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      console.error('AskAI request failed:', error.response || error.message);
      const errorMsg = error.response?.data?.msg || error.message || 'Unable to answer that question';
      setMessage(`✗ ${errorMsg}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey && !isLoading) {
      ask();
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
      setMessage(`✗ ${error.response?.data?.msg || 'Failed to download document'}`);
    }
  };

  return (
    <div className="ask-ai">
      <div className="ask-input-group">
        <input
          placeholder={sopId ? 'Ask about this SOP or uploaded document' : 'Ask a question and AI will find the best SOP guidance'}
          value={question} 
          onChange={e => setQuestion(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={isLoading}
        />
        <button 
          onClick={ask}
          disabled={isLoading}
        >
          {isLoading ? 'Thinking...' : 'Ask'}
        </button>
      </div>
      {answer && (
        <div className="answer-box">
          {confidence && (
            <p className="muted" style={{ marginTop: 0 }}>
              Confidence: <strong>{confidence}</strong>
            </p>
          )}
          <strong>Answer:</strong>
          <p>{answer}</p>
          {sources.length > 0 && (
            <div>
              <strong>Sources:</strong>
              {sources.map((source, index) => (
                <p key={`${source.sop_id || 'sop'}-${index}`} className="muted">
                  [{index + 1}] {source.sop_title || 'SOP'}
                  {source.source_type === 'document' && source.document_title ? ` (${source.document_title})` : ''}
                  : {source.excerpt}
                  {source.download_url ? (
                    <>
                      {' '}
                      <button
                        className="secondary"
                        style={{ width: 'auto', padding: '6px 10px', marginLeft: 8 }}
                        onClick={() => downloadDocument(source.download_url, source.document_title || 'document')}
                      >
                        Download document
                      </button>
                    </>
                  ) : null}
                </p>
              ))}
            </div>
          )}
        </div>
      )}
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

export default AskAI;

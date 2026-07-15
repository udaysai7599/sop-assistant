import React, { useState, useEffect } from 'react';
import axios from '../api';

function AskAI({ token, sopId, onAnswered }) {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState('');
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [selectedDocumentId, setSelectedDocumentId] = useState('');

  useEffect(() => {
    axios.get('/documents/')
      .then((res) => setDocuments(res.data))
      .catch(() => setDocuments([]));
  }, []);

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
      if (selectedDocumentId) payload.document_id = selectedDocumentId;

      const res = await axios.post('/questions/', payload);
      setAnswer(res.data.answer);
      setSources(res.data.sources);
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

  return (
    <div className="ask-ai">
      <div className="ask-input-group">
        <input 
          placeholder="Ask about this SOP or uploaded document" 
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
      {documents.length > 0 && (
        <select value={selectedDocumentId} onChange={e => setSelectedDocumentId(e.target.value)}>
          <option value="">Use SOP context</option>
          {documents.map(doc => (
            <option key={doc.id} value={doc.id}>{doc.title}</option>
          ))}
        </select>
      )}
      {answer && (
        <div className="answer-box">
          <strong>Answer:</strong>
          <p>{answer}</p>
          {sources && <p className="muted">Source excerpt: {sources}</p>}
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

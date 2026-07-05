import React, { useState } from 'react';
import axios from '../api';

function AskAI({ token, sopId, onAnswered }) {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState('');
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const ask = async () => {
    if (!question.trim()) {
      setMessage('Please enter a question');
      return;
    }

    setIsLoading(true);
    setMessage('');
    try {
      const res = await axios.post('/questions/',
        { sop_id: sopId, question },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setAnswer(res.data.answer);
      setSources(res.data.sources);
      setQuestion('');
      setMessage('✓ Answer saved to your history');
      if (onAnswered) onAnswered();
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      const errorMsg = error.response?.data?.msg || 'Unable to answer that question';
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
          placeholder="Ask about this SOP (press Enter to submit)" 
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
          <strong>Answer:</strong>
          <p>{answer}</p>
        </div>
      )}
      {sources && (
        <p className="sources">
          <strong>Source excerpt:</strong> {sources}
        </p>
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

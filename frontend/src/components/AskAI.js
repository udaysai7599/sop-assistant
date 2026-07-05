import React, { useState } from 'react';
import axios from '../api';

function AskAI({ token, sopId, onAnswered }) {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState('');
  const [message, setMessage] = useState('');

  const ask = async () => {
    try {
      const res = await axios.post('/questions/',
        { sop_id: sopId, question },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setAnswer(res.data.answer);
      setSources(res.data.sources);
      setMessage('Answer saved to your history');
      if (onAnswered) onAnswered();
    } catch (error) {
      setMessage(error.response?.data?.msg || 'Unable to answer that question');
    }
  };

  return (
    <div className="ask-ai">
      <input placeholder="Ask about this SOP" value={question} onChange={e => setQuestion(e.target.value)} />
      <button onClick={ask}>Ask AI</button>
      {answer && <div className="answer-box"><strong>Answer:</strong> {answer}</div>}
      {sources && <p className="sources">Source excerpt: {sources}</p>}
      {message && <p className="message">{message}</p>}
    </div>
  );
}

export default AskAI;

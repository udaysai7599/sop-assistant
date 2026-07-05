import React, { useState } from 'react';
import axios from '../api';

function AskAI({ token, sopId }) {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');

  const ask = async () => {
    const res = await axios.post('/questions/', 
      { sop_id: sopId, question }, 
      { headers: { Authorization: `Bearer ${token}` } }
    );
    setAnswer(res.data.answer);
  };

  return (
    <div>
      <input placeholder="Ask a question" onChange={e => setQuestion(e.target.value)} />
      <button onClick={ask}>Ask</button>
      {answer && <p><strong>Answer:</strong> {answer}</p>}
    </div>
  );
}

export default AskAI;

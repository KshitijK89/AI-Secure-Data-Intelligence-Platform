import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './ChatInput.css';

const ChatInput = () => {
  const navigate = useNavigate();
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [options, setOptions] = useState({
    mask: true,
    block_high_risk: false,
    log_analysis: false
  });

  const handleAnalyze = async () => {
    if (!message.trim()) {
      alert('Please enter some text to analyze');
      return;
    }

    setLoading(true);

    const formData = new FormData();
    formData.append('content', message);
    formData.append('input_type', 'chat');
    formData.append('mask', options.mask);
    formData.append('block_high_risk', options.block_high_risk);
    formData.append('log_analysis', options.log_analysis);

    try {
      const response = await axios.post('http://127.0.0.1:8000/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      console.log('Analysis response:', response.data);
      
      navigate('/results', {
        state: {
          results: response.data,
          insights: response.data.ai_insights
        }
      });
    } catch (error) {
      console.error('Analysis error:', error);
      alert(error.response?.data?.detail || 'Analysis failed. Please try again.');
      setLoading(false);
    }
  };

  const handleOptionChange = (option) => {
    setOptions(prev => ({
      ...prev,
      [option]: !prev[option]
    }));
  };

  return (
    <div className="chat-input-container">
      <div className="chat-header">
        <h3>💬 Live Chat Analysis</h3>
        <p>Paste text, logs, or code for instant security analysis</p>
      </div>

      <textarea
        className="chat-textarea"
        placeholder="Paste your text, log entries, or code here for instant analysis...&#10;&#10;Example:&#10;API_KEY=sk-prod-abc123xyz456&#10;password=mySecretPass123&#10;user@example.com logged in from 192.168.1.1"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        rows={10}
      />

      <div className="char-count">
        {message.length} characters
      </div>

      <div className="options-section">
        <h3>Analysis Options</h3>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={options.mask}
            onChange={() => handleOptionChange('mask')}
          />
          <span>Mask sensitive data</span>
        </label>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={options.block_high_risk}
            onChange={() => handleOptionChange('block_high_risk')}
          />
          <span>Block high-risk content</span>
        </label>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={options.log_analysis}
            onChange={() => handleOptionChange('log_analysis')}
          />
          <span>Enable log analysis</span>
        </label>
      </div>

      <button
        className="analyze-button"
        onClick={handleAnalyze}
        disabled={!message.trim() || loading}
      >
        {loading ? '⏳ Analyzing...' : '🔍 Analyze Text'}
      </button>
    </div>
  );
};

export default ChatInput;

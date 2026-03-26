import React, { useState } from 'react';
import FileUpload from '../components/FileUpload';
import ChatInput from '../components/ChatInput';
import './HomePage.css';

function HomePage() {
  const [activeTab, setActiveTab] = useState('file');

  return (
    <div className="home-page">
      <div className="home-container">
        <div className="home-header">
          <div className="header-badge">
            <span className="badge-icon">🛡️</span>
            <span>AI-Powered Security</span>
          </div>
          <h1 className="animated-title">
            AI Secure Data Intelligence
          </h1>
          <p className="subtitle">
            Advanced security analysis powered by artificial intelligence
          </p>
          <div className="features-tags">
            <span className="feature-tag">🔍 Deep Scanning</span>
            <span className="feature-tag">⚡ Real-time</span>
            <span className="feature-tag">🤖 AI Insights</span>
          </div>
        </div>
        
        <div className="input-tabs">
          <button
            className={`tab-button ${activeTab === 'file' ? 'active' : ''}`}
            onClick={() => setActiveTab('file')}
          >
            <span className="tab-icon">📁</span>
            <span className="tab-text">File Upload</span>
          </button>
          <button
            className={`tab-button ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            <span className="tab-icon">💬</span>
            <span className="tab-text">Live Text</span>
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'file' ? <FileUpload /> : <ChatInput />}
        </div>
      </div>
    </div>
  );
}

export default HomePage;

import React, { useState, useEffect } from 'react';
import FileUpload from '../components/FileUpload';
import ChatInput from '../components/ChatInput';
import './HomePage.css';

const API_URL = (() => {
  const configuredUrl = process.env.REACT_APP_API_URL;
  const isLocalhost = typeof window !== 'undefined' && ['localhost', '127.0.0.1'].includes(window.location.hostname);

  if (isLocalhost) {
    return configuredUrl && !configuredUrl.includes('your-backend-name.onrender.com')
      ? configuredUrl
      : 'http://127.0.0.1:8000';
  }

  if (!configuredUrl || configuredUrl.includes('your-backend-name.onrender.com')) {
    return '/api';
  }
  return configuredUrl;
})();

function HomePage() {
  const [activeTab, setActiveTab] = useState('file');
  const [backendReady, setBackendReady] = useState(false);
  const [backendStatus, setBackendStatus] = useState('Checking backend...');

  // Warm up backend on page load to avoid cold start delay
  useEffect(() => {
    let isMounted = true;
    const controller = new AbortController();
    let retryTimer = null;
    let attempts = 0;
    const maxAttempts = 12;

    const pingBackend = async () => {
      attempts += 1;
      try {
        const response = await fetch(`${API_URL}/health`, {
          cache: 'no-store',
          signal: controller.signal,
        });

        if (isMounted && response.ok) {
          const healthData = await response.json();
          const providerStatus = healthData?.ai_provider_status || {};
          const geminiState = providerStatus.gemini_enabled ? 'Gemini on' : 'Gemini off';
          const groqState = providerStatus.groq_enabled ? 'Groq on' : 'Groq off';
          setBackendReady(true);
          setBackendStatus(`${healthData.status || 'healthy'} · ${geminiState} · ${groqState}`);
          return;
        }

        if (isMounted) {
          setBackendStatus(`Backend returned ${response.status}`);
        }
      } catch (error) {
        if (error.name === 'AbortError') {
          return;
        }

        if (isMounted) {
          setBackendStatus(`Backend check failed: ${error.message}`);
        }
      }

      if (isMounted && attempts < maxAttempts) {
        retryTimer = setTimeout(pingBackend, 2000);
      } else if (isMounted) {
        setBackendStatus(`Backend unavailable after ${maxAttempts} attempts`);
      }
    };

    pingBackend();

    return () => {
      isMounted = false;
      controller.abort();
      if (retryTimer) {
        clearTimeout(retryTimer);
      }
    };
  }, []);

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

      <div className={`backend-status ${backendReady ? 'ready' : 'warming'}`}>
        <span className="status-dot"></span>
        <span>{backendReady ? 'Backend Ready' : backendStatus}</span>
      </div>
    </div>
  );
}

export default HomePage;

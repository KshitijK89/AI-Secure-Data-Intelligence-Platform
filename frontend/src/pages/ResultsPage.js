import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import InsightsPanel from '../components/InsightsPanel';
import ContentDisplay from '../components/ContentDisplay';
import ResultsPanel from '../components/ResultsPanel';
import RiskGauge from '../components/RiskGauge';
import StatCard from '../components/StatCard';
import './ResultsPage.css';

function ResultsPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [shouldRedirect, setShouldRedirect] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);

  useEffect(() => {
    console.log('ResultsPage mounted');
    console.log('Location state:', location.state);
    
    // Give a brief moment for state to populate, then check
    const timer = setTimeout(() => {
      if (!location.state) {
        console.log('No state found after timeout, will redirect');
        setShouldRedirect(true);
      }
    }, 100);

    return () => clearTimeout(timer);
  }, [location.state]);

  useEffect(() => {
    if (shouldRedirect) {
      console.log('Redirecting to home');
      navigate('/', { replace: true });
    }
  }, [shouldRedirect, navigate]);

  const { results, insights } = location.state || {};

  const downloadPDFReport = async () => {
    setIsDownloading(true);
    try {
      const reportData = {
        summary: results.summary,
        risk_level: results.risk_level,
        risk_score: results.risk_score,
        statistics: results.statistics,
        findings: results.findings,
        insights: results.insights,
        content_type: results.content_type
      };

      console.log('Sending report data:', reportData);

      const API_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';
      const response = await axios.post(
        `${API_URL}/generate-report`,
        reportData,
        {
          responseType: 'blob',
          headers: {
            'Content-Type': 'application/json'
          },
          timeout: 30000 // 30 second timeout
        }
      );

      console.log('Response received, size:', response.data.size);

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'security_analysis_report.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

    } catch (error) {
      console.error('PDF download failed:', error);
      console.error('Error details:', error.response?.data);
      alert(`Failed to generate PDF report: ${error.message}`);
    } finally {
      setIsDownloading(false);
    }
  };

  // Show loading while checking
  if (!location.state || !results) {
    return (
      <div className="results-page">
        <div className="results-header">
          <button className="back-button" onClick={() => navigate('/')}>
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M12.5 15L7.5 10L12.5 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Back
          </button>
          <h1>Analysis Results</h1>
        </div>
        <div style={{ padding: '2rem', textAlign: 'center', color: '#8e8e93' }}>
          <p>Loading results...</p>
        </div>
      </div>
    );
  }

  console.log('Rendering results:', results);
  console.log('Rendering insights:', insights);

  return (
    <div className="results-page">
      <div className="results-header">
        <button className="back-button" onClick={() => navigate('/')}>
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M12.5 15L7.5 10L12.5 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Back
        </button>
        <h1>Analysis Results</h1>
        <button 
          className="download-pdf-button" 
          onClick={downloadPDFReport}
          disabled={isDownloading}
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M17.5 12.5V15.8333C17.5 16.2754 17.3244 16.6993 17.0118 17.0118C16.6993 17.3244 16.2754 17.5 15.8333 17.5H4.16667C3.72464 17.5 3.30072 17.3244 2.98816 17.0118C2.67559 16.6993 2.5 16.2754 2.5 15.8333V12.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M5.83334 8.33337L10 12.5L14.1667 8.33337" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M10 12.5V2.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          {isDownloading ? 'Generating...' : 'Download PDF'}
        </button>
      </div>
      
      <div className="results-overview">
        <RiskGauge 
          riskScore={results.risk_score || 0} 
          riskLevel={results.risk_level || 'Low'}
        />
        <div className="stats-grid">
          <StatCard 
            label="Issues Found"
            value={results.statistics?.total_findings || 0}
            icon="🔍"
            color="#667eea"
          />
          <StatCard 
            label="Critical"
            value={results.statistics?.critical || 0}
            icon="🚨"
            color="#ef4444"
          />
          <StatCard 
            label="High"
            value={results.statistics?.high || 0}
            icon="⚠️"
            color="#f59e0b"
          />
          <StatCard 
            label="Medium"
            value={results.statistics?.medium || 0}
            icon="📊"
            color="#3b82f6"
          />
        </div>
      </div>
      
      <div className="results-content">
        {insights && <InsightsPanel insights={insights} />}
        <ContentDisplay 
          content={results.processed_content} 
          contentType={results.content_type || 'text'} 
        />
        <ResultsPanel results={results} />
      </div>
    </div>
  );
}

export default ResultsPage;

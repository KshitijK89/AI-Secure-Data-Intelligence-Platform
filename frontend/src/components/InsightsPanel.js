import React from 'react';
import './InsightsPanel.css';

const InsightsPanel = ({ insights }) => {
  const { insights: insightList, summary, risk_level, risk_score, statistics } = insights || {};

  const getRiskColor = (level) => {
    const colors = {
      critical: '#dc3545',
      high: '#fd7e14',
      medium: '#ffc107',
      low: '#28a745',
      none: '#6c757d'
    };
    return colors[level] || '#6c757d';
  };

  const getRiskEmoji = (level) => {
    const emojis = {
      critical: '🚨',
      high: '⚠️',
      medium: '⚡',
      low: 'ℹ️',
      none: '✅'
    };
    return emojis[level] || 'ℹ️';
  };

  if (!insights) {
    return null;
  }

  return (
    <div className="insights-panel">
      <div className="panel-header">
        <h2>AI-Powered Insights</h2>
      </div>

      <div className="summary-section">
        <div className="summary-card">
          <h3 style={{ color: '#ffffff', fontSize: '0.9rem', fontWeight: '600', marginBottom: '0.5rem' }}>Summary</h3>
          <p style={{ color: '#e5e5e7', fontSize: '0.9rem', lineHeight: '1.5' }}>{summary}</p>
        </div>

        <div className="risk-card" style={{ borderColor: getRiskColor(risk_level) }}>
          <span className="risk-emoji">{getRiskEmoji(risk_level)}</span>
          <h3 style={{ color: '#ffffff', fontSize: '0.9rem', fontWeight: '600' }}>Risk Assessment</h3>
          <div className="risk-score-display">
            <div className="risk-score-number" style={{ color: getRiskColor(risk_level) }}>
              {risk_score || 0}
            </div>
            <div className="risk-score-label">Risk Score</div>
          </div>
          <p className="risk-level" style={{ color: getRiskColor(risk_level), marginTop: '0.5rem' }}>
            {risk_level.toUpperCase()}
          </p>
        </div>
      </div>

      <div className="statistics-section">
        <h3>Findings Breakdown</h3>
        <div className="stats-grid">
          <div className="stat-card critical">
            <div className="stat-number">{statistics.critical}</div>
            <div className="stat-label">Critical</div>
          </div>
          <div className="stat-card high">
            <div className="stat-number">{statistics.high}</div>
            <div className="stat-label">High</div>
          </div>
          <div className="stat-card medium">
            <div className="stat-number">{statistics.medium}</div>
            <div className="stat-label">Medium</div>
          </div>
          <div className="stat-card low">
            <div className="stat-number">{statistics.low}</div>
            <div className="stat-label">Low</div>
          </div>
        </div>
      </div>

      <div className="insights-list">
        <h3>Key Insights</h3>
        {insightList && insightList.length > 0 ? (
          <ul>
            {insightList.map((insight, index) => (
              <li key={index} className="insight-item">
                <span className="insight-bullet">•</span>
                <span className="insight-text">{insight}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="no-insights">No specific insights generated</p>
        )}
      </div>
    </div>
  );
};

export default InsightsPanel;

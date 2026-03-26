import React, { useState } from 'react';
import './ResultsPanel.css';

const ResultsPanel = ({ results }) => {
  const { findings, action } = results;
  const [filter, setFilter] = useState('all');

  const getRiskIcon = (risk) => {
    const icons = {
      critical: '🚨',
      high: '⚠️',
      medium: '⚡',
      low: 'ℹ️'
    };
    return icons[risk] || 'ℹ️';
  };

  const getRiskClass = (risk) => {
    return `finding-card ${risk}-risk`;
  };

  const filteredFindings = filter === 'all'
    ? findings
    : findings.filter(f => f.risk === filter);

  return (
    <div className="results-panel">
      <div className="results-header">
        <h2>🔍 Detailed Findings</h2>
        <div className="action-badge">
          Action: <span className={`action-${action}`}>{action.toUpperCase()}</span>
        </div>
      </div>

      <div className="filter-section">
        <button
          className={filter === 'all' ? 'filter-btn active' : 'filter-btn'}
          onClick={() => setFilter('all')}
        >
          All ({findings.length})
        </button>
        <button
          className={filter === 'critical' ? 'filter-btn active critical' : 'filter-btn critical'}
          onClick={() => setFilter('critical')}
        >
          Critical ({findings.filter(f => f.risk === 'critical').length})
        </button>
        <button
          className={filter === 'high' ? 'filter-btn active high' : 'filter-btn high'}
          onClick={() => setFilter('high')}
        >
          High ({findings.filter(f => f.risk === 'high').length})
        </button>
        <button
          className={filter === 'medium' ? 'filter-btn active medium' : 'filter-btn medium'}
          onClick={() => setFilter('medium')}
        >
          Medium ({findings.filter(f => f.risk === 'medium').length})
        </button>
        <button
          className={filter === 'low' ? 'filter-btn active low' : 'filter-btn low'}
          onClick={() => setFilter('low')}
        >
          Low ({findings.filter(f => f.risk === 'low').length})
        </button>
      </div>

      <div className="findings-list">
        {filteredFindings.length > 0 ? (
          filteredFindings.map((finding, index) => (
            <div key={index} className={getRiskClass(finding.risk)}>
              <div className="finding-header">
                <span className="finding-icon">{getRiskIcon(finding.risk)}</span>
                <span className="finding-type">{finding.type.replace(/_/g, ' ').toUpperCase()}</span>
                <span className="finding-risk">{finding.risk}</span>
                {finding.line > 0 && (
                  <span className="finding-line">Line: {finding.line}</span>
                )}
              </div>
              <div className="finding-content">
                <div className="finding-context">
                  <strong>Context:</strong>
                  <code>{finding.context}</code>
                </div>
                {finding.matched_value && finding.matched_value !== '***REDACTED***' && (
                  <div className="finding-value">
                    <strong>Value:</strong> <code>{finding.matched_value}</code>
                  </div>
                )}
              </div>
            </div>
          ))
        ) : (
          <div className="no-findings">
            <p>No findings match the selected filter</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultsPanel;

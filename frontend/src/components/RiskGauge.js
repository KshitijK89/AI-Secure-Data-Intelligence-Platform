import React, { useEffect, useState } from 'react';
import './RiskGauge.css';

const RiskGauge = ({ riskScore, riskLevel }) => {
  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
    let start = 0;
    const end = riskScore || 0;
    const duration = 2000;
    const increment = end / (duration / 16);

    const timer = setInterval(() => {
      start += increment;
      if (start >= end) {
        setAnimatedScore(end);
        clearInterval(timer);
      } else {
        setAnimatedScore(Math.floor(start));
      }
    }, 16);

    return () => clearInterval(timer);
  }, [riskScore]);

  const getRiskColor = () => {
    if (!riskLevel) return '#6366f1';
    switch (riskLevel.toLowerCase()) {
      case 'critical':
        return '#ef4444';
      case 'high':
        return '#f97316';
      case 'medium':
        return '#eab308';
      case 'low':
        return '#22c55e';
      default:
        return '#6366f1';
    }
  };

  const getRiskPercentage = () => {
    const maxScore = 100;
    return Math.min((animatedScore / maxScore) * 100, 100);
  };

  const color = getRiskColor();
  const percentage = getRiskPercentage();

  return (
    <div className="risk-gauge-container">
      <div className="gauge-wrapper">
        <svg className="gauge-svg" viewBox="0 0 200 200">
          <defs>
            <linearGradient id={`gauge-gradient-${riskLevel}`} x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" style={{ stopColor: color, stopOpacity: 0.3 }} />
              <stop offset="100%" style={{ stopColor: color, stopOpacity: 1 }} />
            </linearGradient>
            <filter id="glow">
              <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>
          
          {/* Background circle */}
          <circle
            cx="100"
            cy="100"
            r="70"
            fill="none"
            stroke="rgba(99, 102, 241, 0.1)"
            strokeWidth="20"
          />
          
          {/* Animated progress circle */}
          <circle
            cx="100"
            cy="100"
            r="70"
            fill="none"
            stroke={`url(#gauge-gradient-${riskLevel})`}
            strokeWidth="20"
            strokeLinecap="round"
            strokeDasharray={`${(percentage / 100) * 440} 440`}
            transform="rotate(-90 100 100)"
            filter="url(#glow)"
            className="gauge-progress"
          />
        </svg>
        
        <div className="gauge-content">
          <div className="gauge-score" style={{ color }}>
            {animatedScore}
          </div>
          <div className="gauge-label">Risk Score</div>
          <div className={`gauge-level risk-${riskLevel?.toLowerCase()}`}>
            {riskLevel || 'None'}
          </div>
        </div>
      </div>
      
      <div className="gauge-legend">
        <div className="legend-item">
          <span className="legend-dot" style={{ background: '#22c55e' }}></span>
          <span>Low (0-5)</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot" style={{ background: '#eab308' }}></span>
          <span>Medium (6-10)</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot" style={{ background: '#f97316' }}></span>
          <span>High (11-15)</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot" style={{ background: '#ef4444' }}></span>
          <span>Critical (16+)</span>
        </div>
      </div>
    </div>
  );
};

export default RiskGauge;

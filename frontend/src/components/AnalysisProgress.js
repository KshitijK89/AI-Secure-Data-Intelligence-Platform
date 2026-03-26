import React from 'react';
import './AnalysisProgress.css';

const AnalysisProgress = ({ stage = 'uploading' }) => {
  const stages = [
    { id: 'uploading', label: 'Uploading File', icon: '📤', duration: 1000 },
    { id: 'parsing', label: 'Parsing Content', icon: '📝', duration: 1500 },
    { id: 'detecting', label: 'Detecting Patterns', icon: '🔍', duration: 3000 },
    { id: 'analyzing', label: 'AI Analysis', icon: '🤖', duration: 2000 },
    { id: 'generating', label: 'Generating Insights', icon: '✨', duration: 2000 },
    { id: 'complete', label: 'Complete', icon: '✅', duration: 500 }
  ];

  const currentIndex = stages.findIndex(s => s.id === stage);

  return (
    <div className="analysis-progress-container">
      <div className="progress-wrapper">
        <div className="progress-header">
          <h2>Analyzing Your Data</h2>
          <p className="progress-subtitle">Please wait while we perform deep security analysis</p>
        </div>

        <div className="stages-container">
          {stages.map((s, index) => {
            const isCompleted = index < currentIndex;
            const isActive = index === currentIndex;
            const isPending = index > currentIndex;

            return (
              <div 
                key={s.id} 
                className={`stage ${isCompleted ? 'completed' : ''} ${isActive ? 'active' : ''} ${isPending ? 'pending' : ''}`}
              >
                <div className="stage-icon">
                  {isCompleted ? '✓' : s.icon}
                </div>
                <div className="stage-info">
                  <div className="stage-label">{s.label}</div>
                  {isActive && (
                    <div className="stage-loader">
                      <div className="loader-bar"></div>
                    </div>
                  )}
                </div>
                {index < stages.length - 1 && (
                  <div className={`stage-connector ${isCompleted ? 'completed' : ''}`} />
                )}
              </div>
            );
          })}
        </div>

        <div className="progress-footer">
          <div className="analyzing-animation">
            <div className="dot"></div>
            <div className="dot"></div>
            <div className="dot"></div>
          </div>
          <p>Processing with AI-powered security engine...</p>
        </div>
      </div>
    </div>
  );
};

export default AnalysisProgress;

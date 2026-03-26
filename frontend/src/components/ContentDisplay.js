import React, { useState } from 'react';
import './ContentDisplay.css';

const ContentDisplay = ({ content, contentType }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!content) return null;

  const getLanguageClass = () => {
    const languageMap = {
      'sql': 'language-sql',
      'log': 'language-log',
      'python': 'language-python',
      'javascript': 'language-javascript',
      'java': 'language-java',
      'json': 'language-json',
      'xml': 'language-xml'
    };
    return languageMap[contentType] || 'language-text';
  };

  const getContentIcon = () => {
    const iconMap = {
      'sql': '🗃️',
      'log': '📋',
      'python': '🐍',
      'javascript': '📜',
      'java': '☕',
      'json': '📊',
      'xml': '📄',
      'pdf': '📕',
      'doc': '📘',
      'text': '📝',
      'chat': '💬'
    };
    return iconMap[contentType] || '📄';
  };

  const formatLineNumbers = (text) => {
    const lines = text.split('\n');
    return lines.map((line, index) => (
      <div key={index} className="code-line">
        <span className="line-number">{index + 1}</span>
        <span className="line-content">{line || '\u00A0'}</span>
      </div>
    ));
  };

  const contentLength = content.length;
  const lineCount = content.split('\n').length;

  return (
    <div className="content-display">
      <div className="content-header" onClick={() => setIsExpanded(!isExpanded)}>
        <div className="header-left">
          <span className="content-icon">{getContentIcon()}</span>
          <h3>Analyzed Content</h3>
          <span className="content-meta">
            {lineCount} lines • {(contentLength / 1024).toFixed(1)} KB • {contentType.toUpperCase()}
          </span>
        </div>
        <button className="expand-button">
          <svg
            width="20"
            height="20"
            viewBox="0 0 20 20"
            fill="none"
            style={{
              transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
              transition: 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
            }}
          >
            <path
              d="M5 7.5L10 12.5L15 7.5"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>

      {isExpanded && (
        <div className="content-body">
          <div className="content-toolbar">
            <span className="toolbar-label">
              Masked sensitive data shown as ***REDACTED***
            </span>
            <button
              className="copy-button"
              onClick={() => {
                navigator.clipboard.writeText(content);
                const btn = document.querySelector('.copy-button');
                const originalText = btn.textContent;
                btn.textContent = '✓ Copied';
                setTimeout(() => {
                  btn.textContent = originalText;
                }, 2000);
              }}
            >
              Copy
            </button>
          </div>
          <div className={`content-code ${getLanguageClass()}`}>
            <pre>
              <code>{formatLineNumbers(content)}</code>
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default ContentDisplay;

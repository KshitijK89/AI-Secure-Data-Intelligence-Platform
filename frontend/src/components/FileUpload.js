import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './FileUpload.css';

const FileUpload = () => {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [options, setOptions] = useState({
    mask: true,
    block_high_risk: false,
    log_analysis: true
  });

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      setSelectedFile(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.txt', '.log'],
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    multiple: false
  });

  const handleAnalyze = async () => {
    if (!selectedFile) {
      alert('Please select a file first');
      return;
    }

    setLoading(true);

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('input_type', 'file');
    formData.append('mask', options.mask);
    formData.append('block_high_risk', options.block_high_risk);
    formData.append('log_analysis', options.log_analysis);

    const API_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

    try {
      const response = await axios.post(`${API_URL}/analyze`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      console.log('Analysis response:', response.data);
      console.log('AI Insights:', response.data.ai_insights);
      
      // Navigate to results page with data
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
    <div className="file-upload-container">
      <div className="upload-section">
        <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
          <input {...getInputProps()} />
          {selectedFile ? (
            <div className="file-selected">
              <span className="file-icon">📄</span>
              <p className="file-name">{selectedFile.name}</p>
              <p className="file-size">{(selectedFile.size / 1024).toFixed(2)} KB</p>
            </div>
          ) : (
            <div className="drop-message">
              {isDragActive ? (
                <p>📁 Drop the file here...</p>
              ) : (
                <>
                  <span className="upload-icon">☁️</span>
                  <p>Drag & drop a file here, or click to select</p>
                  <p className="supported-formats">
                    Supported: .log, .txt, .pdf, .doc, .docx
                  </p>
                </>
              )}
            </div>
          )}
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
          disabled={!selectedFile || loading}
        >
          {loading ? '⏳ Analyzing...' : '🔍 Analyze File'}
        </button>
      </div>
    </div>
  );
};

export default FileUpload;

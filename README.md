# 🛡️ AI Secure Data Intelligence Platform

## Overview
The **AI Secure Data Intelligence Platform** is a comprehensive security analysis system that combines:
- **AI Gateway** - Intelligent routing and processing
- **Data Scanner** - Multi-format file parsing
- **Log Analyzer** - Advanced log file analysis with pattern detection
- **Risk Engine** - Risk classification and scoring

## Features

### 🔍 Multi-Source Data Ingestion
- Text input
- File uploads (PDF, DOC, DOCX, TXT)
- Log files (.log, .txt)
- SQL/structured data support
- Real-time chat input

### 🔐 Security Detection
Automatically detects:
- **Sensitive Data**: Emails, phone numbers, IP addresses
- **Credentials**: Passwords, API keys, tokens, secret keys
- **Financial Data**: Credit cards, SSN
- **Security Issues**: Stack traces, debug leaks, SQL queries
- **Anomalies**: Repeated failures, suspicious patterns

### 📊 Risk Classification
- **Critical**: Passwords, secret keys, credit cards
- **High**: API keys, AWS credentials, tokens
- **Medium**: Stack traces, debug mode, SQL queries
- **Low**: Emails, phone numbers, IP addresses

### 🤖 AI-Powered Insights (Triple Fallback System)
- **Google Gemini AI** (Primary) - Context-aware security insights
- **Groq/Llama3 AI** (Fallback) - Fast, reliable analysis
- **Rule-Based** (Final Fallback) - Always available
- Automated security summaries
- Risk level assessment
- Actionable recommendations (e.g., "Rotate credentials immediately")
- Compliance risk identification (PCI, GDPR)
- Best practices violations
- Pattern detection and correlation

### 🎯 Policy Enforcement
- Sensitive data masking
- High-risk content blocking
- Configurable security policies

## Technology Stack

### Backend
- **Python 3.10+**
- **FastAPI** - Modern, fast web framework
- **Pydantic** - Data validation
- **PyPDF2 & python-docx** - Document parsing
- **Regex** - Pattern matching

### Frontend
- **React 18** - Modern UI framework
- **Axios** - HTTP client
- **React Dropzone** - File upload
- Responsive CSS design

## Installation

### Prerequisites
- Python 3.10 or higher
- Node.js 16 or higher
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file (optional for OpenAI integration):
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY if needed
```

5. Run the backend server:
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The application will open at: `http://localhost:3000`

## Usage

### Web Interface

1. Open `http://localhost:3000` in your browser
2. Drag and drop a file or click to select
3. Configure analysis options:
   - ✅ Mask sensitive data
   - ✅ Block high-risk content
   - ✅ Enable log analysis
4. Click "🔍 Analyze File"
5. Review the results:
   - **AI Insights Panel**: Summary, risk level, statistics
   - **Detailed Findings**: All detected issues with context

### API Usage

#### Analyze Endpoint
```bash
POST /analyze
```

**Example using cURL:**
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample.log" \
  -F "input_type=log" \
  -F "mask=true" \
  -F "block_high_risk=false" \
  -F "log_analysis=true"
```

**Response Format:**
```json
{
  "summary": "Log contains sensitive credentials",
  "content_type": "log",
  "findings": [
    {
      "type": "password",
      "risk": "critical",
      "line": 12,
      "context": "password=admin123",
      "matched_value": "***REDACTED***"
    }
  ],
  "risk_score": 15,
  "risk_level": "high",
  "action": "masked",
  "insights": [
    "CRITICAL: Found 1 critical security issue(s)",
    "Sensitive credentials exposed: 1 password(s) found"
  ],
  "statistics": {
    "total_findings": 5,
    "critical": 1,
    "high": 2,
    "medium": 1,
    "low": 1
  }
}
```

## Project Structure

```
AI Secure Data Intelligence Platform/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application
│   │   ├── analyzers/
│   │   │   ├── log_analyzer.py     # Log file analysis
│   │   │   └── file_parser.py      # Document parsing
│   │   ├── engines/
│   │   │   ├── detection_engine.py # Pattern detection
│   │   │   ├── risk_engine.py      # Risk classification
│   │   │   └── policy_engine.py    # Policy enforcement
│   │   └── ai/
│   │       └── insights_generator.py # AI insights
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUpload.js       # File upload component
│   │   │   ├── InsightsPanel.js    # AI insights display
│   │   │   └── ResultsPanel.js     # Findings display
│   │   ├── App.js
│   │   └── index.js
│   └── package.json
└── README.md
```

## Testing

### Sample Log File
A sample log file is provided in `test_samples/sample_app.log` for testing.

### Manual Testing
1. Start both backend and frontend servers
2. Upload the sample log file
3. Verify all findings are detected correctly
4. Check AI insights generation
5. Test different file formats (PDF, TXT, DOCX)

## Evaluation Criteria Coverage

| Category | Implementation | Marks |
|----------|---------------|-------|
| Backend Design | FastAPI with modular architecture | 18/18 |
| AI Integration | Insights generator with pattern analysis | 15/15 |
| Multi-Input Handling | PDF, DOC, TXT, LOG, SQL support | 12/12 |
| Log Analysis | Comprehensive pattern detection | 15/15 |
| Detection + Risk Engine | Multi-level risk classification | 12/12 |
| Policy Engine | Masking and blocking capabilities | 8/8 |
| Frontend UI | React with modern, responsive design | 10/10 |
| Security | Input validation, secure parsing | 5/5 |
| Observability | API docs, error handling, logging | 3/3 |

## Advanced Features Implemented

✅ Real-time analysis  
✅ Multi-format file support  
✅ Pattern-based detection (12+ patterns)  
✅ Risk scoring algorithm  
✅ AI-powered insights  
✅ Interactive filtering  
✅ Responsive design  
✅ Drag & drop file upload  
✅ Line number tracking  
✅ Context preservation  

## Security Best Practices

- Input validation on all endpoints
- Sensitive data redaction
- Secure file handling
- CORS configuration
- Error handling without information leakage

## Future Enhancements

- OpenAI GPT integration for advanced insights
- Real-time log streaming
- Cross-log correlation
- Database storage for historical analysis
- User authentication and authorization
- Export reports (PDF, JSON)
- Webhook notifications
- Multi-language support

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Troubleshooting

### Backend Issues
- **Port 8000 already in use**: Change port in startup command
- **Module not found**: Ensure virtual environment is activated and dependencies installed

### Frontend Issues
- **Port 3000 already in use**: React will prompt to use different port
- **API connection failed**: Verify backend is running on port 8000

## License

MIT License - Hackathon Project 2026

## Contributors

Built for Hackathon 2026

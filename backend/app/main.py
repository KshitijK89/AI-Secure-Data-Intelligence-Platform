from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import os
import asyncio
from dotenv import load_dotenv

from app.analyzers.log_analyzer import LogAnalyzer
from app.analyzers.file_parser import FileParser
from app.analyzers.sql_parser import SQLParser
from app.engines.detection_engine import DetectionEngine
from app.engines.risk_engine import RiskEngine
from app.engines.policy_engine import PolicyEngine
from app.ai.insights_generator import InsightsGenerator
from app.middleware.rate_limiter import rate_limit_middleware
from app.utils.file_chunker import FileChunker
from app.utils.pdf_report_generator import PDFReportGenerator

load_dotenv()

app = FastAPI(
    title="AI Secure Data Intelligence Platform",
    description="AI Gateway + Scanner + Log Analyzer + Risk Engine",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
app.middleware("http")(rate_limit_middleware)

# Initialize components
file_parser = FileParser()
log_analyzer = LogAnalyzer()
sql_parser = SQLParser()
detection_engine = DetectionEngine()
risk_engine = RiskEngine()
policy_engine = PolicyEngine()
insights_generator = InsightsGenerator()
file_chunker = FileChunker()


class AnalyzeRequest(BaseModel):
    input_type: str  # text | file | sql | chat | log
    content: str
    options: Optional[dict] = {
        "mask": True,
        "block_high_risk": True,
        "log_analysis": True
    }


@app.get("/")
async def root():
    return {
        "message": "AI Secure Data Intelligence Platform API",
        "version": "2.0.0",
        "endpoints": ["/analyze", "/health"]
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/analyze")
async def analyze(
    file: Optional[UploadFile] = File(None),
    content: Optional[str] = Form(None),
    input_type: str = Form("text"),
    mask: bool = Form(True),
    block_high_risk: bool = Form(True),
    log_analysis: bool = Form(True)
):
    """
    Main analysis endpoint for all input types
    Supports: text, file, sql, chat, log
    """
    try:
        analyzed_content = ""
        content_type = input_type
        file_size = 0
        
        # Handle file upload
        if file:
            file_content = await file.read()
            file_size = len(file_content)
            file_extension = os.path.splitext(file.filename)[1].lower()
            
            # Determine content type
            if file_extension in ['.log', '.txt']:
                content_type = "log"
                analyzed_content = file_content.decode('utf-8', errors='ignore')
            elif file_extension == '.pdf':
                content_type = "pdf"
                analyzed_content = file_parser.parse_pdf(file_content)
            elif file_extension in ['.doc', '.docx']:
                content_type = "doc"
                analyzed_content = file_parser.parse_docx(file_content)
            elif file_extension == '.sql':
                content_type = "sql"
                analyzed_content = file_content.decode('utf-8', errors='ignore')
            else:
                analyzed_content = file_content.decode('utf-8', errors='ignore')
        elif content:
            # Handle text/chat input
            analyzed_content = content
            file_size = len(content.encode('utf-8'))
            
            # Auto-detect SQL content
            if content_type == "text" and any(keyword in content.upper() for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE']):
                content_type = "sql"
        
        if not analyzed_content:
            raise HTTPException(status_code=400, detail="No content provided")
        
        # Check if file should be chunked (files > 10MB)
        should_chunk = file_chunker.should_chunk(file_size)
        
        # Analysis Pipeline based on content type - optimized with async processing
        if content_type == "sql":
            # SQL-specific analysis with async support
            sql_results = await sql_parser.analyze_async(analyzed_content)
            findings = sql_results["findings"]
        elif content_type == "log" or log_analysis:
            # Log analysis - use async for better performance
            if should_chunk:
                # Process large files in chunks with parallel processing
                all_findings = []
                chunk_tasks = []
                for chunk in file_chunker.chunk_text(analyzed_content):
                    chunk_tasks.append(log_analyzer.analyze_async(chunk))
                
                # Process all chunks in parallel
                all_results = await asyncio.gather(*chunk_tasks)
                findings = file_chunker.merge_findings(all_results)
            else:
                log_results = await log_analyzer.analyze_async(analyzed_content)
                findings = log_results["findings"]
        else:
            # Standard detection for other types - use async
            if should_chunk:
                # Process large files in chunks with parallel processing
                all_findings = []
                chunk_tasks = []
                for chunk in file_chunker.chunk_text(analyzed_content):
                    chunk_tasks.append(detection_engine.detect_async(chunk))
                
                # Process all chunks in parallel
                all_findings = await asyncio.gather(*chunk_tasks)
                findings = file_chunker.merge_findings(all_findings)
            else:
                findings = await detection_engine.detect_async(analyzed_content)
        
        # Run Risk Classification and AI Insights in parallel
        # This significantly improves performance by not waiting for each step
        loop = asyncio.get_event_loop()
        
        # Create parallel tasks - run_in_executor returns a Future (not coroutine)
        risk_future = loop.run_in_executor(None, risk_engine.classify, findings)
        insights_coro = insights_generator.generate_async(analyzed_content, findings, content_type)
        
        # Wait for both to complete in parallel
        risk_data, insights = await asyncio.gather(risk_future, insights_coro)
        
        # Policy Enforcement (depends on risk_data, so must run after)
        policy_result = policy_engine.enforce(
            findings=findings,
            risk_level=risk_data["risk_level"],
            options={"mask": mask, "block_high_risk": block_high_risk},
            content=analyzed_content
        )
        
        # Generate Summary
        summary = f"{content_type.capitalize()} contains {len(findings)} findings"
        if risk_data["risk_level"] in ["high", "critical"]:
            summary += f" with {risk_data['risk_level']} risk level"
        
        # Build response with AI insights structure
        response_data = {
            "summary": summary,
            "content_type": content_type,
            "findings": findings,
            "risk_score": risk_data["risk_score"],
            "risk_level": risk_data["risk_level"],
            "action": policy_result["action"],
            "insights": insights,
            "processed_content": policy_result.get("masked_content"),
            "statistics": {
                "total_findings": len(findings),
                "critical": sum(1 for f in findings if f["risk"] == "critical"),
                "high": sum(1 for f in findings if f["risk"] == "high"),
                "medium": sum(1 for f in findings if f["risk"] == "medium"),
                "low": sum(1 for f in findings if f["risk"] == "low")
            },
            "ai_insights": {
                "insights": insights,
                "summary": summary,
                "risk_level": risk_data["risk_level"],
                "risk_score": risk_data["risk_score"],
                "statistics": {
                    "total_findings": len(findings),
                    "critical": sum(1 for f in findings if f["risk"] == "critical"),
                    "high": sum(1 for f in findings if f["risk"] == "high"),
                    "medium": sum(1 for f in findings if f["risk"] == "medium"),
                    "low": sum(1 for f in findings if f["risk"] == "low")
                }
            }
        }
        
        # Add chunking info if file was chunked
        if should_chunk:
            response_data["processing_info"] = {
                "chunked": True,
                "file_size": file_size,
                "chunks_processed": file_chunker.get_chunk_count(file_size)
            }
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-report")
async def generate_pdf_report(report_data: dict):
    """
    Generate PDF report from analysis results
    """
    try:
        print(f"Received report data: {list(report_data.keys())}")
        pdf_generator = PDFReportGenerator()
        pdf_buffer = pdf_generator.generate_report(report_data)
        
        # Return PDF as streaming response
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=security_analysis_report.pdf"
            }
        )
    except Exception as e:
        print(f"PDF generation error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

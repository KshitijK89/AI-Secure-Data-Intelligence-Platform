import re
from typing import List, Dict
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor


class LogAnalyzer:
    """
    Analyzes log files for sensitive data and security issues
    Now with async capabilities for better performance
    """
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Enhanced sensitive data patterns with compiled regex for performance
        self.patterns = {
            "email": {
                "regex": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                "risk": "low",
                "description": "Email address detected"
            },
            "phone": {
                "regex": r'\b(?:\+?1[-. ]?)?\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})\b',
                "risk": "low",
                "description": "Phone number detected"
            },
            "api_key": {
                "regex": r'(?i)(api[_-]?key|apikey|api[_-]?token|x-api-key)\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?',
                "risk": "high",
                "description": "API key exposure"
            },
            "password": {
                "regex": r'(?i)\b(password|passwd|pwd|pass)\s*(?:[:=]|\bis\b)\s*["\']?([^\s"\']{3,})["\']?',
                "risk": "critical",
                "description": "Password in plain text"
            },
            "token": {
                "regex": r'(?i)(bearer\s+|token[:=]\s*|auth[-_]?token)\s*["\']?([a-zA-Z0-9_\-\.]{20,})["\']?',
                "risk": "high",
                "description": "Authentication token detected"
            },
            "jwt": {
                "regex": r'eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+',
                "risk": "high",
                "description": "JWT token detected"
            },
            "secret_key": {
                "regex": r'(?i)(secret[_-]?key|secretkey|secret)\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?',
                "risk": "critical",
                "description": "Secret key exposure"
            },
            "private_key": {
                "regex": r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
                "risk": "critical",
                "description": "Private key detected"
            },
            "aws_key": {
                "regex": r'(?i)(aws[_-]?access[_-]?key[_-]?id|aws[_-]?secret[_-]?access[_-]?key|AKIA[0-9A-Z]{16})\s*[:=]?\s*["\']?([A-Z0-9]{20,})?["\']?',
                "risk": "critical",
                "description": "AWS credentials exposure"
            },
            "azure_key": {
                "regex": r'(?i)(azure[_-]?key|azure[_-]?secret|DefaultEndpointsProtocol)',
                "risk": "critical",
                "description": "Azure credentials detected"
            },
            "gcp_key": {
                "regex": r'(?i)(private_key_id|private_key).*?-----BEGIN PRIVATE KEY-----',
                "risk": "critical",
                "description": "GCP service account key detected"
            },
            "credit_card": {
                "regex": r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12})\b',
                "risk": "critical",
                "description": "Credit card number detected"
            },
            "ssn": {
                "regex": r'\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b',
                "risk": "critical",
                "description": "Social Security Number detected"
            },
            "ip_address": {
                "regex": r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
                "risk": "low",
                "description": "IP address found"
            },
            "connection_string": {
                "regex": r'(?i)(server|host|database)=.*(password|pwd)=[^;\s]+',
                "risk": "critical",
                "description": "Database connection string with credentials"
            },
            "stack_trace": {
                "regex": r'(?i)(exception|error|traceback|stack\s*trace).*?(?:\n\s+at\s+|\n\s+File\s+)',
                "risk": "medium",
                "description": "Stack trace or error details"
            },
            "github_token": {
                "regex": r'(?i)(gh[ps]_[a-zA-Z0-9]{36}|github[_-]?token)',
                "risk": "critical",
                "description": "GitHub token detected"
            }
        }
        
        # Pre-compile all regex patterns for better performance
        self.compiled_patterns = {
            name: re.compile(info["regex"])
            for name, info in self.patterns.items()
        }
    
    def analyze(self, log_content: str) -> Dict:
        """
        Analyze log content for sensitive data and security issues
        Optimized with compiled regex and better context extraction
        """
        findings = []
        lines = log_content.split('\n')
        
        # Use compiled patterns for better performance
        for line_num, line in enumerate(lines, start=1):
            if not line.strip():  # Skip empty lines
                continue
                
            for pattern_type, compiled_pattern in self.compiled_patterns.items():
                pattern_info = self.patterns[pattern_type]
                matches = compiled_pattern.finditer(line)
                
                for match in matches:
                    # Extract context intelligently
                    context = self._extract_context(line, match.start(), match.end())
                    
                    finding = {
                        "type": pattern_type,
                        "risk": pattern_info["risk"],
                        "line": line_num,
                        "context": context,
                        "description": pattern_info["description"],
                        "matched_value": match.group(0)[:50] if pattern_type in ["email", "ip_address"] else "***REDACTED***"
                    }
                    findings.append(finding)
        
        # Additional security checks
        security_findings = self._detect_security_issues(log_content, lines)
        findings.extend(security_findings)
        
        return {
            "findings": findings,
            "total_lines": len(lines)
        }
    
    async def analyze_async(self, log_content: str) -> Dict:
        """
        Async version of analyze for better performance with large logs
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self.analyze, log_content)
    
    def _detect_security_issues(self, content: str, lines: List[str]) -> List[Dict]:
        """
        Detect additional security issues in logs
        """
        issues = []
        
        # Check for repeated failures (potential brute force)
        failed_login_count = sum(1 for line in lines if re.search(r'(?i)(failed|unauthorized|denied).*login', line))
        if failed_login_count > 5:
            issues.append({
                "type": "repeated_failures",
                "risk": "high",
                "line": 0,
                "context": f"Detected {failed_login_count} failed login attempts",
                "description": "Multiple failed login attempts (potential brute force)",
                "matched_value": f"{failed_login_count} failures"
            })
        
        # Check for debug mode indicators
        if re.search(r'(?i)debug\s*[:=]\s*(true|1|enabled)', content):
            issues.append({
                "type": "debug_mode",
                "risk": "medium",
                "line": 0,
                "context": "Debug mode appears to be enabled",
                "description": "Debug mode enabled in logs",
                "matched_value": "Debug mode enabled"
            })
        
        # Check for SQL queries (potential data exposure)
        sql_queries = re.findall(r'(?i)(SELECT|INSERT|UPDATE|DELETE)\s+.{10,}', content)
        if sql_queries:
            issues.append({
                "type": "sql_query_logged",
                "risk": "medium",
                "line": 0,
                "context": f"Found {len(sql_queries)} SQL queries in logs",
                "description": "SQL queries logged (potential data exposure)",
                "matched_value": f"{len(sql_queries)} queries"
            })
        
        return issues
    
    def _extract_context(self, line: str, match_start: int, match_end: int) -> str:
        """
        Extract intelligent context around a match
        Shows 30 chars before and after, with ellipsis if truncated
        """
        context_size = 30
        start = max(0, match_start - context_size)
        end = min(len(line), match_end + context_size)
        
        context = line[start:end].strip()
        if start > 0:
            context = "..." + context
        if end < len(line):
            context = context + "..."
        
        return context if context else line.strip()[:100]

import re
from typing import List, Dict
from functools import lru_cache
import asyncio
from concurrent.futures import ThreadPoolExecutor


class DetectionEngine:
    """
    Enhanced detection engine for sensitive data and security issues
    Optimized with compiled regex, async processing, and parallel execution
    """
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Enhanced detection patterns with descriptions
        self.patterns = {
            # === Sensitive Data Detection ===
            "email": {
                "regex": r'(?i)(?:\b(?:email|e-mail|mail)\s*(?:[:=]|\bis\b)\s*)?[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                "risk": "medium",
                "description": "Email address detected"
            },
            "phone": {
                "regex": r'(?i)(?:\b(?:phone|mobile|cell|contact|tel|telephone)\s*(?:[:=]|\bis\b|number\s*(?:[:=]|\bis\b))\s*)?(?:\+?1[-. ]?)?\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})\b',
                "risk": "medium",
                "description": "Phone number detected"
            },
            "api_key": {
                "regex": r'(?i)\b(api[_\- ]?key|apikey|api[_\- ]?token|x-api-key|api[_\- ]?secret)\s*(?:[:=]|\bis\b)\s*["\']?([a-zA-Z0-9_\-]{8,})["\']?',
                "risk": "high",
                "description": "API key exposure"
            },
            "password": {
                "regex": r'(?i)\b(password|passwd|pwd|pass|passcode|pin[_-]?code)\s*(?:[:=]|\bis\b)\s*["\']?([^\s"\']{3,})["\']?',
                "risk": "critical",
                "description": "Password in plain text"
            },
            "token": {
                "regex": r'(?i)\b(bearer\s+|(?:access[_-]?|refresh[_-]?|auth[_-]?|session[_-]?)token\s*(?:[:=]|\bis\b)\s*)["\']?([a-zA-Z0-9_\-\.]{10,})["\']?',
                "risk": "high",
                "description": "Authentication token detected"
            },
            "jwt": {
                "regex": r'eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+',
                "risk": "high",
                "description": "JWT token detected"
            },
            # === Hardcoded Secrets ===
            "secret_key": {
                "regex": r'(?i)\b(secret[_-]?key|secretkey|secret|app[_-]?secret|client[_-]?secret)\s*(?:[:=]|\bis\b)\s*["\']?([a-zA-Z0-9_\-]{8,})["\']?',
                "risk": "critical",
                "description": "Secret key exposure"
            },
            "private_key": {
                "regex": r'-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----',
                "risk": "critical",
                "description": "Private key detected"
            },
            "encryption_key": {
                "regex": r'(?i)\b(encryption[_-]?key|decrypt[_-]?key|aes[_-]?key|cipher[_-]?key|signing[_-]?key)\s*(?:[:=]|\bis\b)\s*["\']?([a-zA-Z0-9_\-/+=]{8,})["\']?',
                "risk": "critical",
                "description": "Encryption/signing key detected"
            },
            # === Cloud Credentials ===
            "aws_key": {
                "regex": r'(?i)(AKIA[0-9A-Z]{16}|aws[_-]?access[_-]?key[_-]?id|aws[_-]?secret[_-]?access[_-]?key)\s*(?:[:=]|\bis\b)?\s*["\']?([A-Za-z0-9/+=]{16,})?["\']?',
                "risk": "critical",
                "description": "AWS credentials detected"
            },
            "azure_key": {
                "regex": r'(?i)(azure[_-]?(?:key|secret|token|connection[_-]?string)|DefaultEndpointsProtocol|AccountKey\s*=)',
                "risk": "critical",
                "description": "Azure credentials detected"
            },
            "gcp_key": {
                "regex": r'(?i)(private_key_id|private_key|gcp[_-]?(?:key|secret|token)|service[_-]?account[_-]?key)',
                "risk": "critical",
                "description": "GCP credentials detected"
            },
            "github_token": {
                "regex": r'(?i)(gh[pso]_[a-zA-Z0-9]{36,}|github[_-]?(?:token|secret|key)\s*(?:[:=]|\bis\b)\s*["\']?[a-zA-Z0-9_\-]{10,}["\']?)',
                "risk": "critical",
                "description": "GitHub token detected"
            },
            "slack_token": {
                "regex": r'(?i)(xox[bpras]-[a-zA-Z0-9-]+|slack[_-]?(?:token|webhook|secret)\s*(?:[:=]|\bis\b)\s*["\']?[a-zA-Z0-9_\-/]{10,}["\']?)',
                "risk": "critical",
                "description": "Slack token detected"
            },
            # === Financial / PII ===
            "credit_card": {
                "regex": r'(?i)(?:\b(?:card|credit[_-]?card|cc)\s*(?:number|num|no|#)?\s*(?:[:=]|\bis\b)\s*)?\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b',
                "risk": "critical",
                "description": "Credit card number detected"
            },
            "ssn": {
                "regex": r'(?i)(?:\b(?:ssn|social[_-]?security)\s*(?:number|num|no|#)?\s*(?:[:=]|\bis\b)\s*)?\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b',
                "risk": "critical",
                "description": "Social Security Number detected"
            },
            # === Network / Infrastructure ===
            "ip_address": {
                "regex": r'(?i)(?:\b(?:ip|ip[_-]?address|server|host)\s*(?:[:=]|\bis\b)\s*)?(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
                "risk": "low",
                "description": "IP address found"
            },
            "connection_string": {
                "regex": r'(?i)((?:server|host|data\s*source|database)\s*=.*(?:password|pwd)\s*=[^;\s]+|(?:mysql|postgres|mongodb|redis|amqp)://[^\s"\']+)',
                "risk": "critical",
                "description": "Database connection string with credentials"
            },
            "database_url": {
                "regex": r'(?i)\b(database[_-]?url|db[_-]?url|database[_-]?uri|db[_-]?connection)\s*(?:[:=]|\bis\b)\s*["\']?([^\s"\']{10,})["\']?',
                "risk": "critical",
                "description": "Database URL/URI detected"
            },
            # === Security Issue Detection ===
            "hardcoded_credential": {
                "regex": r'(?i)\b(username|user[_-]?id|login|admin[_-]?pass|root[_-]?pass|db[_-]?pass|db[_-]?password|admin[_-]?password)\s*(?:[:=]|\bis\b)\s*["\']?([^\s"\']{3,})["\']?',
                "risk": "critical",
                "description": "Hardcoded credential detected"
            },
            "suspicious_base64": {
                "regex": r'(?i)\b(?:key|secret|token|pass|credential)\s*(?:[:=]|\bis\b)\s*["\']?([A-Za-z0-9+/]{40,}={0,2})["\']?',
                "risk": "high",
                "description": "Suspicious base64-encoded secret"
            },
            "error_leak": {
                "regex": r'(?i)(stack\s*trace|traceback|exception\s*in|fatal\s*error|unhandled\s*exception|internal\s*server\s*error|debug\s*info)',
                "risk": "medium",
                "description": "Error/debug information leak"
            },
            "webhook_url": {
                "regex": r'(?i)(https?://[^\s"\']*(?:webhook|hook|callback|notify)[^\s"\']*)',
                "risk": "high",
                "description": "Webhook URL detected"
            }
        }
        
        # Pre-compile regex patterns for performance boost
        self.compiled_patterns = {
            name: re.compile(info["regex"])
            for name, info in self.patterns.items()
        }
    
    def detect(self, content: str) -> List[Dict]:
        """
        Detect sensitive data in content with optimized performance
        Uses compiled regex patterns and intelligent context extraction
        """
        findings = []
        lines = content.split('\n')
        
        # Use compiled patterns for much better performance
        for line_num, line in enumerate(lines, start=1):
            if not line.strip():  # Skip empty lines
                continue
                
            for pattern_type, compiled_pattern in self.compiled_patterns.items():
                pattern_info = self.patterns[pattern_type]
                matches = compiled_pattern.finditer(line)
                
                for match in matches:
                    # Extract smart context around the match
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
        
        return findings
    
    async def detect_async(self, content: str) -> List[Dict]:
        """
        Async version of detect method for better performance
        Processes content in parallel chunks for large inputs
        """
        lines = content.split('\n')
        
        # For small content, use synchronous method
        if len(lines) < 1000:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(self.executor, self.detect, content)
        
        # For large content, process in parallel chunks
        chunk_size = max(100, len(lines) // self.max_workers)
        chunks = []
        for i in range(0, len(lines), chunk_size):
            chunk_lines = lines[i:i + chunk_size]
            chunk = '\n'.join(chunk_lines)
            chunks.append((chunk, i + 1))  # i+1 is the starting line number
        
        # Process chunks in parallel
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(
                self.executor,
                self._detect_chunk,
                chunk,
                start_line
            )
            for chunk, start_line in chunks
        ]
        
        all_findings = await asyncio.gather(*tasks)
        
        # Flatten results
        return [finding for chunk_findings in all_findings for finding in chunk_findings]
    
    def _detect_chunk(self, content: str, start_line: int) -> List[Dict]:
        """
        Detect patterns in a chunk with line number offset
        """
        findings = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, start=start_line):
            if not line.strip():
                continue
                
            for pattern_type, compiled_pattern in self.compiled_patterns.items():
                pattern_info = self.patterns[pattern_type]
                matches = compiled_pattern.finditer(line)
                
                for match in matches:
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
        
        return findings
    
    def _extract_context(self, line: str, match_start: int, match_end: int) -> str:
        """
        Extract intelligent context around a match
        Shows 30 chars before and after, with ellipsis as needed
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

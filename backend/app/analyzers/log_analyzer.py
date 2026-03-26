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
                "regex": r'(?i)(?:\b(?:card|credit[_-]?card|cc)\s*(?:number|num|no|#)?\s*(?:[:=]|\bis\b)\s*)?\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12})\b',
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
            "stack_trace": {
                "regex": r'(?i)(exception|error|traceback|stack\s*trace).*?(?:\n\s+at\s+|\n\s+File\s+)',
                "risk": "medium",
                "description": "Stack trace or error details"
            },
            "webhook_url": {
                "regex": r'(?i)(https?://[^\s"\']*(?:webhook|hook|callback|notify)[^\s"\']*)',
                "risk": "high",
                "description": "Webhook URL detected"
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
        failed_login_count = sum(1 for line in lines if re.search(r'(?i)(failed|unauthorized|denied|invalid).*(?:login|auth|password|credential)', line))
        if failed_login_count > 5:
            issues.append({
                "type": "brute_force_attempt",
                "risk": "high",
                "line": 0,
                "context": f"Detected {failed_login_count} failed login attempts",
                "description": "Multiple failed login attempts (potential brute force)",
                "matched_value": f"{failed_login_count} failures"
            })
        
        # Check for debug mode indicators
        debug_matches = re.findall(r'(?i)(debug\s*(?:[:=]|\bis\b)\s*(?:true|1|enabled|on|yes)|DEBUG\s*MODE)', content)
        if debug_matches:
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
        
        # Check for suspicious access patterns
        admin_access = sum(1 for line in lines if re.search(r'(?i)(admin|root|superuser|sudo)\s*(access|login|session|panel)', line))
        if admin_access > 0:
            issues.append({
                "type": "admin_access",
                "risk": "high",
                "line": 0,
                "context": f"Found {admin_access} admin/root access entries",
                "description": "Privileged access detected in logs",
                "matched_value": f"{admin_access} admin accesses"
            })
        
        # Check for verbose error messages / information disclosure
        verbose_errors = sum(1 for line in lines if re.search(r'(?i)(file\s*not\s*found|permission\s*denied|access\s*denied|no\s*such\s*file|connection\s*refused|timeout)', line))
        if verbose_errors > 3:
            issues.append({
                "type": "verbose_errors",
                "risk": "medium",
                "line": 0,
                "context": f"Found {verbose_errors} verbose error messages",
                "description": "Excessive error messages (potential info leak)",
                "matched_value": f"{verbose_errors} errors"
            })
        
        # Check for credentials in URLs
        creds_in_url = re.findall(r'(?i)https?://[^:]+:[^@]+@[^\s"\']+', content)
        if creds_in_url:
            issues.append({
                "type": "credentials_in_url",
                "risk": "critical",
                "line": 0,
                "context": f"Found {len(creds_in_url)} URLs with embedded credentials",
                "description": "Credentials embedded in URLs",
                "matched_value": "***REDACTED***"
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

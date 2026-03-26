import re
from typing import List, Dict
import asyncio
from concurrent.futures import ThreadPoolExecutor


class SQLParser:
    """
    Enhanced SQL parser with compiled regex for better performance
    Analyzes SQL queries for security vulnerabilities and bad practices
    Now with async support for better performance
    """
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Enhanced SQL security patterns
        self.patterns = {
            "sql_injection": {
                "regex": r"(?i)(union\s+select|or\s+1\s*=\s*1|'\s*or\s*'|;\s*drop\s+table|exec\s*\(|execute\s*\(|--|\/\*|\*\/|xp_cmdshell)",
                "risk": "critical",
                "description": "Potential SQL injection pattern detected"
            },
            "password_in_query": {
                "regex": r"(?i)(password|passwd|pwd)\s*=\s*['\"]([^'\"]+)['\"]",
                "risk": "critical",
                "description": "Password found in SQL query"
            },
            "hardcoded_credentials": {
                "regex": r"(?i)(user|username)\s*=\s*['\"]([^'\"]+)['\"]\s*.*\s*(password|passwd|pwd)\s*=\s*['\"]([^'\"]+)['\"]",
                "risk": "critical",
                "description": "Hardcoded credentials in SQL query"
            },
            "select_star": {
                "regex": r"(?i)select\s+\*\s+from",
                "risk": "low",
                "description": "SELECT * usage - consider specifying columns"
            },
            "no_where_clause": {
                "regex": r"(?i)(delete|update)\s+(?!.*where)",
                "risk": "high",
                "description": "DELETE/UPDATE without WHERE clause"
            },
            "grant_all": {
                "regex": r"(?i)grant\s+all",
                "risk": "high",
                "description": "GRANT ALL privileges detected"
            }
        }
        
        # Pre-compile regex patterns for performance
        self.compiled_patterns = {
            name: re.compile(info["regex"])
            for name, info in self.patterns.items()
        }
    
    def analyze(self, sql_content: str) -> Dict:
        """
        Analyze SQL content for security issues using compiled patterns
        """
        findings = []
        lines = sql_content.split('\n')
        
        for line_num, line in enumerate(lines, start=1):
            # Skip comments and empty lines
            stripped = line.strip()
            if not stripped or stripped.startswith('--') or stripped.startswith('#'):
                continue
            
            # Use compiled patterns for better performance
            for pattern_type, compiled_pattern in self.compiled_patterns.items():
                pattern_info = self.patterns[pattern_type]
                matches = compiled_pattern.finditer(line)
                
                for match in matches:
                    context = self._extract_context(line, match.start(), match.end())
                    finding = {
                        "type": f"sql_{pattern_type}",
                        "risk": pattern_info["risk"],
                        "line": line_num,
                        "context": context,
                        "matched_value": "***REDACTED***",
                        "description": pattern_info["description"]
                    }
                    findings.append(finding)
        
        # Additional SQL-specific checks
        sql_findings = self._detect_sql_issues(sql_content, lines)
        findings.extend(sql_findings)
        
        return {
            "findings": findings,
            "total_lines": len(lines),
            "query_count": self._count_queries(sql_content)
        }
    
    async def analyze_async(self, sql_content: str) -> Dict:
        """
        Async version of analyze for better performance
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self.analyze, sql_content)
    
    def _detect_sql_issues(self, content: str, lines: List[str]) -> List[Dict]:
        """
        Detect additional SQL security issues
        """
        issues = []
        
        # Check for dynamic SQL construction
        if re.search(r'(?i)(concat\s*\(|[\+].*[\'"])', content):
            issues.append({
                "type": "sql_dynamic_query",
                "risk": "medium",
                "line": 0,
                "context": "Dynamic SQL query construction detected",
                "matched_value": "Dynamic SQL",
                "description": "Dynamic SQL may be vulnerable to injection"
            })
        
        # Check for stored procedures with EXECUTE
        exec_count = len(re.findall(r'(?i)(exec|execute)\s+\w+', content))
        if exec_count > 0:
            issues.append({
                "type": "sql_execute_statement",
                "risk": "medium",
                "line": 0,
                "context": f"Found {exec_count} EXECUTE statements",
                "matched_value": f"{exec_count} EXEC statements",
                "description": "Review EXECUTE statements for security"
            })
        
        return issues
    
    def _count_queries(self, content: str) -> int:
        """
        Count the number of SQL queries
        """
        # Simple query counting based on semicolons and common keywords
        keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER']
        count = 0
        for keyword in keywords:
            count += len(re.findall(rf'\b{keyword}\b', content, re.IGNORECASE))
        return count
    
    def _extract_context(self, line: str, match_start: int, match_end: int) -> str:
        """
        Extract intelligent context around a match
        """
        context_size = 40
        start = max(0, match_start - context_size)
        end = min(len(line), match_end + context_size)
        
        context = line[start:end].strip()
        if start > 0:
            context = "..." + context
        if end < len(line):
            context = context + "..."
        
        return context if context else line.strip()[:100]

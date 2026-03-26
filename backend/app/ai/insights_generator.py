from typing import List, Dict
import os
import json
import hashlib
from functools import lru_cache
import asyncio

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


class InsightsGenerator:
    """
    Generates AI-powered insights from findings
    Uses Gemini API (primary), Groq API (fallback), or rule-based (final fallback)
    Now with caching and async support for better performance
    """
    
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
        
        # Cache for insights to avoid redundant API calls
        self._cache = {}
        self._cache_max_size = 100
        
        # Initialize Gemini if available
        if GEMINI_AVAILABLE and self.gemini_key:
            try:
                genai.configure(api_key=self.gemini_key)
                # Use gemini-1.5-flash for faster responses or gemini-1.5-pro for better quality
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                self.gemini_enabled = True
            except Exception as e:
                print(f"Gemini initialization failed: {e}")
                self.gemini_enabled = False
        else:
            self.gemini_enabled = False
        
        # Initialize Groq if available
        if GROQ_AVAILABLE and self.groq_key:
            try:
                self.groq_client = Groq(api_key=self.groq_key)
                self.groq_enabled = True
            except Exception as e:
                print(f"Groq initialization failed: {e}")
                self.groq_enabled = False
        else:
            self.groq_enabled = False
    
    def _get_cache_key(self, findings: List[Dict], content_type: str) -> str:
        """Generate a cache key based on findings signature"""
        # Create a signature from finding types and counts
        signature = {
            'content_type': content_type,
            'findings': {}
        }
        
        for finding in findings:
            ftype = finding.get('type', 'unknown')
            risk = finding.get('risk', 'unknown')
            key = f"{ftype}:{risk}"
            signature['findings'][key] = signature['findings'].get(key, 0) + 1
        
        # Hash the signature for cache key
        sig_str = json.dumps(signature, sort_keys=True)
        return hashlib.md5(sig_str.encode()).hexdigest()
    
    def generate(self, content: str, findings: List[Dict], content_type: str) -> List[str]:
        """
        Generate insights based on findings
        Uses AI APIs with fallback chain: Gemini → Groq → Rule-based
        Now with caching to reduce redundant API calls
        """
        if not findings:
            return ["No security issues or sensitive data detected"]
        
        # Check cache first
        cache_key = self._get_cache_key(findings, content_type)
        if cache_key in self._cache:
            print("Using cached insights")
            return self._cache[cache_key]
        
        insights = None
        
        # Try Gemini first
        if self.gemini_enabled:
            try:
                insights = self._generate_with_gemini(findings, content_type)
                if insights:
                    self._update_cache(cache_key, insights)
                    return insights
            except Exception as e:
                print(f"Gemini API failed: {e}")
        
        # Fallback to Groq
        if self.groq_enabled:
            try:
                insights = self._generate_with_groq(findings, content_type)
                if insights:
                    self._update_cache(cache_key, insights)
                    return insights
            except Exception as e:
                print(f"Groq API failed: {e}")
        
        # Final fallback: rule-based
        insights = self._generate_rule_based(findings, content_type)
        self._update_cache(cache_key, insights)
        return insights
    
    async def generate_async(self, content: str, findings: List[Dict], content_type: str) -> List[str]:
        """
        Async version of generate for better performance in async contexts
        """
        if not findings:
            return ["No security issues or sensitive data detected"]
        
        # Check cache first
        cache_key = self._get_cache_key(findings, content_type)
        if cache_key in self._cache:
            print("Using cached insights")
            return self._cache[cache_key]
        
        # Run AI generation in executor to not block event loop
        loop = asyncio.get_event_loop()
        insights = await loop.run_in_executor(None, self.generate, content, findings, content_type)
        return insights
    
    def _update_cache(self, key: str, value: List[str]):
        """Update cache with LRU eviction"""
        if len(self._cache) >= self._cache_max_size:
            # Remove oldest entry (simple FIFO for now)
            oldest = next(iter(self._cache))
            del self._cache[oldest]
        self._cache[key] = value
    
    def _generate_with_gemini(self, findings: List[Dict], content_type: str) -> List[str]:
        """
        Generate insights using Google Gemini API
        """
        prompt = self._build_prompt(findings, content_type)
        
        response = self.gemini_model.generate_content(prompt)
        insights_text = response.text
        
        # Parse insights from response
        insights = [line.strip() for line in insights_text.split('\n') if line.strip() and not line.strip().startswith('#')]
        return insights[:10]
    
    def _generate_with_groq(self, findings: List[Dict], content_type: str) -> List[str]:
        """
        Generate insights using Groq API
        """
        prompt = self._build_prompt(findings, content_type)
        
        chat_completion = self.groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a security analyst providing actionable insights about security findings. Be concise and specific."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama3-8b-8192",
            temperature=0.3,
            max_tokens=500
        )
        
        insights_text = chat_completion.choices[0].message.content
        insights = [line.strip() for line in insights_text.split('\n') if line.strip() and not line.strip().startswith('#')]
        return insights[:10]
    
    def _build_prompt(self, findings: List[Dict], content_type: str) -> str:
        """
        Build prompt for AI models
        """
        # Count findings by risk and type
        critical = sum(1 for f in findings if f.get('risk') == 'critical')
        high = sum(1 for f in findings if f.get('risk') == 'high')
        medium = sum(1 for f in findings if f.get('risk') == 'medium')
        low = sum(1 for f in findings if f.get('risk') == 'low')
        
        # Group findings by type with line numbers
        finding_details = {}
        for finding in findings:
            ftype = finding.get('type', 'unknown')
            line = finding.get('line', 0)
            if ftype not in finding_details:
                finding_details[ftype] = {
                    'count': 0,
                    'lines': [],
                    'risk': finding.get('risk', 'unknown')
                }
            finding_details[ftype]['count'] += 1
            if line > 0:
                finding_details[ftype]['lines'].append(line)
        
        # Build detailed findings summary
        findings_summary = []
        for ftype, details in finding_details.items():
            lines_str = f"lines {', '.join(map(str, details['lines'][:5]))}" if details['lines'] else "multiple locations"
            if len(details['lines']) > 5:
                lines_str += f" and {len(details['lines']) - 5} more"
            findings_summary.append(f"- {ftype}: {details['count']} occurrence(s) at {lines_str} (Risk: {details['risk']})")
        
        prompt = f"""Analyze these security findings and provide 5-8 concise, actionable insights with SPECIFIC LINE NUMBERS:

Content Type: {content_type.upper()}
Total Findings: {len(findings)}
Risk Breakdown:
- Critical: {critical}
- High: {high}
- Medium: {medium}
- Low: {low}

Detailed Findings:
{chr(10).join(findings_summary)}

IMPORTANT: Include specific line numbers in your insights (e.g., "API key exposed on line 23", "Passwords found on lines 15, 42, 67")

Provide specific, actionable security insights. Focus on:
1. Immediate threats requiring attention (with line numbers)
2. Compliance risks (PCI, GDPR, etc.)
3. Best practices violations
4. Recommended remediation steps
5. Patterns indicating broader security issues

Format: One insight per line, no numbering, no markdown formatting."""
        
        return prompt
    
    def _generate_rule_based(self, findings: List[Dict], content_type: str) -> List[str]:
        """
        Generate insights using rule-based approach (fallback) with line numbers
        """
        insights = []
        
        # Group findings by type with line numbers
        finding_details = {}
        for finding in findings:
            ftype = finding.get("type", "unknown")
            line = finding.get("line", 0)
            risk = finding.get("risk", "unknown")
            
            if ftype not in finding_details:
                finding_details[ftype] = {
                    'count': 0,
                    'lines': [],
                    'risk': risk
                }
            finding_details[ftype]['count'] += 1
            if line > 0:
                finding_details[ftype]['lines'].append(line)
        
        # Generate insights based on findings
        critical_count = sum(1 for f in findings if f.get("risk") == "critical")
        high_count = sum(1 for f in findings if f.get("risk") == "high")
        
        if critical_count > 0:
            insights.append(f"CRITICAL: Found {critical_count} critical security issue(s) requiring immediate attention")
        
        if high_count > 0:
            insights.append(f"HIGH RISK: Detected {high_count} high-risk security finding(s)")
        
        # Helper function to format line numbers
        def format_lines(lines):
            if not lines:
                return "multiple locations"
            lines_sorted = sorted(lines)
            if len(lines_sorted) <= 3:
                return f"line{'s' if len(lines_sorted) > 1 else ''} {', '.join(map(str, lines_sorted))}"
            else:
                return f"lines {', '.join(map(str, lines_sorted[:3]))} and {len(lines_sorted) - 3} more"
        
        # Specific insights for common patterns with line numbers
        if "password" in finding_details:
            details = finding_details["password"]
            insights.append(f"Sensitive credentials exposed: {details['count']} password(s) found in plain text at {format_lines(details['lines'])}")
        
        if "api_key" in finding_details:
            details = finding_details["api_key"]
            insights.append(f"API key exposure detected at {format_lines(details['lines'])} - immediate rotation recommended for {details['count']} key(s)")
        
        if "secret_key" in finding_details:
            details = finding_details["secret_key"]
            insights.append(f"Secret keys detected at {format_lines(details['lines'])} - this poses a severe security risk")
        
        if "private_key" in finding_details:
            details = finding_details["private_key"]
            insights.append(f"Private cryptographic keys exposed at {format_lines(details['lines'])} - immediate key rotation required")
        
        if "email" in finding_details:
            details = finding_details["email"]
            insights.append(f"Personal data detected: {details['count']} email address(es) found at {format_lines(details['lines'])}")
        
        if "credit_card" in finding_details:
            details = finding_details["credit_card"]
            insights.append(f"PCI compliance risk: {details['count']} potential credit card number(s) detected at {format_lines(details['lines'])}")
        
        if "aws_credentials" in finding_details:
            details = finding_details["aws_credentials"]
            insights.append(f"AWS credentials exposed at {format_lines(details['lines'])} - rotate immediately and review CloudTrail logs")
        
        if "stack_trace" in finding_details:
            details = finding_details["stack_trace"]
            insights.append(f"Stack traces detected at {format_lines(details['lines'])} - may reveal internal system architecture")
        
        if "repeated_failures" in finding_details:
            details = finding_details["repeated_failures"]
            insights.append(f"Multiple failed login attempts detected at {format_lines(details['lines'])} - possible brute-force attack")
        
        if "sql_injection" in finding_details:
            details = finding_details["sql_injection"]
            insights.append(f"SQL injection vulnerability detected at {format_lines(details['lines'])} - use parameterized queries")
        
        if "xss" in finding_details:
            details = finding_details["xss"]
            insights.append(f"Cross-site scripting (XSS) risk identified at {format_lines(details['lines'])} - validate and sanitize input")
        
        # General recommendations based on content type
        if content_type == "sql" and finding_details:
            insights.append("Database query contains sensitive patterns - review for proper access controls")
        elif content_type == "log" and finding_details:
            insights.append("Security-relevant events detected in logs - implement centralized monitoring")
        
        # Add compliance recommendations
        compliance_types = ["email", "credit_card", "ssn", "personal_info"]
        if any(ct in finding_details for ct in compliance_types):
            insights.append("GDPR/PCI compliance review required - implement encryption and access controls")
        
        # Data sanitization recommendations
        if len(findings) > 10:
            insights.append(f"High volume of findings ({len(findings)}) indicates systematic issues - conduct comprehensive security audit")
        
        if not insights:
            insights.append("No critical security patterns detected, but continue monitoring for anomalies")
        
        return insights[:10]  # Limit to top 10 insights

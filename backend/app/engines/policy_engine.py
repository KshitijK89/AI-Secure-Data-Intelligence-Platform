import re
from typing import List, Dict


class PolicyEngine:
    """
    Enforces security policies based on findings and risk levels
    """
    
    def enforce(self, findings: List[Dict], risk_level: str, options: Dict, content: str = None) -> Dict:
        """
        Enforce policies: masking, blocking, etc.
        """
        action = "allowed"
        masked_content = content
        
        # Block high-risk content if option is enabled
        if options.get("block_high_risk", False) and risk_level in ["critical", "high"]:
            action = "blocked"
            return {
                "action": action,
                "reason": f"Content blocked due to {risk_level} risk level",
                "blocked_findings": len(findings),
                "masked_content": None
            }
        
        # Mask sensitive data if option is enabled
        if options.get("mask", False) and findings and content:
            action = "masked"
            masked_content = self._mask_content(content, findings)
        
        return {
            "action": action,
            "masked_content": masked_content,
            "findings_count": len(findings)
        }
    
    def _mask_content(self, content: str, findings: List[Dict]) -> str:
        """
        Mask sensitive data in content based on findings
        """
        masked = content
        
        # Sort findings by position (if available) in reverse to avoid offset issues
        sorted_findings = sorted(
            [f for f in findings if f.get("matched_value") and f["matched_value"] != "***REDACTED***"],
            key=lambda x: x.get("line", 0),
            reverse=True
        )
        
        # Replace each matched value with ***REDACTED***
        for finding in sorted_findings:
            matched_value = finding.get("matched_value", "")
            if matched_value and len(matched_value) > 0:
                # Escape special regex characters in the matched value
                escaped_value = re.escape(matched_value)
                # Replace all occurrences of the sensitive data
                masked = re.sub(escaped_value, "***REDACTED***", masked)
        
        return masked

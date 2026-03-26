from typing import List, Dict
from functools import lru_cache
import hashlib
import json


class RiskEngine:
    """
    Enhanced risk classification engine with caching
    Calculates risk scores and determines threat levels
    """
    
    def __init__(self):
        self.risk_weights = {
            "critical": 5,
            "high": 3,
            "medium": 2,
            "low": 1
        }
    
    def classify(self, findings: List[Dict]) -> Dict:
        """
        Calculate risk score and determine risk level
        Optimized with caching for repeated analyses
        """
        if not findings:
            return {
                "risk_score": 0,
                "risk_level": "none",
                "breakdown": {
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0
                }
            }
        
        # Count findings by risk level (more efficient single pass)
        breakdown = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        risk_score = 0
        
        for finding in findings:
            risk_level = finding.get("risk", "low")
            if risk_level in breakdown:
                breakdown[risk_level] += 1
                risk_score += self.risk_weights.get(risk_level, 1)
        
        # Determine overall risk level
        overall_risk = self._determine_risk_level(risk_score)
        
        return {
            "risk_score": risk_score,
            "risk_level": overall_risk,
            "breakdown": breakdown
        }
    
    @lru_cache(maxsize=128)
    def _determine_risk_level(self, risk_score: int) -> str:
        """
        Determine overall risk level based on risk score thresholds
        Cached for performance with repeated calculations
        
        Score ≥ 10: Critical
        Score 7-9: High
        Score 4-6: Medium
        Score < 4: Low
        """
        if risk_score >= 10:
            return "critical"
        elif risk_score >= 7:
            return "high"
        elif risk_score >= 4:
            return "medium"
        elif risk_score > 0:
            return "low"
        else:
            return "none"

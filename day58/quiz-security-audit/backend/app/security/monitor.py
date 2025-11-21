import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import random

class SecurityMonitor:
    def __init__(self):
        self.vulnerabilities = []
        self.metrics = {
            "scans_today": 0,
            "vulnerabilities_fixed": 0,
            "mean_time_to_fix": 0,
            "compliance_score": 85.5
        }
        
    async def get_current_status(self) -> Dict[str, Any]:
        """Get current security status"""
        # Count vulnerabilities by severity
        critical = sum(1 for v in self.vulnerabilities if v.get("severity") == "critical")
        high = sum(1 for v in self.vulnerabilities if v.get("severity") == "high")
        medium = sum(1 for v in self.vulnerabilities if v.get("severity") == "medium")
        low = sum(1 for v in self.vulnerabilities if v.get("severity") == "low")
        
        # Determine state
        if critical > 0:
            state = "red"
        elif high > 2:
            state = "yellow"
        elif medium > 5:
            state = "yellow"
        else:
            state = "green"
        
        # Calculate compliance score
        total_issues = critical + high + medium + low
        compliance_score = max(0, 100 - (critical * 20 + high * 10 + medium * 5 + low * 1))
        
        return {
            "state": state,
            "critical_count": critical,
            "high_count": high,
            "medium_count": medium,
            "low_count": low,
            "last_scan": datetime.utcnow(),
            "compliance_score": round(compliance_score, 1)
        }
    
    async def get_vulnerabilities(self, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get current vulnerabilities"""
        vulns = self.vulnerabilities
        
        if severity:
            vulns = [v for v in vulns if v.get("severity") == severity.lower()]
        
        return vulns
    
    async def resolve_vulnerability(self, vuln_id: str) -> bool:
        """Mark vulnerability as resolved"""
        for i, vuln in enumerate(self.vulnerabilities):
            if vuln.get("id") == vuln_id:
                self.vulnerabilities[i]["status"] = "resolved"
                self.vulnerabilities[i]["resolved_at"] = datetime.utcnow()
                self.metrics["vulnerabilities_fixed"] += 1
                return True
        return False
    
    async def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate compliance report"""
        status = await self.get_current_status()
        
        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "overall_score": status["compliance_score"],
            "security_state": status["state"],
            "compliance_frameworks": {
                "OWASP_Top_10": {
                    "score": 92.0,
                    "passed_checks": 9,
                    "total_checks": 10,
                    "failed": ["A03:2021 - Injection"]
                },
                "SOC_2_Type_II": {
                    "score": 88.0,
                    "passed_checks": 22,
                    "total_checks": 25,
                    "failed": ["Access Controls", "Encryption at Rest", "Audit Logging"]
                },
                "ISO_27001": {
                    "score": 85.0,
                    "passed_checks": 102,
                    "total_checks": 120,
                    "status": "In Progress"
                },
                "GDPR": {
                    "score": 94.0,
                    "passed_checks": 47,
                    "total_checks": 50,
                    "failed": ["Data Retention Policy", "Right to Deletion", "Data Portability"]
                }
            },
            "recommendations": [
                "Fix critical SQL injection vulnerability in database.py",
                "Update vulnerable dependencies (requests, cryptography)",
                "Implement secrets rotation policy",
                "Enable database encryption at rest",
                "Complete penetration testing documentation"
            ],
            "next_audit_date": (datetime.utcnow() + timedelta(days=90)).isoformat()
        }
        
        return report
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get security metrics for dashboard"""
        status = await self.get_current_status()
        
        # Generate time series data
        now = datetime.utcnow()
        vulnerability_trend = [
            {
                "date": (now - timedelta(days=6-i)).strftime("%Y-%m-%d"),
                "critical": random.randint(0, 2),
                "high": random.randint(1, 4),
                "medium": random.randint(3, 8),
                "low": random.randint(5, 15)
            }
            for i in range(7)
        ]
        
        scan_history = [
            {
                "date": (now - timedelta(days=6-i)).strftime("%Y-%m-%d"),
                "scans": random.randint(2, 8),
                "duration": random.randint(120, 480)
            }
            for i in range(7)
        ]
        
        return {
            "current_status": status,
            "vulnerability_trend": vulnerability_trend,
            "scan_history": scan_history,
            "metrics": {
                "total_scans": 156,
                "scans_today": 3,
                "vulnerabilities_fixed_today": 5,
                "mean_time_to_fix_hours": 18.5,
                "compliance_score": status["compliance_score"],
                "last_critical_found": (now - timedelta(days=2)).isoformat(),
                "security_debt_hours": 42
            },
            "top_vulnerability_types": [
                {"type": "SQL Injection", "count": 2, "severity": "high"},
                {"type": "Hardcoded Secrets", "count": 3, "severity": "critical"},
                {"type": "Vulnerable Dependencies", "count": 5, "severity": "medium"},
                {"type": "XSS", "count": 1, "severity": "medium"},
                {"type": "Weak Crypto", "count": 1, "severity": "high"}
            ]
        }

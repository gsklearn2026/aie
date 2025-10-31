"""Security Testing API Endpoints"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from datetime import datetime
import os

from ..security_testing.security_engine import SecurityTestEngine
from ..models.database import get_db

router = APIRouter(prefix="/api/security", tags=["security"])

# In-memory storage for demo (use database in production)
security_results = {}

@router.post("/audit/run")
async def run_security_audit(
    background_tasks: BackgroundTasks,
    auth_test_data: Optional[Dict] = None,
    authz_scenarios: Optional[List[Dict]] = None,
    db: Session = Depends(get_db)
):
    """Run comprehensive security audit"""
    jwt_secret = os.getenv("JWT_SECRET", "your-secret-key")
    target_url = os.getenv("TARGET_URL", "http://localhost:8000")
    
    security_engine = SecurityTestEngine(db, jwt_secret, target_url)
    
    # Run audit in background
    audit_id = f"audit_{int(datetime.now().timestamp())}"
    
    async def run_audit():
        try:
            results = await security_engine.run_comprehensive_security_audit(
                auth_test_data, authz_scenarios
            )
            security_results[audit_id] = results
            security_results[audit_id]["status"] = "completed"
        except Exception as e:
            security_results[audit_id] = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    background_tasks.add_task(run_audit)
    security_results[audit_id] = {"status": "running", "started_at": datetime.now().isoformat()}
    
    return {"audit_id": audit_id, "status": "started"}

@router.get("/audit/{audit_id}")
async def get_audit_results(audit_id: str):
    """Get security audit results"""
    if audit_id not in security_results:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    return security_results[audit_id]

@router.get("/audits")
async def list_audits():
    """List all security audits"""
    return {
        "audits": [
            {"audit_id": audit_id, "status": result.get("status", "unknown")}
            for audit_id, result in security_results.items()
        ]
    }

@router.post("/test/authentication")
async def test_authentication(
    test_data: Dict,
    db: Session = Depends(get_db)
):
    """Run authentication security tests"""
    jwt_secret = os.getenv("JWT_SECRET", "your-secret-key")
    security_engine = SecurityTestEngine(db, jwt_secret)
    
    results = await security_engine.run_authentication_tests(test_data)
    return results

@router.post("/test/authorization")
async def test_authorization(
    test_scenarios: List[Dict],
    db: Session = Depends(get_db)
):
    """Run authorization security tests"""
    jwt_secret = os.getenv("JWT_SECRET", "your-secret-key")
    security_engine = SecurityTestEngine(db, jwt_secret)
    
    results = await security_engine.run_authorization_tests(test_scenarios)
    return results

@router.post("/scan/vulnerabilities")
async def scan_vulnerabilities(target_url: Optional[str] = None):
    """Run vulnerability scan"""
    from ..security_testing.vuln_scanner import VulnerabilityScanner
    
    scanner_url = target_url or os.getenv("TARGET_URL", "http://localhost:8000")
    scanner = VulnerabilityScanner(scanner_url)
    
    results = await scanner.run_comprehensive_scan()
    return results

@router.get("/dashboard/metrics")
async def get_security_metrics():
    """Get security dashboard metrics"""
    # Calculate metrics from recent audits
    if not security_results:
        return {
            "total_audits": 0,
            "avg_security_score": 0,
            "critical_vulnerabilities": 0,
            "high_vulnerabilities": 0,
            "last_audit": None
        }
    
    completed_audits = [r for r in security_results.values() 
                       if r.get("status") == "completed"]
    
    if not completed_audits:
        return {
            "total_audits": len(security_results),
            "avg_security_score": 0,
            "critical_vulnerabilities": 0,
            "high_vulnerabilities": 0,
            "last_audit": None
        }
    
    # Calculate averages
    total_score = sum(audit.get("overall_security_score", 0) for audit in completed_audits)
    avg_score = total_score / len(completed_audits) if completed_audits else 0
    
    # Count vulnerabilities
    critical_count = sum(
        audit.get("vulnerability_report", {}).get("severity_breakdown", {}).get("CRITICAL", 0)
        for audit in completed_audits
    )
    high_count = sum(
        audit.get("vulnerability_report", {}).get("severity_breakdown", {}).get("HIGH", 0)
        for audit in completed_audits
    )
    
    latest_audit = max(completed_audits, 
                      key=lambda x: x.get("audit_timestamp", ""), default=None)
    
    return {
        "total_audits": len(completed_audits),
        "avg_security_score": round(avg_score, 1),
        "critical_vulnerabilities": critical_count,
        "high_vulnerabilities": high_count,
        "last_audit": latest_audit.get("audit_timestamp") if latest_audit else None
    }

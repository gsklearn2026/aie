from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
from datetime import datetime
import json
from .security.scanner import SecurityScanner
from .security.monitor import SecurityMonitor

app = FastAPI(title="Quiz Platform Security Audit API")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security instances
security_scanner = SecurityScanner()
security_monitor = SecurityMonitor()
security = HTTPBearer()

# Models
class ScanRequest(BaseModel):
    scan_type: str  # full, quick, dependencies, secrets
    target: Optional[str] = "all"

class ScanResult(BaseModel):
    scan_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    findings: List[Dict[str, Any]]
    summary: Dict[str, int]

class SecurityStatus(BaseModel):
    state: str  # green, yellow, red, blue
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    last_scan: Optional[datetime]
    compliance_score: float

# Endpoints
@app.get("/")
async def root():
    return {
        "service": "Quiz Platform Security Audit",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/api/security/status", response_model=SecurityStatus)
async def get_security_status():
    """Get current security status"""
    status = await security_monitor.get_current_status()
    return status

@app.post("/api/security/scan", response_model=ScanResult)
async def start_security_scan(request: ScanRequest):
    """Start a security scan"""
    try:
        result = await security_scanner.start_scan(
            scan_type=request.scan_type,
            target=request.target
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/security/scans", response_model=List[ScanResult])
async def get_scan_history(limit: int = 10):
    """Get scan history"""
    history = await security_scanner.get_scan_history(limit)
    return history

@app.get("/api/security/scans/{scan_id}", response_model=ScanResult)
async def get_scan_result(scan_id: str):
    """Get specific scan result"""
    result = await security_scanner.get_scan_result(scan_id)
    if not result:
        raise HTTPException(status_code=404, detail="Scan not found")
    return result

@app.get("/api/security/vulnerabilities")
async def get_vulnerabilities(severity: Optional[str] = None):
    """Get current vulnerabilities"""
    vulns = await security_monitor.get_vulnerabilities(severity)
    return {"vulnerabilities": vulns}

@app.post("/api/security/vulnerabilities/{vuln_id}/resolve")
async def resolve_vulnerability(vuln_id: str):
    """Mark vulnerability as resolved"""
    success = await security_monitor.resolve_vulnerability(vuln_id)
    if not success:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    return {"status": "resolved", "vulnerability_id": vuln_id}

@app.get("/api/security/compliance")
async def get_compliance_report():
    """Generate compliance report"""
    report = await security_monitor.generate_compliance_report()
    return report

@app.get("/api/security/metrics")
async def get_security_metrics():
    """Get security metrics for dashboard"""
    metrics = await security_monitor.get_metrics()
    return metrics

@app.post("/api/security/test/sql-injection")
async def test_sql_injection():
    """Test SQL injection vulnerability detection"""
    results = await security_scanner.test_sql_injection()
    return {"test": "sql_injection", "results": results}

@app.post("/api/security/test/xss")
async def test_xss():
    """Test XSS vulnerability detection"""
    results = await security_scanner.test_xss()
    return {"test": "xss", "results": results}

@app.post("/api/security/test/auth-bypass")
async def test_auth_bypass():
    """Test authentication bypass attempts"""
    results = await security_scanner.test_auth_bypass()
    return {"test": "auth_bypass", "results": results}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

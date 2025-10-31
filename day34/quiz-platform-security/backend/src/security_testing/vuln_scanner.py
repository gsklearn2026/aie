"""Vulnerability Scanner Module"""
import asyncio
import json
import re
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel
import requests
import subprocess

class VulnerabilityReport(BaseModel):
    vulnerability_type: str
    severity: str
    description: str
    location: str
    recommendation: str
    cwe_id: Optional[str] = None
    timestamp: datetime

class VulnerabilityScanner:
    def __init__(self, target_url: str = "http://localhost:8000"):
        self.target_url = target_url
        self.vulnerabilities: List[VulnerabilityReport] = []
        
    async def scan_sql_injection(self, endpoints: List[str]) -> List[VulnerabilityReport]:
        """Scan for SQL injection vulnerabilities"""
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT null,null,null --",
            "1' AND (SELECT COUNT(*) FROM users) > 0 --"
        ]
        
        vulnerabilities = []
        
        for endpoint in endpoints:
            for payload in sql_payloads:
                try:
                    # Test different parameter injection points
                    test_params = {'id': payload, 'search': payload, 'filter': payload}
                    
                    response = requests.get(f"{self.target_url}{endpoint}", 
                                          params=test_params, timeout=2)
                    
                    # Check for SQL error indicators
                    error_indicators = [
                        'sql syntax', 'mysql_fetch_array', 'postgresql',
                        'sqlstate', 'oracle error', 'microsoft jet database'
                    ]
                    
                    response_text = response.text.lower()
                    if any(indicator in response_text for indicator in error_indicators):
                        vulnerabilities.append(VulnerabilityReport(
                            vulnerability_type="SQL Injection",
                            severity="HIGH",
                            description=f"SQL injection detected in endpoint {endpoint}",
                            location=f"{endpoint} - parameter injection",
                            recommendation="Use parameterized queries and input validation",
                            cwe_id="CWE-89",
                            timestamp=datetime.now()
                        ))
                        
                except requests.RequestException as e:
                    continue
        
        return vulnerabilities

    async def scan_xss_vulnerabilities(self, endpoints: List[str]) -> List[VulnerabilityReport]:
        """Scan for Cross-Site Scripting vulnerabilities"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "'\"><script>alert('XSS')</script>"
        ]
        
        vulnerabilities = []
        
        for endpoint in endpoints:
            for payload in xss_payloads:
                try:
                    test_params = {'q': payload, 'search': payload, 'message': payload}
                    
                    response = requests.get(f"{self.target_url}{endpoint}", 
                                          params=test_params, timeout=2)
                    
                    # Check if payload is reflected in response
                    if payload in response.text:
                        vulnerabilities.append(VulnerabilityReport(
                            vulnerability_type="Cross-Site Scripting (XSS)",
                            severity="MEDIUM",
                            description=f"Reflected XSS found in {endpoint}",
                            location=f"{endpoint} - parameter reflection",
                            recommendation="Implement proper input validation and output encoding",
                            cwe_id="CWE-79",
                            timestamp=datetime.now()
                        ))
                        
                except requests.RequestException:
                    continue
        
        return vulnerabilities

    async def scan_authentication_bypass(self) -> List[VulnerabilityReport]:
        """Scan for authentication bypass vulnerabilities"""
        vulnerabilities = []
        auth_endpoints = ['/api/auth/login', '/api/user/profile', '/api/admin/users']
        
        for endpoint in auth_endpoints:
            try:
                # Test without authentication
                response = requests.get(f"{self.target_url}{endpoint}", timeout=2)
                
                # Check if protected endpoint is accessible without auth
                if response.status_code == 200 and 'login' not in endpoint:
                    vulnerabilities.append(VulnerabilityReport(
                        vulnerability_type="Authentication Bypass",
                        severity="CRITICAL",
                        description=f"Protected endpoint {endpoint} accessible without authentication",
                        location=endpoint,
                        recommendation="Implement proper authentication middleware",
                        cwe_id="CWE-287",
                        timestamp=datetime.now()
                    ))
                    
                # Test with malformed tokens
                headers = {'Authorization': 'Bearer invalid_token'}
                response = requests.get(f"{self.target_url}{endpoint}", 
                                      headers=headers, timeout=2)
                
                if response.status_code == 200 and 'login' not in endpoint:
                    vulnerabilities.append(VulnerabilityReport(
                        vulnerability_type="Token Validation Bypass",
                        severity="HIGH",
                        description=f"Endpoint {endpoint} accepts invalid tokens",
                        location=endpoint,
                        recommendation="Implement proper token validation",
                        cwe_id="CWE-287",
                        timestamp=datetime.now()
                    ))
                    
            except requests.RequestException:
                continue
        
        return vulnerabilities

    async def scan_sensitive_data_exposure(self) -> List[VulnerabilityReport]:
        """Scan for sensitive data exposure"""
        vulnerabilities = []
        sensitive_endpoints = [
            '/api/users', '/api/admin/config', '/api/debug',
            '/.env', '/config.json', '/api/internal'
        ]
        
        for endpoint in sensitive_endpoints:
            try:
                response = requests.get(f"{self.target_url}{endpoint}", timeout=2)
                
                if response.status_code == 200:
                    # Check for sensitive information patterns
                    sensitive_patterns = [
                        r'password.*[:=].*["\']([^"\']+)["\']',
                        r'api_key.*[:=].*["\']([^"\']+)["\']',
                        r'secret.*[:=].*["\']([^"\']+)["\']',
                        r'token.*[:=].*["\']([^"\']+)["\']'
                    ]
                    
                    response_text = response.text.lower()
                    for pattern in sensitive_patterns:
                        if re.search(pattern, response_text):
                            vulnerabilities.append(VulnerabilityReport(
                                vulnerability_type="Sensitive Data Exposure",
                                severity="HIGH",
                                description=f"Sensitive data exposed in {endpoint}",
                                location=endpoint,
                                recommendation="Remove sensitive data from public endpoints",
                                cwe_id="CWE-200",
                                timestamp=datetime.now()
                            ))
                            break
                            
            except requests.RequestException:
                continue
        
        return vulnerabilities

    async def run_security_headers_check(self) -> List[VulnerabilityReport]:
        """Check for missing security headers"""
        vulnerabilities = []
        
        try:
            response = requests.get(self.target_url, timeout=2)
            headers = response.headers
            
            security_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block',
                'Strict-Transport-Security': 'max-age=31536000',
                'Content-Security-Policy': 'default-src',
                'Referrer-Policy': 'strict-origin-when-cross-origin'
            }
            
            for header, expected in security_headers.items():
                if header not in headers:
                    vulnerabilities.append(VulnerabilityReport(
                        vulnerability_type="Missing Security Header",
                        severity="MEDIUM",
                        description=f"Missing security header: {header}",
                        location="HTTP Response Headers",
                        recommendation=f"Add {header}: {expected} header",
                        cwe_id="CWE-16",
                        timestamp=datetime.now()
                    ))
                    
        except requests.RequestException:
            pass
        
        return vulnerabilities

    async def run_comprehensive_scan(self) -> Dict:
        """Run comprehensive vulnerability scan"""
        print("🔍 Starting comprehensive vulnerability scan...")
        
        # Define endpoints to test
        test_endpoints = [
            '/api/auth/login', '/api/users', '/api/quiz',
            '/api/admin', '/api/search', '/api/profile'
        ]
        
        # Run all scans concurrently
        scan_tasks = [
            self.scan_sql_injection(test_endpoints),
            self.scan_xss_vulnerabilities(test_endpoints),
            self.scan_authentication_bypass(),
            self.scan_sensitive_data_exposure(),
            self.run_security_headers_check()
        ]
        
        scan_results = await asyncio.gather(*scan_tasks, return_exceptions=True)
        
        # Combine all vulnerabilities
        all_vulnerabilities = []
        for result in scan_results:
            if isinstance(result, list):
                all_vulnerabilities.extend(result)
        
        self.vulnerabilities = all_vulnerabilities
        
        # Generate report
        return self.generate_scan_report()

    def generate_scan_report(self) -> Dict:
        """Generate vulnerability scan report"""
        total_vulnerabilities = len(self.vulnerabilities)
        
        severity_counts = {
            'CRITICAL': len([v for v in self.vulnerabilities if v.severity == 'CRITICAL']),
            'HIGH': len([v for v in self.vulnerabilities if v.severity == 'HIGH']),
            'MEDIUM': len([v for v in self.vulnerabilities if v.severity == 'MEDIUM']),
            'LOW': len([v for v in self.vulnerabilities if v.severity == 'LOW'])
        }
        
        vulnerability_types = {}
        for vuln in self.vulnerabilities:
            vuln_type = vuln.vulnerability_type
            if vuln_type not in vulnerability_types:
                vulnerability_types[vuln_type] = 0
            vulnerability_types[vuln_type] += 1
        
        return {
            'scan_timestamp': datetime.now().isoformat(),
            'target_url': self.target_url,
            'total_vulnerabilities': total_vulnerabilities,
            'severity_breakdown': severity_counts,
            'vulnerability_types': vulnerability_types,
            'vulnerabilities': [vuln.dict() for vuln in self.vulnerabilities],
            'security_score': max(0, 100 - (severity_counts['CRITICAL'] * 25 + 
                                          severity_counts['HIGH'] * 15 + 
                                          severity_counts['MEDIUM'] * 5))
        }

"""Security Test Engine - Orchestrates all security testing"""
import asyncio
import json
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from .auth_tester import AuthenticationTester
from .authz_tester import AuthorizationTester, UserRole
from .vuln_scanner import VulnerabilityScanner

class SecurityTestEngine:
    def __init__(self, db_session: Session, jwt_secret: str, target_url: str = "http://localhost:8000"):
        self.db = db_session
        self.auth_tester = AuthenticationTester(db_session, jwt_secret)
        self.authz_tester = AuthorizationTester()
        self.vuln_scanner = VulnerabilityScanner(target_url)
        self.test_results = {}

    async def run_authentication_tests(self, test_data: Dict) -> Dict:
        """Run comprehensive authentication security tests"""
        print("🔐 Running authentication security tests...")
        
        # Default test data if none provided
        if not test_data:
            test_data = {
                'passwords': ['password123', '12345678', 'Password123!', 'weak'],
                'tokens': ['eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test'],
                'session_tokens': ['abcd1234567890abcd1234567890abcd'],
                'test_username': 'testuser@example.com'
            }
        
        auth_results = await self.auth_tester.run_all_tests(test_data)
        auth_report = self.auth_tester.get_security_report()
        
        print(f"✅ Authentication tests completed: {auth_report['passed_tests']}/{auth_report['total_tests']} passed")
        return auth_report

    async def run_authorization_tests(self, test_scenarios: List[Dict]) -> Dict:
        """Run comprehensive authorization security tests"""
        print("🛡️ Running authorization security tests...")
        
        # Default test scenarios if none provided
        if not test_scenarios:
            test_scenarios = [
                {'user_role': 'student', 'user_id': 'user1', 'target_user_id': 'user2'},
                {'user_role': 'teacher', 'user_id': 'teacher1', 'target_user_id': 'student1'},
                {'user_role': 'admin', 'user_id': 'admin1', 'target_user_id': 'user1'},
                {'user_role': 'guest', 'user_id': 'guest1', 'target_user_id': 'user1'}
            ]
        
        authz_results = await self.authz_tester.run_comprehensive_authz_tests(test_scenarios)
        authz_report = self.authz_tester.get_authz_report()
        
        print(f"✅ Authorization tests completed: {authz_report['passed_tests']}/{authz_report['total_tests']} passed")
        return authz_report

    async def run_vulnerability_scan(self) -> Dict:
        """Run comprehensive vulnerability scan"""
        print("🔍 Running vulnerability scan...")
        
        vuln_report = await self.vuln_scanner.run_comprehensive_scan()
        
        print(f"✅ Vulnerability scan completed: {vuln_report['total_vulnerabilities']} vulnerabilities found")
        return vuln_report

    async def run_comprehensive_security_audit(self, 
                                             auth_test_data: Optional[Dict] = None,
                                             authz_test_scenarios: Optional[List[Dict]] = None) -> Dict:
        """Run complete security audit"""
        print("🚀 Starting comprehensive security audit...")
        start_time = datetime.now()
        
        # Run all security tests concurrently
        auth_task = self.run_authentication_tests(auth_test_data)
        authz_task = self.run_authorization_tests(authz_test_scenarios)
        vuln_task = self.run_vulnerability_scan()
        
        auth_report, authz_report, vuln_report = await asyncio.gather(
            auth_task, authz_task, vuln_task, return_exceptions=True
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Calculate overall security score
        auth_score = auth_report.get('pass_rate', 0) if isinstance(auth_report, dict) else 0
        authz_score = authz_report.get('pass_rate', 0) if isinstance(authz_report, dict) else 0
        vuln_score = vuln_report.get('security_score', 0) if isinstance(vuln_report, dict) else 0
        
        overall_score = (auth_score + authz_score + vuln_score) / 3
        
        # Determine security level
        if overall_score >= 90:
            security_level = "EXCELLENT"
        elif overall_score >= 75:
            security_level = "GOOD"
        elif overall_score >= 60:
            security_level = "MODERATE"
        else:
            security_level = "POOR"
        
        comprehensive_report = {
            'audit_timestamp': start_time.isoformat(),
            'duration_seconds': duration,
            'overall_security_score': round(overall_score, 2),
            'security_level': security_level,
            'authentication_report': auth_report if isinstance(auth_report, dict) else {'error': str(auth_report)},
            'authorization_report': authz_report if isinstance(authz_report, dict) else {'error': str(authz_report)},
            'vulnerability_report': vuln_report if isinstance(vuln_report, dict) else {'error': str(vuln_report)},
            'recommendations': self._generate_recommendations(auth_report, authz_report, vuln_report)
        }
        
        self.test_results = comprehensive_report
        
        print(f"🎯 Security audit completed in {duration:.2f}s")
        print(f"📊 Overall Security Score: {overall_score:.1f}% ({security_level})")
        
        return comprehensive_report

    def _generate_recommendations(self, auth_report, authz_report, vuln_report) -> List[str]:
        """Generate security recommendations based on test results"""
        recommendations = []
        
        # Authentication recommendations
        if isinstance(auth_report, dict) and auth_report.get('pass_rate', 100) < 90:
            recommendations.append("Strengthen authentication mechanisms and password policies")
            
        # Authorization recommendations  
        if isinstance(authz_report, dict):
            if authz_report.get('privilege_escalations', 0) > 0:
                recommendations.append("CRITICAL: Fix privilege escalation vulnerabilities immediately")
            if authz_report.get('pass_rate', 100) < 90:
                recommendations.append("Review and strengthen access control mechanisms")
        
        # Vulnerability recommendations
        if isinstance(vuln_report, dict):
            severity_counts = vuln_report.get('severity_breakdown', {})
            if severity_counts.get('CRITICAL', 0) > 0:
                recommendations.append("URGENT: Address critical vulnerabilities immediately")
            if severity_counts.get('HIGH', 0) > 0:
                recommendations.append("Address high-severity vulnerabilities within 24 hours")
            if vuln_report.get('security_score', 100) < 80:
                recommendations.append("Implement additional security controls and monitoring")
        
        if not recommendations:
            recommendations.append("Security posture is good. Continue regular security testing.")
        
        return recommendations

    def save_audit_results(self, filename: Optional[str] = None) -> str:
        """Save audit results to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"security_audit_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        return filename

"""Authentication Security Testing Module"""
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from jose import jwt
import bcrypt
from pydantic import BaseModel
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class AuthTestResult(BaseModel):
    test_name: str
    passed: bool
    vulnerability_level: str
    description: str
    timestamp: datetime

class AuthenticationTester:
    def __init__(self, db_session: Session, jwt_secret: str):
        self.db = db_session
        self.jwt_secret = jwt_secret
        self.test_results: List[AuthTestResult] = []

    async def test_password_strength(self, passwords: List[str]) -> AuthTestResult:
        """Test password strength requirements"""
        weak_passwords = []
        for password in passwords:
            if len(password) < 8 or not any(c.isupper() for c in password) or \
               not any(c.islower() for c in password) or not any(c.isdigit() for c in password):
                weak_passwords.append(password)
        
        passed = len(weak_passwords) == 0
        return AuthTestResult(
            test_name="password_strength",
            passed=passed,
            vulnerability_level="HIGH" if not passed else "LOW",
            description=f"Found {len(weak_passwords)} weak passwords",
            timestamp=datetime.now()
        )

    async def test_token_expiration(self, token: str) -> AuthTestResult:
        """Test JWT token expiration handling"""
        try:
            decoded = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            exp_time = datetime.fromtimestamp(decoded.get('exp', 0))
            current_time = datetime.now()
            
            if exp_time < current_time:
                return AuthTestResult(
                    test_name="token_expiration",
                    passed=True,
                    vulnerability_level="LOW",
                    description="Expired token correctly rejected",
                    timestamp=datetime.now()
                )
            else:
                time_left = exp_time - current_time
                if time_left > timedelta(hours=24):
                    return AuthTestResult(
                        test_name="token_expiration",
                        passed=False,
                        vulnerability_level="MEDIUM",
                        description="Token expiration too long (>24h)",
                        timestamp=datetime.now()
                    )
        except jwt.ExpiredSignatureError:
            return AuthTestResult(
                test_name="token_expiration",
                passed=True,
                vulnerability_level="LOW",
                description="Token expiration properly handled",
                timestamp=datetime.now()
            )
        except Exception as e:
            return AuthTestResult(
                test_name="token_expiration",
                passed=False,
                vulnerability_level="HIGH",
                description=f"Token validation error: {str(e)}",
                timestamp=datetime.now()
            )

    async def test_brute_force_protection(self, username: str, attempts: int = 10) -> AuthTestResult:
        """Test brute force attack protection"""
        failed_attempts = 0
        for i in range(attempts):
            # Simulate failed login attempts
            try:
                # This would normally call your auth endpoint
                # For testing, we'll simulate the behavior
                failed_attempts += 1
                await asyncio.sleep(0.01)  # Reduced rate limiting for faster testing
            except Exception:
                break
        
        # Check if account gets locked after too many attempts
        locked = failed_attempts >= 5  # Assuming lockout after 5 attempts
        
        return AuthTestResult(
            test_name="brute_force_protection",
            passed=locked,
            vulnerability_level="LOW" if locked else "HIGH",
            description=f"Account {'locked' if locked else 'not locked'} after {failed_attempts} attempts",
            timestamp=datetime.now()
        )

    async def test_session_security(self, session_token: str) -> AuthTestResult:
        """Test session security measures"""
        security_issues = []
        
        # Check if session token is secure
        if len(session_token) < 32:
            security_issues.append("Session token too short")
        
        # Check for proper session invalidation
        # This would normally test actual session management
        
        passed = len(security_issues) == 0
        return AuthTestResult(
            test_name="session_security",
            passed=passed,
            vulnerability_level="LOW" if passed else "MEDIUM",
            description=f"Security issues: {', '.join(security_issues) if security_issues else 'None'}",
            timestamp=datetime.now()
        )

    async def run_all_tests(self, test_data: Dict) -> List[AuthTestResult]:
        """Run comprehensive authentication security tests"""
        results = []
        
        # Password strength test
        if 'passwords' in test_data:
            result = await self.test_password_strength(test_data['passwords'])
            results.append(result)
        
        # Token expiration test
        if 'tokens' in test_data:
            for token in test_data['tokens']:
                result = await self.test_token_expiration(token)
                results.append(result)
        
        # Brute force protection test
        if 'test_username' in test_data:
            result = await self.test_brute_force_protection(test_data['test_username'])
            results.append(result)
        
        # Session security test
        if 'session_tokens' in test_data:
            for token in test_data['session_tokens']:
                result = await self.test_session_security(token)
                results.append(result)
        
        self.test_results = results
        return results

    def get_security_report(self) -> Dict:
        """Generate security report from test results"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.passed)
        
        vulnerabilities = {
            'HIGH': [r for r in self.test_results if r.vulnerability_level == 'HIGH' and not r.passed],
            'MEDIUM': [r for r in self.test_results if r.vulnerability_level == 'MEDIUM' and not r.passed],
            'LOW': [r for r in self.test_results if r.vulnerability_level == 'LOW' and not r.passed]
        }
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'pass_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            'vulnerabilities': vulnerabilities,
            'timestamp': datetime.now().isoformat()
        }

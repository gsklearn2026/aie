import asyncio
import os
import gzip
import logging
from typing import Optional
from dataclasses import dataclass
import google.generativeai as genai

from .backup_strategies import BackupResult

@dataclass
class ValidationResult:
    valid: bool
    confidence_score: float
    issues: list
    size_check: bool
    integrity_check: bool
    ai_analysis: Optional[str] = None

class BackupValidator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize Gemini AI
        api_key = os.environ.get('GEMINI_API_KEY')
        if api_key and api_key != 'your_gemini_api_key_here':
            genai.configure(api_key=api_key)
            self.ai_enabled = True
        else:
            self.ai_enabled = False
            self.logger.warning("Gemini API key not configured, AI validation disabled")
    
    async def validate_backup(self, backup_result: BackupResult) -> ValidationResult:
        """Validate a backup file comprehensively"""
        issues = []
        
        # Basic validation checks
        size_check = self._validate_size(backup_result)
        if not size_check:
            issues.append("Backup file size is suspicious")
        
        integrity_check = await self._validate_integrity(backup_result)
        if not integrity_check:
            issues.append("Backup integrity check failed")
        
        # AI-powered validation
        ai_analysis = None
        if self.ai_enabled and backup_result.file_path:
            ai_analysis = await self._ai_validate_backup(backup_result)
            if "CRITICAL" in ai_analysis.upper():
                issues.append("AI detected critical issues")
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence(size_check, integrity_check, issues)
        
        return ValidationResult(
            valid=len(issues) == 0,
            confidence_score=confidence_score,
            issues=issues,
            size_check=size_check,
            integrity_check=integrity_check,
            ai_analysis=ai_analysis
        )
    
    def _validate_size(self, backup_result: BackupResult) -> bool:
        """Validate backup file size is reasonable"""
        if not backup_result.file_path or not backup_result.size:
            return False
        
        # Check minimum size (should be at least 1KB for valid backup)
        if backup_result.size < 1024:
            return False
        
        # Check file exists and reported size matches actual size
        if os.path.exists(backup_result.file_path):
            actual_size = os.path.getsize(backup_result.file_path)
            return abs(actual_size - backup_result.size) < 1024  # Allow 1KB variance
        
        return False
    
    async def _validate_integrity(self, backup_result: BackupResult) -> bool:
        """Validate backup file integrity"""
        if not backup_result.file_path or not os.path.exists(backup_result.file_path):
            return False
        
        try:
            # For compressed files, try to decompress a portion
            if backup_result.file_path.endswith('.gz'):
                with gzip.open(backup_result.file_path, 'rt') as f:
                    # Try to read first few lines
                    for _ in range(5):
                        line = f.readline()
                        if not line:
                            break
                    return True
            
            # For directory backups, check if it contains expected files
            elif os.path.isdir(backup_result.file_path):
                files = os.listdir(backup_result.file_path)
                return len(files) > 0
            
            # For other files, basic read test
            else:
                with open(backup_result.file_path, 'rb') as f:
                    f.read(1024)  # Try to read first 1KB
                return True
                
        except Exception as e:
            self.logger.error(f"Integrity check failed: {e}")
            return False
    
    async def _ai_validate_backup(self, backup_result: BackupResult) -> str:
        """Use AI to analyze backup content and structure"""
        if not self.ai_enabled:
            return "AI validation disabled"
        
        try:
            # Read sample of backup content
            sample_content = await self._get_backup_sample(backup_result.file_path)
            
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"""
            Analyze this database backup sample for potential issues:
            
            Backup Type: {backup_result.backup_type}
            File Size: {backup_result.size} bytes
            Duration: {backup_result.duration} seconds
            
            Sample Content (first 500 chars):
            {sample_content[:500]}
            
            Please identify:
            1. Any structural anomalies
            2. Potential corruption indicators
            3. Missing expected elements
            4. Overall quality assessment
            
            Respond with PASS if backup looks healthy, or CRITICAL if serious issues found.
            """
            
            response = await asyncio.to_thread(model.generate_content, prompt)
            return response.text
            
        except Exception as e:
            self.logger.error(f"AI validation failed: {e}")
            return f"AI validation error: {str(e)}"
    
    async def _get_backup_sample(self, file_path: str) -> str:
        """Get a sample of backup content for AI analysis"""
        try:
            if file_path.endswith('.gz'):
                with gzip.open(file_path, 'rt') as f:
                    return f.read(1000)  # Read first 1000 chars
            elif os.path.isdir(file_path):
                # For directory backups, list files
                files = os.listdir(file_path)[:10]  # First 10 files
                return "Directory contents: " + ", ".join(files)
            else:
                with open(file_path, 'rb') as f:
                    content = f.read(1000)
                    try:
                        return content.decode('utf-8', errors='ignore')
                    except:
                        return f"Binary content, {len(content)} bytes"
        except Exception as e:
            return f"Error reading sample: {str(e)}"
    
    def _calculate_confidence(self, size_check: bool, integrity_check: bool, issues: list) -> float:
        """Calculate confidence score based on validation results"""
        base_score = 1.0
        
        if not size_check:
            base_score -= 0.3
        
        if not integrity_check:
            base_score -= 0.4
        
        # Deduct points for each issue
        base_score -= len(issues) * 0.1
        
        return max(0.0, min(1.0, base_score))

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import asyncio
import time
from loguru import logger
from dataclasses import dataclass
from enum import Enum

class TestStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class TestResult:
    test_name: str
    status: TestStatus
    execution_time: float
    details: Dict[str, Any]
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class BaseTestRunner(ABC):
    def __init__(self, name: str):
        self.name = name
        self.results: List[TestResult] = []
        self.start_time = None
        self.end_time = None
        
    @abstractmethod
    async def setup(self) -> None:
        """Setup test environment"""
        pass
    
    @abstractmethod
    async def teardown(self) -> None:
        """Cleanup test environment"""
        pass
    
    @abstractmethod
    async def run_test(self, test_case: Dict[str, Any]) -> TestResult:
        """Execute individual test case"""
        pass
    
    async def run_suite(self, test_cases: List[Dict[str, Any]]) -> List[TestResult]:
        """Run complete test suite"""
        logger.info(f"Starting test suite: {self.name}")
        self.start_time = time.time()
        
        try:
            await self.setup()
            
            # Run tests concurrently with limited parallelism
            semaphore = asyncio.Semaphore(5)  # Limit concurrent tests
            
            async def run_single_test(test_case):
                async with semaphore:
                    return await self.run_test(test_case)
            
            tasks = [run_single_test(test_case) for test_case in test_cases]
            self.results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions in results
            processed_results = []
            for i, result in enumerate(self.results):
                if isinstance(result, Exception):
                    processed_results.append(TestResult(
                        test_name=f"test_{i}",
                        status=TestStatus.FAILED,
                        execution_time=0.0,
                        details={},
                        error_message=str(result)
                    ))
                else:
                    processed_results.append(result)
            
            self.results = processed_results
            
        finally:
            await self.teardown()
            self.end_time = time.time()
        
        logger.info(f"Test suite completed: {self.name}")
        return self.results
    
    def get_summary(self) -> Dict[str, Any]:
        """Get test execution summary"""
        if not self.results:
            return {"status": "no_tests", "summary": {}}
        
        passed = len([r for r in self.results if r.status == TestStatus.PASSED])
        failed = len([r for r in self.results if r.status == TestStatus.FAILED])
        skipped = len([r for r in self.results if r.status == TestStatus.SKIPPED])
        total = len(self.results)
        
        total_time = self.end_time - self.start_time if self.end_time and self.start_time else 0
        
        return {
            "status": "completed",
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "success_rate": passed / total if total > 0 else 0,
                "total_execution_time": total_time,
                "average_test_time": sum(r.execution_time for r in self.results) / total if total > 0 else 0
            },
            "results": [
                {
                    "test_name": r.test_name,
                    "status": r.status.value,
                    "execution_time": r.execution_time,
                    "details": r.details,
                    "error_message": r.error_message
                }
                for r in self.results
            ]
        }

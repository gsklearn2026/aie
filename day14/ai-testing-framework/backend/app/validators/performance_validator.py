import time
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import statistics

@dataclass
class PerformanceMetrics:
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float
    success_rate: float
    throughput: float
    error_count: int
    total_requests: int

class PerformanceValidator:
    def __init__(self):
        self.max_response_time = 5000  # milliseconds
        self.min_success_rate = 0.95
        self.target_throughput = 10  # requests per second
        
    async def validate_performance(self, ai_service, test_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run performance validation tests"""
        concurrent_users = test_config.get("concurrent_users", 5)
        requests_per_user = test_config.get("requests_per_user", 3)
        test_prompt = test_config.get("prompt", "Performance test prompt")
        
        start_time = time.time()
        
        # Run concurrent performance test
        tasks = []
        for user in range(concurrent_users):
            tasks.append(self._run_user_simulation(ai_service, test_prompt, requests_per_user))
        
        user_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Aggregate results
        all_response_times = []
        successful_requests = 0
        failed_requests = 0
        
        for user_result in user_results:
            if isinstance(user_result, Exception):
                failed_requests += requests_per_user
                continue
                
            for request_result in user_result:
                if request_result.get("success", False):
                    successful_requests += 1
                    all_response_times.append(request_result["response_time"])
                else:
                    failed_requests += 1
        
        total_requests = successful_requests + failed_requests
        
        # Calculate metrics
        if all_response_times:
            metrics = PerformanceMetrics(
                avg_response_time=statistics.mean(all_response_times),
                p95_response_time=self._percentile(all_response_times, 95),
                p99_response_time=self._percentile(all_response_times, 99),
                success_rate=successful_requests / total_requests if total_requests > 0 else 0,
                throughput=successful_requests / total_duration if total_duration > 0 else 0,
                error_count=failed_requests,
                total_requests=total_requests
            )
        else:
            metrics = PerformanceMetrics(0, 0, 0, 0, 0, failed_requests, total_requests)
        
        # Validate against thresholds
        validation_results = self._validate_metrics(metrics, test_config)
        
        return {
            "metrics": {
                "avg_response_time": metrics.avg_response_time,
                "p95_response_time": metrics.p95_response_time,
                "p99_response_time": metrics.p99_response_time,
                "success_rate": metrics.success_rate,
                "throughput": metrics.throughput,
                "error_count": metrics.error_count,
                "total_requests": metrics.total_requests,
                "test_duration": total_duration
            },
            "validation": validation_results,
            "passed": validation_results["overall_passed"]
        }
    
    async def _run_user_simulation(self, ai_service, prompt: str, request_count: int) -> List[Dict[str, Any]]:
        """Simulate requests from a single user"""
        results = []
        
        for i in range(request_count):
            start_time = time.time()
            try:
                response = await ai_service.generate_text(f"{prompt} - request {i}")
                response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                
                results.append({
                    "success": True,
                    "response_time": response_time,
                    "tokens_used": response.get("tokens_used", 0),
                    "provider": response.get("provider", "unknown")
                })
            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                results.append({
                    "success": False,
                    "response_time": response_time,
                    "error": str(e)
                })
        
        return results
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile value"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def _validate_metrics(self, metrics: PerformanceMetrics, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate performance metrics against thresholds"""
        max_response_time = config.get("max_response_time", self.max_response_time)
        min_success_rate = config.get("min_success_rate", self.min_success_rate)
        min_throughput = config.get("min_throughput", self.target_throughput)
        
        validations = {
            "response_time_valid": metrics.p95_response_time <= max_response_time,
            "success_rate_valid": metrics.success_rate >= min_success_rate,
            "throughput_valid": metrics.throughput >= min_throughput,
            "error_count_acceptable": metrics.error_count / metrics.total_requests <= (1 - min_success_rate) if metrics.total_requests > 0 else True
        }
        
        validations["overall_passed"] = all(validations.values())
        
        return validations

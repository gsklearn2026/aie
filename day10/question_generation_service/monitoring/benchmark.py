"""Performance benchmarking for question generation service"""

import asyncio
import time
import statistics
from typing import List
import httpx
import json

class PerformanceBenchmark:
    """Benchmark question generation service performance"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
        
    async def benchmark_question_generation(self, 
                                           topics: List[str], 
                                           concurrent_requests: int = 10) -> dict:
        """Benchmark question generation with concurrent requests"""
        print(f"🚀 Starting benchmark with {concurrent_requests} concurrent requests...")
        
        tasks = []
        for i in range(concurrent_requests):
            topic = topics[i % len(topics)]
            tasks.append(self._generate_questions_with_timing(topic, i))
            
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        # Process results
        successful_results = [r for r in results if not isinstance(r, Exception)]
        failed_results = [r for r in results if isinstance(r, Exception)]
        
        if successful_results:
            response_times = [r['response_time'] for r in successful_results]
            generation_times = [r['generation_time'] for r in successful_results 
                              if r['generation_time'] is not None]
            
            stats = {
                "total_requests": concurrent_requests,
                "successful_requests": len(successful_results),
                "failed_requests": len(failed_results),
                "total_time": total_time,
                "requests_per_second": len(successful_results) / total_time,
                "average_response_time": statistics.mean(response_times),
                "median_response_time": statistics.median(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
            }
            
            if generation_times:
                stats.update({
                    "average_generation_time": statistics.mean(generation_times),
                    "median_generation_time": statistics.median(generation_times),
                })
                
        else:
            stats = {
                "total_requests": concurrent_requests,
                "successful_requests": 0,
                "failed_requests": len(failed_results),
                "error": "All requests failed"
            }
            
        return stats
        
    async def _generate_questions_with_timing(self, topic: str, request_id: int) -> dict:
        """Generate questions and measure timing"""
        start_time = time.time()
        
        # Submit job
        response = await self.client.post(f"{self.base_url}/questions/generate", 
                                        json={"topic": topic, "count": 3})
        
        if response.status_code != 200:
            raise Exception(f"Failed to submit job: {response.status_code}")
            
        job_data = response.json()
        job_id = job_data["job_id"]
        
        # Poll for completion
        generation_start = time.time()
        while True:
            status_response = await self.client.get(f"{self.base_url}/questions/jobs/{job_id}")
            
            if status_response.status_code != 200:
                raise Exception(f"Failed to get job status: {status_response.status_code}")
                
            status_data = status_response.json()
            
            if status_data["status"] == "completed":
                generation_time = time.time() - generation_start
                break
            elif status_data["status"] == "failed":
                raise Exception(f"Job failed: {status_data.get('error_message', 'Unknown error')}")
                
            await asyncio.sleep(0.1)
            
        response_time = time.time() - start_time
        
        return {
            "request_id": request_id,
            "job_id": job_id,
            "topic": topic,
            "response_time": response_time,
            "generation_time": generation_time,
            "question_count": len(status_data.get("questions", []))
        }
        
    async def health_check_benchmark(self, requests: int = 100) -> dict:
        """Benchmark health check endpoint"""
        print(f"🏥 Benchmarking health check with {requests} requests...")
        
        tasks = [self._health_check_request() for _ in range(requests)]
        
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        successful = len([r for r in results if not isinstance(r, Exception)])
        failed = len([r for r in results if isinstance(r, Exception)])
        
        return {
            "total_requests": requests,
            "successful_requests": successful,
            "failed_requests": failed,
            "total_time": total_time,
            "requests_per_second": successful / total_time,
        }
        
    async def _health_check_request(self):
        """Single health check request"""
        response = await self.client.get(f"{self.base_url}/health")
        if response.status_code != 200:
            raise Exception(f"Health check failed: {response.status_code}")
        return response.json()
        
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def run_benchmarks():
    """Run all benchmarks"""
    benchmark = PerformanceBenchmark()
    
    try:
        # Test topics
        topics = [
            "Python programming",
            "Machine Learning",
            "Web Development",
            "Data Structures",
            "Software Engineering"
        ]
        
        print("🔥 Performance Benchmark Results")
        print("=" * 50)
        
        # Health check benchmark
        health_stats = await benchmark.health_check_benchmark(100)
        print(f"Health Check: {health_stats['requests_per_second']:.2f} req/s")
        
        # Question generation benchmark
        gen_stats = await benchmark.benchmark_question_generation(topics, 5)
        print(f"Question Generation:")
        print(f"  - Success Rate: {gen_stats['successful_requests']}/{gen_stats['total_requests']}")
        print(f"  - Avg Response Time: {gen_stats.get('average_response_time', 0):.2f}s")
        print(f"  - Throughput: {gen_stats.get('requests_per_second', 0):.2f} req/s")
        
        return gen_stats
        
    finally:
        await benchmark.close()

if __name__ == "__main__":
    asyncio.run(run_benchmarks())

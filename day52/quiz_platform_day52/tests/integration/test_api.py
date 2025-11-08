import sys
import os
import asyncio
import httpx

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

BASE_URL = "http://localhost:8000"

async def test_root_endpoint():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"

async def test_memory_stats():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/memory/stats")
        assert response.status_code == 200
        data = response.json()
        assert "process" in data
        assert "tracker" in data

async def test_quiz_generation():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/quiz/generate",
            json={"topic": "Python", "num_questions": 3},
            timeout=30.0
        )
        assert response.status_code == 200
        data = response.json()
        assert "questions" in data
        assert len(data["questions"]) == 3

async def test_gc_trigger():
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/api/memory/gc")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"

async def run_all_tests():
    print("Running integration tests...")
    await test_root_endpoint()
    print("✅ Root endpoint test passed")
    
    await test_memory_stats()
    print("✅ Memory stats test passed")
    
    await test_quiz_generation()
    print("✅ Quiz generation test passed")
    
    await test_gc_trigger()
    print("✅ GC trigger test passed")
    
    print("\n✅ All integration tests passed!")

if __name__ == "__main__":
    asyncio.run(run_all_tests())

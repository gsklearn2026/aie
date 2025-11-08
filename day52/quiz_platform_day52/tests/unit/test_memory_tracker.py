import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from app.services.memory_tracker import MemoryTracker

def test_memory_tracker_singleton():
    tracker1 = MemoryTracker()
    tracker2 = MemoryTracker()
    assert tracker1 is tracker2, "MemoryTracker should be singleton"

def test_record_request():
    tracker = MemoryTracker()
    initial_count = len(tracker.request_history)
    
    tracker.record_request(
        endpoint="/test",
        memory_before=100.0,
        memory_after=105.0,
        memory_diff=5.0,
        duration=0.5,
        top_allocations=[]
    )
    
    assert len(tracker.request_history) == initial_count + 1

def test_leak_detection():
    tracker = MemoryTracker()
    endpoint = "/leak_test"
    
    for _ in range(5):
        tracker.record_request(
            endpoint=endpoint,
            memory_before=100.0,
            memory_after=105.0,
            memory_diff=2.0,
            duration=0.5,
            top_allocations=[]
        )
    
    assert endpoint in tracker.leak_suspects

if __name__ == "__main__":
    test_memory_tracker_singleton()
    test_record_request()
    test_leak_detection()
    print("✅ All unit tests passed!")

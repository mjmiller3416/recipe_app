#!/usr/bin/env python3
"""
Performance test script for optimized hook handler sound system.
Tests latency and measures response times.
"""
import json
from pathlib import Path
import sys
import time

# Import the optimized hook handler functions
sys.path.insert(0, str(Path(__file__).parent))
from hook_handler import (
    OS_NAME, SOUND_CACHE, WINSOUND_AVAILABLE, handle_event, initialize_sound_cache,
)

def test_sound_latency():
    """Test sound trigger latency with the optimized system."""
    print("=" * 60)
    print("PERFORMANCE TEST: Hook Handler Sound Latency")
    print("=" * 60)
    print(f"OS: {OS_NAME}")
    print(f"winsound available: {WINSOUND_AVAILABLE}")
    
    # Initialize cache (simulate startup)
    print("\n1. Initializing sound cache...")
    start_time = time.perf_counter()
    initialize_sound_cache()
    init_time = (time.perf_counter() - start_time) * 1000
    print(f"   Cache initialization: {init_time:.2f}ms")
    print(f"   Cached sounds: {len(SOUND_CACHE)}")
    
    # Test each event type
    test_events = [
        {"hook_event_name": "Notification"},
        {"hook_event_name": "PostToolUse"},
        {"hook_event_name": "Stop"},
        {"hook_event_name": "Error"},
        {"hook_event_name": "SubagentStop"}
    ]
    
    print(f"\n2. Testing sound trigger latency...")
    print("   (measuring time from event receipt to sound command dispatch)")
    
    latencies = []
    
    for i, event in enumerate(test_events):
        event_type = event["hook_event_name"]
        print(f"\n   Test {i+1}: {event_type}")
        
        # Measure latency from event to sound dispatch
        start_time = time.perf_counter()
        handle_event(event)
        latency = (time.perf_counter() - start_time) * 1000
        
        latencies.append(latency)
        print(f"      Latency: {latency:.2f}ms")
        
        # Small delay between tests
        time.sleep(0.5)
    
    # Results summary
    print(f"\n3. LATENCY RESULTS:")
    print(f"   Average latency: {sum(latencies)/len(latencies):.2f}ms")
    print(f"   Min latency: {min(latencies):.2f}ms") 
    print(f"   Max latency: {max(latencies):.2f}ms")
    
    # Performance analysis
    avg_latency = sum(latencies) / len(latencies)
    if avg_latency < 10:
        print(f"   *** EXCELLENT: Sub-10ms response time")
    elif avg_latency < 50:
        print(f"   ** GOOD: Sub-50ms response time") 
    elif avg_latency < 100:
        print(f"   * ACCEPTABLE: Sub-100ms response time")
    else:
        print(f"   POOR: >100ms response time needs optimization")
    
    print(f"\n4. OPTIMIZATION SUMMARY:")
    optimizations = [
        "[+] Eliminated PowerShell startup overhead",
        "[+] Pre-cached sound file paths",
        "[+] Asynchronous sound playback",
        "[+] Asynchronous event logging", 
        "[+] Built-in winsound API (Windows)",
        "[+] Suppressed subprocess stdout/stderr",
        "[+] Daemon threads for non-blocking operations"
    ]
    
    for opt in optimizations:
        print(f"   {opt}")
        
    print("\n" + "=" * 60)

def test_concurrent_events():
    """Test handling multiple rapid events."""
    print(f"\n5. CONCURRENT EVENT TEST:")
    print("   Testing rapid-fire event handling...")
    
    events = [
        {"hook_event_name": "Notification"},
        {"hook_event_name": "PostToolUse"},
        {"hook_event_name": "Notification"},
        {"hook_event_name": "Error"},
        {"hook_event_name": "Stop"}
    ]
    
    start_time = time.perf_counter()
    
    # Fire events rapidly
    for event in events:
        handle_event(event)
    
    total_time = (time.perf_counter() - start_time) * 1000
    avg_per_event = total_time / len(events)
    
    print(f"   {len(events)} events processed in {total_time:.2f}ms")
    print(f"   Average per event: {avg_per_event:.2f}ms")
    
    if avg_per_event < 5:
        print(f"   *** EXCELLENT: Can handle rapid events")
    else:
        print(f"   * May struggle with very rapid events")

if __name__ == "__main__":
    test_sound_latency()
    test_concurrent_events()
    
    print(f"\nTest complete. The optimized hook handler should provide")
    print(f"near-instantaneous (<10ms) sound response times.")
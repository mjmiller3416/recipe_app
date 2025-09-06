#!/usr/bin/env python3
"""Quick test to verify notification sound timing"""

import json
import sys
import time
from pathlib import Path

def test_notification():
    """Send a notification event to the hook handler"""
    # Create a notification event
    event = {
        "hook_event_name": "Notification",
        "test": True,
        "timestamp": time.time()
    }
    
    print("Triggering notification sound...")
    start = time.perf_counter()
    
    # Send event to hook handler via stdin
    import subprocess
    hook_handler = Path(__file__).parent / "hook_handler.py"
    
    process = subprocess.Popen(
        [sys.executable, str(hook_handler)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Send the event
    process.stdin.write(json.dumps(event) + "\n")
    process.stdin.flush()
    
    # Give it a moment to process
    time.sleep(0.1)
    
    # Terminate the handler
    process.terminate()
    
    elapsed = (time.perf_counter() - start) * 1000
    print(f"✓ Notification triggered in {elapsed:.2f}ms")
    
    # Check if sound file exists
    sound_file = Path(__file__).parent / "sounds" / "notification.wav"
    if sound_file.exists():
        print(f"✓ Sound file found: {sound_file}")
    else:
        print(f"✗ Sound file missing: {sound_file}")
        print("  Please ensure notification.wav is in the sounds/ directory")

if __name__ == "__main__":
    print("=" * 50)
    print("NOTIFICATION SOUND TEST")
    print("=" * 50)
    print("\nYou should hear the notification sound immediately.\n")
    
    test_notification()
    
    print("\nDid you hear the notification sound? (It should play instantly)")
    print("If not, check that:")
    print("  1. Your volume is turned up")
    print("  2. The sounds/notification.wav file exists")
    print("  3. Windows audio service is running")
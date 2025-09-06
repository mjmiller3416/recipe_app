#!/usr/bin/env python3
"""
Comparison test: Old PowerShell method vs New optimized method
"""
import time
import subprocess
from pathlib import Path
import winsound

def test_old_powershell_method(sound_path):
    """Test the old PowerShell method"""
    start_time = time.perf_counter()
    try:
        # Old method from original code
        subprocess.Popen([
            "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe", "-c",
            f"(New-Object Media.SoundPlayer '{sound_path}').PlaySync();"
        ])
        latency = (time.perf_counter() - start_time) * 1000
        return latency
    except Exception as e:
        return None

def test_new_winsound_method(sound_path):
    """Test the new winsound method"""
    start_time = time.perf_counter()
    try:
        # New method - built-in winsound
        winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NOWAIT)
        latency = (time.perf_counter() - start_time) * 1000
        return latency
    except Exception as e:
        return None

if __name__ == "__main__":
    sound_path = str(Path(__file__).parent / "sounds" / "notification.wav")
    
    if not Path(sound_path).exists():
        print("Sound file not found!")
        exit(1)
        
    print("PERFORMANCE COMPARISON: Old vs New Sound Methods")
    print("=" * 50)
    
    # Test old method
    print("Testing OLD PowerShell method...")
    old_times = []
    for i in range(3):
        latency = test_old_powershell_method(sound_path)
        if latency:
            old_times.append(latency)
            print(f"  Test {i+1}: {latency:.2f}ms")
        time.sleep(1)  # Wait between tests
    
    print(f"\nTesting NEW winsound method...")  
    new_times = []
    for i in range(3):
        latency = test_new_winsound_method(sound_path)
        if latency:
            new_times.append(latency)
            print(f"  Test {i+1}: {latency:.2f}ms")
        time.sleep(0.1)  # Shorter wait for faster method
    
    print("\n" + "=" * 50)
    print("RESULTS:")
    
    if old_times:
        old_avg = sum(old_times) / len(old_times)
        print(f"Old PowerShell average: {old_avg:.2f}ms")
    else:
        print("Old PowerShell method failed")
        
    if new_times:
        new_avg = sum(new_times) / len(new_times)  
        print(f"New winsound average: {new_avg:.2f}ms")
        
        if old_times:
            improvement = ((old_avg - new_avg) / old_avg) * 100
            speedup = old_avg / new_avg
            print(f"\nIMPROVEMENT:")
            print(f"  Speed improvement: {improvement:.1f}%")
            print(f"  Speed-up factor: {speedup:.1f}x faster")
    else:
        print("New winsound method failed")
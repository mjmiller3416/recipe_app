#!/usr/bin/env python3
from pathlib import Path
import platform
import subprocess
import time

# Detect OS once
OS_NAME = platform.system()

def play_sound(sound_path: str, sound_name: str):
    """Play sound and report results."""
    print(f"\n--- Testing {sound_name} ---")
    print(f"File: {sound_path}")
    
    if not Path(sound_path).exists():
        print(f"[ERROR] Sound file not found: {sound_path}")
        return False

    try:
        if OS_NAME == "Windows":
            # Try multiple Windows sound approaches
            try:
                # First try PowerShell with full path
                result = subprocess.run([
                    "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe", "-c",
                    f"(New-Object Media.SoundPlayer '{sound_path}').PlaySync();"
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    print(f"[SUCCESS] {sound_name} played successfully via PowerShell")
                    return True
                else:
                    print(f"[WARN] PowerShell failed: {result.stderr}")
                    
            except Exception as e:
                print(f"[WARN] PowerShell failed: {e}")
                
            try:
                # Fallback to Windows Media Player
                result = subprocess.run([
                    "C:\\Program Files\\Windows Media Player\\wmplayer.exe",
                    sound_path, "/close"
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    print(f"[SUCCESS] {sound_name} played successfully via Windows Media Player")
                    return True
                else:
                    print(f"[WARN] WMP failed: {result.stderr}")
                    
            except Exception as e:
                print(f"[WARN] WMP failed: {e}")
                
            try:
                # Last fallback - use start command  
                result = subprocess.run([
                    "cmd", "/c", "start", "/min", sound_path
                ], capture_output=True, text=True, timeout=5)
                
                print(f"[INFO] {sound_name} sent to default player via start command")
                return True
                
            except Exception as e:
                print(f"[ERROR] All methods failed for {sound_name}: {e}")
                return False
                
    except Exception as e:
        print(f"[ERROR] Failed to play {sound_name}: {e}")
        return False

if __name__ == "__main__":
    sounds_dir = Path(__file__).parent / "sounds"
    
    # Test each sound file
    sound_files = {
        "notification.wav": "Notification",
        "stop.wav": "Stop", 
        "subagent_stop.wav": "SubagentStop",
        "pre_tool_use.wav": "PreToolUse",
        "post_tool_use.wav": "PostToolUse",
        "error.wav": "Error"
    }
    
    print(f"OS detected: {OS_NAME}")
    print(f"Testing sounds in: {sounds_dir}")
    print("=" * 50)
    
    results = {}
    for filename, name in sound_files.items():
        sound_path = sounds_dir / filename
        results[name] = play_sound(str(sound_path), name)
        time.sleep(2)  # Wait 2 seconds between tests
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    for name, success in results.items():
        status = "✅ WORKING" if success else "❌ FAILED"
        print(f"  {name}: {status}")
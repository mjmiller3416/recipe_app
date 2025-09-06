#!/usr/bin/env python3
from pathlib import Path
import platform
import subprocess

# Detect OS once
OS_NAME = platform.system()

def play_sound(sound_path: str):
    """Play sound in a cross-platform way."""
    if not Path(sound_path).exists():
        print(f"[WARN] Sound file not found: {sound_path}")
        return

    try:
        if OS_NAME == "Darwin":  # macOS
            subprocess.Popen(["afplay", sound_path])
        elif OS_NAME == "Linux":
            # Try paplay first (PulseAudio), fallback to aplay
            try:
                subprocess.Popen(["paplay", sound_path])
            except FileNotFoundError:
                subprocess.Popen(["aplay", sound_path])
        elif OS_NAME == "Windows":
            # Try multiple Windows sound approaches
            try:
                # First try PowerShell with full path
                subprocess.Popen([
                    "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe", "-c",
                    f"(New-Object Media.SoundPlayer '{sound_path}').PlaySync();"
                ])
            except FileNotFoundError:
                try:
                    # Fallback to Windows Media Player
                    subprocess.Popen([
                        "C:\\Program Files\\Windows Media Player\\wmplayer.exe",
                        sound_path, "/close"
                    ])
                except FileNotFoundError:
                    # Last fallback - use start command
                    subprocess.Popen([
                        "cmd", "/c", "start", "/min", sound_path
                    ])
        else:
            print(f"[WARN] Unsupported OS for audio: {OS_NAME}")
    except Exception as e:
        print(f"[ERROR] Failed to play sound: {e}")

if __name__ == "__main__":
    sound_file = Path(__file__).parent / "sounds" / "notification.wav"
    print(f"OS detected: {OS_NAME}")
    print(f"Testing sound file: {sound_file}")
    print(f"File exists: {sound_file.exists()}")
    
    if sound_file.exists():
        print("Playing sound...")
        play_sound(str(sound_file))
        print("Sound command sent.")
    else:
        print("Sound file not found!")
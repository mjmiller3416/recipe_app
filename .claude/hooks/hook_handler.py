#!/usr/bin/env python3
import sys
import json
import subprocess
import platform
from pathlib import Path
from datetime import datetime

# Detect OS once
OS_NAME = platform.system()

# Path to log file
log_file = Path(__file__).parent / "hook_handler.jsonl"

# Define audio cue mapping
sound_map = {
    "Notification": "sounds/notification.wav",
    "Stop": "sounds/stop.wav",
    "SubagentStop": "sounds/subagent_stop.wav",
    "PreToolUse": "sounds/pre_tool_use.wav",
    "PostToolUse": "sounds/post_tool_use.wav",
    "Error": "sounds/error.wav",
}

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

def handle_event(event: dict):
    """Handle incoming hook events and trigger sounds."""
    event_type = event.get("hook_event_name", "Unknown")
    timestamp = datetime.now().isoformat()

    # Debug: Print event received
    print(f"[DEBUG] Event received: {event_type} at {timestamp}")

    # Log the event
    with open(log_file, "a") as f:
        f.write(json.dumps({"time": timestamp, **event}) + "\n")

    # Pick sound file
    sound_file = sound_map.get(event_type)
    if sound_file:
        sound_path = str(Path(__file__).parent / sound_file)
        print(f"[DEBUG] Playing sound: {sound_path}")
        play_sound(sound_path)
    else:
        print(f"[DEBUG] No sound file found for event type: {event_type}")

def main():
    for line in sys.stdin:
        try:
            event = json.loads(line.strip())
            handle_event(event)
        except json.JSONDecodeError:
            print(f"[ERROR] Failed to parse event: {line.strip()}")

if __name__ == "__main__":
    main()

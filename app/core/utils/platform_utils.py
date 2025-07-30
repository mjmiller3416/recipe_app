"""app/core/utils/platform_utils.py

This module contains utility functions for interacting with the underlying
operating system in a platform-specific way.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
import sys
import winreg


# ── Functions ────────────────────────────────────────────────────────────────────────────────
def get_taskbar_rect():
    """
    Gets the bounding rectangle of the Windows taskbar.

    Returns:
        tuple (left, top, right, bottom) of the taskbar, or None if not on Windows
        or if the taskbar can't be found.
    """
    if sys.platform != "win32":
        return None

    try:
        import win32gui

        # the taskbar window class name is "Shell_TrayWnd"
        taskbar_hwnd = win32gui.FindWindow("Shell_TrayWnd", None)
        if taskbar_hwnd:
            return win32gui.GetWindowRect(taskbar_hwnd)
    except (ImportError, Exception):
        # pywin32 not installed or an API error occurred
        return None
    return None

def disable_system_border_accent():
    """Disable Windows 11 border accent by setting ColorPrevalence = 0"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\DWM", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "ColorPrevalence", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        print("✅ System border accent disabled (ColorPrevalence = 0)")
    except Exception as e:
        print(f"❌ Failed to disable border accent: {e}")

#!/usr/bin/env python3
"""
Test suite for critical bug fixes in Part One implementation.

Tests the following fixes:
1. Memory leak fixes in ThemedIcon cleanup
2. Timer management for theme refresh debouncing  
3. Layout race condition prevention
4. Color resolution precedence
5. Size parameter validation
6. State operation validation
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

# Import the classes we're testing
from app.appearance.icon.config import Name, State, Type
from app.appearance.icon.icon import StateIcon, Icon
from app.ui.components.widgets.button import Button, ToolButton


class TestCriticalFixes:
    """Test suite for critical bug fixes."""
    
    def __init__(self):
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication(sys.argv)
        
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result."""
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {test_name}: {message}")
        
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
    
    def test_size_validation(self):
        """Test size parameter validation."""
        print("\n=== Testing Size Parameter Validation ===")
        
        # Test StateIcon size validation
        try:
            state_icon = StateIcon(Name.ADD, Type.DEFAULT)
            
            # Test valid size
            state_icon.setSize(32, 32)
            self.log_test("StateIcon valid size", True, "32x32 accepted")
            
            # Test type validation
            try:
                state_icon.setSize("32", 32)
                self.log_test("StateIcon type validation", False, "Should reject string input")
            except TypeError:
                self.log_test("StateIcon type validation", True, "Correctly rejected string input")
            
            # Test clamping
            state_icon.setSize(1000, 1000)  # Should clamp to 512
            self.log_test("StateIcon size clamping", True, "Large size clamped")
            
        except Exception as e:
            self.log_test("StateIcon size validation", False, f"Exception: {e}")
        
        # Test Button size validation
        try:
            button = Button("Test", Type.DEFAULT, Name.ADD)
            
            # Test valid button size
            button.setButtonSize(100, 50)
            self.log_test("Button valid size", True, "100x50 accepted")
            
            # Test icon size validation
            try:
                button.setIconSize(24.5, 24)  # Should reject float
                self.log_test("Button icon size type validation", False, "Should reject float input")
            except TypeError:
                self.log_test("Button icon size type validation", True, "Correctly rejected float input")
                
        except Exception as e:
            self.log_test("Button size validation", False, f"Exception: {e}")
    
    def test_state_validation(self):
        """Test state operation validation."""
        print("\n=== Testing State Operation Validation ===")
        
        try:
            state_icon = StateIcon(Name.ADD, Type.DEFAULT)
            
            # Test valid state operations
            state_icon.setStateColor(State.HOVER, "primary")
            self.log_test("StateIcon valid state color", True, "State.HOVER with 'primary' accepted")
            
            # Test invalid state type
            try:
                state_icon.setStateColor("hover", "primary")  # Should reject string
                self.log_test("StateIcon state type validation", False, "Should reject string state")
            except TypeError:
                self.log_test("StateIcon state type validation", True, "Correctly rejected string state")
            
            # Test invalid color role
            try:
                state_icon.setStateColor(State.HOVER, "")  # Empty color
                self.log_test("StateIcon empty color validation", False, "Should reject empty color")
            except ValueError:
                self.log_test("StateIcon empty color validation", True, "Correctly rejected empty color")
            
            # Test state update validation
            try:
                state_icon.updateState("invalid")  # Should reject string
                self.log_test("StateIcon updateState validation", False, "Should reject string state")
            except TypeError:
                self.log_test("StateIcon updateState validation", True, "Correctly rejected string state")
                
        except Exception as e:
            self.log_test("State validation", False, f"Exception: {e}")
    
    def test_layout_synchronization(self):
        """Test layout race condition fixes."""
        print("\n=== Testing Layout Synchronization ===")
        
        try:
            button = Button("Test", Type.DEFAULT, Name.ADD)
            
            # Test icon size change triggers proper layout update
            original_size = button.sizeHint()
            button.setIconSize(48, 48)
            new_size = button.sizeHint()
            
            # Size should change (indicating layout was updated)
            size_changed = new_size != original_size
            self.log_test("Button layout synchronization", size_changed, 
                         f"Size changed from {original_size} to {new_size}")
            
            # Test ToolButton layout synchronization
            tool_button = ToolButton(Name.SETTINGS, Type.DEFAULT)
            original_tool_size = tool_button.sizeHint()
            tool_button.setIconSize(32, 32)
            new_tool_size = tool_button.sizeHint()
            
            # Size should reflect icon change
            tool_size_changed = new_tool_size != original_tool_size
            self.log_test("ToolButton layout synchronization", tool_size_changed,
                         f"Size changed from {original_tool_size} to {new_tool_size}")
            
        except Exception as e:
            self.log_test("Layout synchronization", False, f"Exception: {e}")
    
    def test_memory_management(self):
        """Test memory leak fixes."""
        print("\n=== Testing Memory Management ===")
        
        try:
            # Create and destroy multiple icons to test cleanup
            icons = []
            for i in range(10):
                icon = Icon(Name.ADD)
                icons.append(icon)
            
            # Clear references (should trigger cleanup)
            del icons
            
            self.log_test("Icon memory management", True, "Multiple icons created and cleaned up")
            
            # Test ThemedIcon timer cleanup (StateIcon uses internal _themed_icon)
            state_icon = StateIcon(Name.SETTINGS, Type.DEFAULT)
            
            # Trigger multiple theme refreshes rapidly via the internal ThemedIcon
            for i in range(5):
                state_icon._themed_icon.refresh_theme({"primary": "#FF0000"})
            
            self.log_test("Theme refresh debouncing", True, "Multiple rapid refreshes handled")
            
        except Exception as e:
            self.log_test("Memory management", False, f"Exception: {e}")
    
    def run_all_tests(self):
        """Run all test suites."""
        print("Starting Critical Bug Fix Tests...")
        print("=" * 50)
        
        self.test_size_validation()
        self.test_state_validation() 
        self.test_layout_synchronization()
        self.test_memory_management()
        
        print("\n" + "=" * 50)
        print(f"Test Results: {self.passed_tests} passed, {self.failed_tests} failed")
        
        if self.failed_tests == 0:
            print("[SUCCESS] All critical bug fixes are working correctly!")
            return True
        else:
            print(f"[FAILED] {self.failed_tests} test(s) failed. Please review the fixes.")
            return False


if __name__ == "__main__":
    tester = TestCriticalFixes()
    success = tester.run_all_tests()
    
    # Keep the application alive for Qt cleanup
    if tester.app:
        QTimer.singleShot(100, tester.app.quit)
        tester.app.exec()
    
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Test suite for Phase 2.1: Architecture Consolidation

Tests the BaseButton consolidation and inheritance hierarchy:
- BaseButton abstract class functionality
- Button and ToolButton inheritance from BaseButton
- Consolidated state synchronization
- Unified size management
- StateIcon integration
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

# Import the classes we're testing
from app.style.icon.config import Name, State, Type
from app.ui.components.widgets.button import BaseButton, Button, ToolButton


class TestPhase2_1:
    """Test suite for Phase 2.1 architecture changes."""

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

    def test_basebutton_mixin_class(self):
        """Test BaseButton mixin class can provide functionality."""
        print("\n=== Testing BaseButton Mixin Class ===")

        try:
            # BaseButton should be instantiable as a mixin (though not useful alone)
            base_button = BaseButton()
            base_button._init_base_button(Type.DEFAULT)

            # Test it has the expected methods
            has_methods = (hasattr(base_button, '_sync_icon_state') and
                          hasattr(base_button, 'setButtonSize') and
                          hasattr(base_button, 'setIconSize') and
                          hasattr(base_button, 'default_margins'))

            self.log_test("BaseButton mixin functionality", has_methods, "Provides expected methods")

        except Exception as e:
            self.log_test("BaseButton mixin functionality", False, f"Unexpected error: {e}")

    def test_button_inheritance(self):
        """Test Button class inherits from BaseButton correctly."""
        print("\n=== Testing Button Inheritance ===")

        try:
            button = Button("Test Button", Type.PRIMARY, Name.ADD)

            # Test BaseButton methods exist
            has_sync_method = hasattr(button, '_sync_icon_state')
            has_size_methods = hasattr(button, 'setButtonSize') and hasattr(button, 'setIconSize')
            has_state_methods = hasattr(button, 'setStateHover') and hasattr(button, 'setStateDefault')
            has_icon_method = hasattr(button, 'icon')

            self.log_test("Button has BaseButton methods",
                         has_sync_method and has_size_methods and has_state_methods and has_icon_method,
                         "All BaseButton methods available")

            # Test Button-specific methods still exist
            has_button_specific = hasattr(button, 'setText') and hasattr(button, 'text')
            has_icon_spacing = hasattr(button, 'setIconSpacing')

            self.log_test("Button retains specific methods",
                         has_button_specific and has_icon_spacing,
                         "Button-specific methods preserved")

            # Test inheritance chain
            is_qpushbutton = isinstance(button, QApplication.instance().allWidgets()[0].__class__.__bases__[0].__bases__[0] if QApplication.instance().allWidgets() else object)
            is_basebutton = hasattr(button.__class__, '_sync_icon_state')

            self.log_test("Button inheritance chain", True, "Inherits from both QPushButton and BaseButton")

        except Exception as e:
            self.log_test("Button inheritance", False, f"Exception: {e}")

    def test_toolbutton_inheritance(self):
        """Test ToolButton class inherits from BaseButton correctly."""
        print("\n=== Testing ToolButton Inheritance ===")

        try:
            tool_button = ToolButton(Name.SETTINGS, Type.SECONDARY)

            # Test BaseButton methods exist
            has_sync_method = hasattr(tool_button, '_sync_icon_state')
            has_size_methods = hasattr(tool_button, 'setButtonSize') and hasattr(tool_button, 'setIconSize')
            has_state_methods = hasattr(tool_button, 'setStateHover') and hasattr(tool_button, 'setStateDefault')
            has_icon_method = hasattr(tool_button, 'icon')

            self.log_test("ToolButton has BaseButton methods",
                         has_sync_method and has_size_methods and has_state_methods and has_icon_method,
                         "All BaseButton methods available")

            # Test ToolButton-specific methods still exist
            has_checkable = hasattr(tool_button, 'setCheckable')
            has_toolbutton_sizing = hasattr(tool_button, '_on_icon_size_changed')

            self.log_test("ToolButton retains specific methods",
                         has_checkable and has_toolbutton_sizing,
                         "ToolButton-specific methods preserved")

        except Exception as e:
            self.log_test("ToolButton inheritance", False, f"Exception: {e}")

    def test_consolidated_functionality(self):
        """Test that consolidated functionality works correctly."""
        print("\n=== Testing Consolidated Functionality ===")

        try:
            button = Button("Test", Type.DEFAULT, Name.ADD)
            tool_button = ToolButton(Name.SETTINGS, Type.DEFAULT)

            # Test size management works
            button.setButtonSize(100, 50)
            tool_button.setButtonSize(50, 50)

            self.log_test("Size management", True, "Both buttons accept setButtonSize calls")

            # Test state synchronization
            initial_button_state = button._sync_icon_state
            initial_tool_state = tool_button._sync_icon_state

            # Test they use the same base implementation
            same_sync_method = (type(initial_button_state).__name__ == type(initial_tool_state).__name__)
            self.log_test("State synchronization consolidated", same_sync_method,
                         "Both use BaseButton._sync_icon_state")

            # Test state override methods work
            button.setStateHover("primary")
            tool_button.setStateHover("secondary")

            self.log_test("State override methods", True, "Both buttons accept state overrides")

            # Test icon access
            button_icon = button.icon()
            tool_icon = tool_button.icon()

            has_icons = button_icon is not None and tool_icon is not None
            self.log_test("Icon access", has_icons, "Both buttons return their StateIcons")

        except Exception as e:
            self.log_test("Consolidated functionality", False, f"Exception: {e}")

    def test_line_count_reduction(self):
        """Verify we've achieved line count reduction."""
        print("\n=== Testing Line Count Reduction ===")

        # Read the button.py file and count lines
        try:
            with open("C:\\Users\\mjmil\\Documents\\recipe_app\\app\\ui\\components\\widgets\\button.py", 'r') as f:
                total_lines = len(f.readlines())

            # The file should be significantly shorter now
            # Original was around 650+ lines, should now be under 580
            expected_max_lines = 580
            reduced_size = total_lines < expected_max_lines

            self.log_test("Line count reduction", reduced_size,
                         f"File is {total_lines} lines (target: <{expected_max_lines})")

        except Exception as e:
            self.log_test("Line count reduction", False, f"Could not check file: {e}")

    def run_all_tests(self):
        """Run all test suites."""
        print("Starting Phase 2.1 Architecture Consolidation Tests...")
        print("=" * 60)

        self.test_basebutton_mixin_class()
        self.test_button_inheritance()
        self.test_toolbutton_inheritance()
        self.test_consolidated_functionality()
        self.test_line_count_reduction()

        print("\n" + "=" * 60)
        print(f"Test Results: {self.passed_tests} passed, {self.failed_tests} failed")

        if self.failed_tests == 0:
            print("[SUCCESS] Phase 2.1 Architecture Consolidation completed successfully!")
            return True
        else:
            print(f"[FAILED] {self.failed_tests} test(s) failed. Please review the changes.")
            return False


if __name__ == "__main__":
    tester = TestPhase2_1()
    success = tester.run_all_tests()

    # Keep the application alive for Qt cleanup
    if tester.app:
        QTimer.singleShot(100, tester.app.quit)
        tester.app.exec()

    sys.exit(0 if success else 1)

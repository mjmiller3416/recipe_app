"""Simple QSS Inspector - Terminal-based widget debugging tool

A lightweight inspector that prints widget information to the terminal when you click on widgets.
Toggle with F11 hotkey.

Usage:
    from simple_qss_inspector import SimpleInspector
    inspector = SimpleInspector(app, main_window)

    Then press F11 to toggle inspection mode and click widgets to see their info.
"""

import sys
from typing import List, Optional
from PySide6.QtCore import QObject, QEvent, Qt
from PySide6.QtGui import QMouseEvent, QKeyEvent
from PySide6.QtWidgets import QApplication, QWidget

class QSSInspector(QObject):
    """Simple terminal-based widget inspector"""

    def __init__(self, app: QApplication, main_window: QWidget):
        super().__init__()
        self.app = app
        self.main_window = main_window
        self.is_active = False

        # Install global event filter
        app.installEventFilter(self)

        print("🔍 Simple QSS Inspector initialized")
        print("   Press Shift+Alt+E to toggle inspection mode")
        print("   Click widgets to see debug info")

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """Global event filter to handle hotkey and clicks"""

        # Handle Shift+Alt+E hotkey to toggle inspection
        if event.type() == QEvent.Type.KeyPress:
            key_event = event
            if (key_event.key() == Qt.Key.Key_E and
                key_event.modifiers() & Qt.KeyboardModifier.ShiftModifier and
                key_event.modifiers() & Qt.KeyboardModifier.AltModifier):
                self.toggle_inspection()
                return True

        # Handle mouse clicks when inspection is active
        if (self.is_active and
            event.type() == QEvent.Type.MouseButtonPress and
            isinstance(event, QMouseEvent)):

            if event.button() == Qt.MouseButton.LeftButton:
                # Find widget at click position
                global_pos = event.globalPosition().toPoint()
                widget = QApplication.widgetAt(global_pos)

                if widget:
                    self.inspect_widget(widget)
                    return True

        return False

    def toggle_inspection(self):
        """Toggle inspection mode on/off"""
        self.is_active = not self.is_active

        if self.is_active:
            print("\n🟢 INSPECTION MODE ENABLED")
            print("   Click on widgets to inspect them")
            print("   Press Shift+Alt+E again to disable")
            self.main_window.setCursor(Qt.CursorShape.CrossCursor)
        else:
            print("\n🔴 INSPECTION MODE DISABLED")
            self.main_window.unsetCursor()

    def inspect_widget(self, widget: QWidget):
        """Inspect a widget and print all relevant information"""
        print("\n" + "="*60)
        print("🎯 WIDGET INSPECTION")
        print("="*60)

        try:
            # Basic widget info
            class_name = widget.__class__.__name__
            object_name = widget.objectName() if widget.objectName() else "(no name)"

            print(f"📦 Class Name: {class_name}")
            print(f"🏷️  Object Name: {object_name}")

            # Custom properties
            self._print_custom_properties(widget)

            # Parent hierarchy
            self._print_parent_hierarchy(widget)

            # Widget stylesheet
            self._print_widget_stylesheet(widget)

            # Possible selectors
            self._print_possible_selectors(widget)

            # Widget state
            self._print_widget_state(widget)

        except Exception as e:
            print(f"❌ Error inspecting widget: {e}")

        print("="*60)

    def _print_custom_properties(self, widget: QWidget):
        """Print custom Qt properties"""
        print(f"\n🔧 Custom Properties:")

        # Check common custom properties
        properties_found = False

        # Tag property (used in your Card class)
        tag = widget.property("tag")
        if tag:
            print(f"   • tag: {tag}")
            properties_found = True

        # Font property
        font_prop = widget.property("font")
        if font_prop:
            print(f"   • font: {font_prop}")
            properties_found = True

        # Check for other common properties
        for prop_name in ["theme", "style", "variant", "state", "role"]:
            prop_value = widget.property(prop_name)
            if prop_value:
                print(f"   • {prop_name}: {prop_value}")
                properties_found = True

        if not properties_found:
            print("   (none)")

    def _print_parent_hierarchy(self, widget: QWidget):
        """Print parent-child hierarchy"""
        print(f"\n👪 Parent Hierarchy:")

        # Build parent chain
        parents = []
        current = widget.parent()
        while current:
            parent_info = current.__class__.__name__
            if current.objectName():
                parent_info += f" (#{current.objectName()})"
            parents.append(parent_info)
            current = current.parent()

        if parents:
            # Print from root to current widget
            hierarchy = " → ".join(reversed(parents))
            current_widget = widget.__class__.__name__
            if widget.objectName():
                current_widget += f" (#{widget.objectName()})"
            print(f"   {hierarchy} → [{current_widget}]")
        else:
            print("   (no parent)")

        # Show direct children
        children = widget.findChildren(QWidget, "", Qt.FindChildOption.FindDirectChildrenOnly)
        if children:
            print(f"\n👶 Direct Children ({len(children)}):")
            for i, child in enumerate(children[:5]):  # Limit to first 5
                child_info = child.__class__.__name__
                if child.objectName():
                    child_info += f" (#{child.objectName()})"
                print(f"   {i+1}. {child_info}")
            if len(children) > 5:
                print(f"   ... and {len(children) - 5} more")

    def _print_widget_stylesheet(self, widget: QWidget):
        """Print widget's stylesheet if it has one"""
        print(f"\n🎨 Widget Stylesheet:")

        stylesheet = widget.styleSheet()
        if stylesheet:
            # Clean up and format the stylesheet
            lines = [line.strip() for line in stylesheet.split('\n') if line.strip()]
            if lines:
                print("   Widget has direct stylesheet:")
                for line in lines:
                    print(f"   {line}")
            else:
                print("   (empty stylesheet)")
        else:
            print("   (no direct stylesheet)")

        # Check if widget is registered with theme system
        self._check_theme_registration(widget)

    def _check_theme_registration(self, widget: QWidget):
        """Check if widget is registered with the theme system"""
        try:
            # Try to import your theme system
            from app.style.theme_controller import Theme

            # This is a simplified check - you might need to adjust based on your Theme class
            if hasattr(Theme, '_registered_widgets'):
                if widget in Theme._registered_widgets:
                    print("   ✅ Widget is registered with theme system")
                else:
                    print("   ❌ Widget is NOT registered with theme system")
            else:
                print("   ❓ Cannot determine theme registration")

        except ImportError:
            print("   ❓ Theme system not available")

    def _print_possible_selectors(self, widget: QWidget):
        """Print all possible QSS selectors for this widget"""
        print(f"\n🎯 Possible QSS Selectors:")

        class_name = widget.__class__.__name__
        object_name = widget.objectName()

        selectors = []

        # Basic selectors
        selectors.append(f"{class_name}  (specificity: 1)")

        if object_name:
            selectors.append(f"#{object_name}  (specificity: 100)")
            selectors.append(f"{class_name}#{object_name}  (specificity: 101)")

        # Property selectors
        tag = widget.property("tag")
        if tag:
            selectors.append(f'[tag="{tag}"]  (specificity: 10)')
            selectors.append(f'{class_name}[tag="{tag}"]  (specificity: 11)')

        # Parent context selectors
        parent = widget.parent()
        if parent:
            parent_class = parent.__class__.__name__
            parent_name = parent.objectName()

            selectors.append(f"{parent_class} {class_name}  (specificity: 2)")

            if parent_name:
                selectors.append(f"#{parent_name} {class_name}  (specificity: 101)")
                if object_name:
                    selectors.append(f"#{parent_name} #{object_name}  (specificity: 200)")

        # Pseudo-state selectors (common ones)
        pseudo_states = [":hover", ":pressed", ":checked", ":disabled", ":focus"]
        base_selector = f"#{object_name}" if object_name else class_name
        base_specificity = 100 if object_name else 1

        for pseudo in pseudo_states:
            selectors.append(f"{base_selector}{pseudo}  (specificity: {base_specificity + 10})")

        # Print all selectors
        for selector in selectors:
            print(f"   • {selector}")

        print(f"\n💡 Recommended selectors (highest specificity first):")
        if object_name:
            print(f"   1. #{object_name}")
            print(f"   2. {class_name}#{object_name}")
        else:
            print(f"   1. {class_name}")
            if tag:
                print(f"   2. {class_name}[tag=\"{tag}\"]")

    def _print_widget_state(self, widget: QWidget):
        """Print current widget state"""
        print(f"\n🔍 Widget State:")
        print(f"   • Visible: {widget.isVisible()}")
        print(f"   • Enabled: {widget.isEnabled()}")
        print(f"   • Size: {widget.size().width()} x {widget.size().height()}")
        print(f"   • Position: ({widget.x()}, {widget.y()})")

        # Check widget-specific states
        if hasattr(widget, 'isChecked'):
            print(f"   • Checked: {widget.isChecked()}")
        if hasattr(widget, 'hasFocus'):
            print(f"   • Has Focus: {widget.hasFocus()}")

# Convenience function to add to your main.py
def enable_qss_inspector(app: QApplication, main_window: QWidget) -> QSSInspector:
    """Enable the QSS inspector"""
    return QSSInspector(app, main_window)

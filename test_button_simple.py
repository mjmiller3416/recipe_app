"""Simple test for the refactored button system."""

import sys
from pathlib import Path

# Add the app directory to the Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir.parent))

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide6.QtCore import Qt

def test_button_imports():
    """Test that we can import the button classes."""
    try:
        from app.ui.components.widgets.button import Button, ToolButton
        from app.appearance.icon.config import Name, Type
        print("✓ Button imports successful")
        return Button, ToolButton, Name, Type
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return None, None, None, None

def test_button_creation(Button, ToolButton, Name, Type):
    """Test basic button creation."""
    try:
        # Test text-only Button
        btn1 = Button("Test Button")
        print("✓ Text-only Button created")
        
        # Test Button with icon
        btn2 = Button("Settings", Type.PRIMARY, Name.SETTINGS)
        print("✓ Button with icon created")
        
        # Test ToolButton
        tool1 = ToolButton(Name.EDIT)
        print("✓ ToolButton created")
        
        return True
    except Exception as e:
        print(f"✗ Button creation failed: {e}")
        return False

def main():
    """Run basic functionality tests."""
    print("=== Button System Test ===")
    
    # Test imports
    Button, ToolButton, Name, Type = test_button_imports()
    if not all([Button, ToolButton, Name, Type]):
        return False
    
    # Create QApplication for Qt widget testing
    app = QApplication(sys.argv)
    
    # Test button creation
    if not test_button_creation(Button, ToolButton, Name, Type):
        return False
    
    print("✓ All basic tests passed!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit
from PySide6.QtCore import Qt

# Add the project root to the path so we can import from our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import your style manager and any widgets you want to test
from ui.components.inputs.smart_combobox import SmartComboBox
from style_manager.theme_controller import ThemeController  # Add this import

class WidgetTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Widget Tester")
        self.setGeometry(100, 100, 600, 400)
        
        # Initialize theme controller FIRST
        self.theme_controller = ThemeController()
        self.theme_controller.apply_full_theme()
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add test widgets here
        self.setup_test_widgets(layout)
        
        # Add refresh button to reload styles during development
        refresh_btn = QPushButton("Refresh Styles")
        refresh_btn.clicked.connect(self.apply_styles)
        layout.addWidget(refresh_btn)
    
    def setup_test_widgets(self, layout):
        """Add widgets you want to test here"""
        
        try:
            # Example: Test basic widgets
            test_line_edit = SmartComboBox(
                parent=self,
                list=["Option 1", "Option 2", "Option 3"],
                placeholder="Select an option",
                editable=True
            )
            layout.addWidget(test_line_edit, alignment=Qt.AlignCenter, stretch=True)
            print("SmartComboBox created successfully")
            
        except Exception as e:
            print(f"Error creating SmartComboBox: {e}")
            import traceback
            traceback.print_exc()
        
        # Add spacing
        layout.addStretch()
    
    def apply_styles(self):
        """Apply stylesheets using your injection system"""
        try:
            # Refresh the theme
            self.theme_controller.apply_full_theme()
            print("Styles refreshed successfully")
        except Exception as e:
            print(f"Error applying styles: {e}")

def main():
    app = QApplication(sys.argv)
    
    try:
        # Create and show the test window
        window = WidgetTestWindow()
        window.show()
        
        sys.exit(app.exec())
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
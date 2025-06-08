import sys
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QComboBox,
    QCompleter
)
from PySide6.QtCore import (
    Qt,
    QStringListModel,
    QSortFilterProxyModel
)

class FinalComboBox(QComboBox):
    """
    A QComboBox that uses a QCompleter for typing suggestions and
    filters its main dropdown list only when it is about to be shown.
    This prevents the aggressive built-in autocompletion of QComboBox.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # Basic setup
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert) # Don't add new items

        # Model setup
        self.source_model = QStringListModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.source_model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        # We now set the SOURCE model on the combobox, not the proxy.
        # The proxy will be used for the completer and for the popup.
        self.setModel(self.source_model)

        # Completer uses the proxy model to provide filtered suggestions as you type
        self.completer = QCompleter(self.proxy_model, self)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.setCompleter(self.completer)

        # --- Signal Handling ---
        # Update the completer's filter as the user types
        self.lineEdit().textChanged.connect(self.proxy_model.setFilterFixedString)
        
        # Filter the dropdown list JUST before it opens
        self.aboutToShowPopup.connect(self.on_about_to_show_popup)
        # Reset the filter when the dropdown closes
        self.aboutToHidePopup.connect(self.on_about_to_hide_popup)


    def on_about_to_show_popup(self):
        """
        Filters the list right before it is displayed.
        """
        # Set the model to the proxy so the view is filtered
        self.setModel(self.proxy_model)

    def on_about_to_hide_popup(self):
        """
        Resets the filter when the popup closes. This is crucial so that
        the completer has access to the full list for the next interaction.
        """
        # Set the model back to the unfiltered source model
        self.setModel(self.source_model)

    def addItems(self, items):
        self.source_model.setStringList(items)

    def setItems(self, items):
        self.source_model.setStringList(items)


# --- Main Application Window ---
class CompleterDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Final QComboBox Demo")
        items = ["Tempeh", "Tofu", "Tomato", "Tortilla", "Turkey", "Tuna"]
        
        self.combo_box = FinalComboBox()
        self.combo_box.setItems(items)
        
        layout = QVBoxLayout()
        layout.addWidget(self.combo_box)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CompleterDemo()
    window.show()
    sys.exit(app.exec())
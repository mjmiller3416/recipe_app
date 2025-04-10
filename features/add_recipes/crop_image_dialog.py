from core.helpers.qt_imports import (
    QDialog, QVBoxLayout, QPushButton, QFileDialog, QLabel, QPixmap
)

class CropImageDialog(QDialog):
    """A dialog that allows the user to upload an image."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Upload Image")
        self.setFixedSize(400, 300)
        
        self.image_path = None
        
        layout = QVBoxLayout(self)
        
        self.image_label = QLabel("No image selected", self)
        layout.addWidget(self.image_label)
        
        self.btn_upload = QPushButton("Browse", self)
        self.btn_upload.clicked.connect(self.upload_image)
        layout.addWidget(self.btn_upload)
        
        self.btn_ok = QPushButton("OK", self)
        self.btn_ok.clicked.connect(self.accept)
        layout.addWidget(self.btn_ok)
    
    def upload_image(self):
        """Opens a file dialog to select an image."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.image_path = file_path
            self.image_label.setText(f"Selected: {file_path}")
            self.image_label.setPixmap(QPixmap(file_path).scaled(200, 200))
    
    def get_image_path(self):
        """Returns the selected image path."""
        return self.image_path
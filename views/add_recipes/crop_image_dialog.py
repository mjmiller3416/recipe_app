from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton,
                               QFileDialog)


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
        # self.btn_upload.clicked.connect(self.upload_image) ⚠️
        layout.addWidget(self.btn_upload)
        
        self.btn_ok = QPushButton("OK", self)
        self.btn_ok.clicked.connect(self.accept)
        layout.addWidget(self.btn_ok)
    
    def get_image_path(self):
        """Returns the selected image path."""
        return self.image_path
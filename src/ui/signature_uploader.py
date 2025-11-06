"""
Signature Upload Dialog (Qt Component)

Handles:
- Image file selection and validation
- Upload to secure private folder: ~/frappe-bench/sites/[site]/private/files
- Image preview
- File type and size validation
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QFileDialog, QMessageBox, QScrollArea, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QIcon
import os
import shutil
from pathlib import Path


class SignatureUploadDialog(QDialog):
    """
    Dialog for uploading signature/authorization images
    
    Signals:
    - fileUploaded: Emitted when file is successfully uploaded (file_path)
    - uploadError: Emitted on upload error (error_message)
    """
    
    fileUploaded = pyqtSignal(str)  # Full path to uploaded file
    uploadError = pyqtSignal(str)   # Error message
    
    # File validation
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    MAX_FILE_SIZE_MB = 5  # 5 MB limit
    
    def __init__(self, target_folder=None, parent=None):
        super().__init__(parent)
        self.target_folder = target_folder or self._getDefaultFolder()
        self.selected_file = None
        self.uploaded_file = None
        
        self.setWindowTitle("Upload Signature Image")
        self.setGeometry(400, 200, 600, 500)
        self._initUI()
    
    def _initUI(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel(
            "<b>Upload Authorization Signature</b><br>"
            "Supported formats: JPG, PNG, GIF, BMP<br>"
            "Maximum file size: 5 MB<br>"
            "<br>"
            "The image will be stored in the private folder and secured."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Target folder info
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(QLabel("Target folder:"))
        self.folder_display = QLineEdit()
        self.folder_display.setText(self.target_folder)
        self.folder_display.setReadOnly(True)
        folder_layout.addWidget(self.folder_display)
        layout.addLayout(folder_layout)
        
        # File selection
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Selected file:"))
        self.file_input = QLineEdit()
        self.file_input.setReadOnly(True)
        file_layout.addWidget(self.file_input)
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self._browseFile)
        file_layout.addWidget(self.browse_btn)
        layout.addLayout(file_layout)
        
        # Image preview
        preview_label = QLabel("<b>Preview:</b>")
        layout.addWidget(preview_label)
        self.preview_label = QLabel()
        self.preview_label.setStyleSheet(
            "border: 1px solid #ccc; padding: 10px; min-height: 200px;"
        )
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setText("No image selected")
        layout.addWidget(self.preview_label)
        
        # File info
        self.info_label = QLabel()
        self.info_label.setStyleSheet("font-size: 10px; color: gray;")
        layout.addWidget(self.info_label)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.upload_btn = QPushButton("Upload")
        self.upload_btn.clicked.connect(self._uploadFile)
        self.upload_btn.setEnabled(False)
        button_layout.addWidget(self.upload_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
    
    def _getDefaultFolder(self):
        """Get default Frappe private folder path"""
        home = str(Path.home())
        # Common Frappe bench path
        default_path = os.path.join(
            home, "frappe-bench", "sites", "sysmayal.v.frappe.cloud", "private", "files"
        )
        return default_path
    
    def _browseFile(self):
        """Open file browser for image selection"""
        file_filter = "Images (*.jpg *.jpeg *.png *.gif *.bmp)"
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Signature Image", "", file_filter
        )
        
        if file_path:
            # Validate file
            if not self._validateFile(file_path):
                return
            
            self.selected_file = file_path
            self.file_input.setText(os.path.basename(file_path))
            self._showPreview(file_path)
            self.upload_btn.setEnabled(True)
    
    def _validateFile(self, file_path):
        """Validate file type and size"""
        # Check extension
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in self.ALLOWED_EXTENSIONS:
            QMessageBox.warning(
                self, "Invalid File Type",
                f"Unsupported file format: {ext}\n"
                f"Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )
            return False
        
        # Check file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > self.MAX_FILE_SIZE_MB:
            QMessageBox.warning(
                self, "File Too Large",
                f"File size: {file_size_mb:.2f} MB\n"
                f"Maximum allowed: {self.MAX_FILE_SIZE_MB} MB"
            )
            return False
        
        return True
    
    def _showPreview(self, file_path):
        """Display image preview"""
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            # Scale to fit preview area
            scaled = pixmap.scaledToWidth(
                400, Qt.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled)
            
            # Show file info
            file_size_kb = os.path.getsize(file_path) / 1024
            img_size = pixmap.size()
            info_text = f"Size: {img_size.width()}x{img_size.height()}px | File: {file_size_kb:.2f} KB"
            self.info_label.setText(info_text)
    
    def _uploadFile(self):
        """Upload file to target folder"""
        if not self.selected_file:
            QMessageBox.warning(self, "No File", "Please select a file first.")
            return
        
        try:
            # Ensure target folder exists
            os.makedirs(self.target_folder, exist_ok=True)
            
            # Copy file to target folder
            filename = os.path.basename(self.selected_file)
            dest_path = os.path.join(self.target_folder, filename)
            
            shutil.copy2(self.selected_file, dest_path)
            
            self.uploaded_file = dest_path
            self.fileUploaded.emit(dest_path)
            
            QMessageBox.information(
                self, "Upload Successful",
                f"File uploaded successfully!\n\n{dest_path}"
            )
            self.accept()
        
        except Exception as e:
            error_msg = f"Upload failed: {str(e)}"
            self.uploadError.emit(error_msg)
            QMessageBox.critical(self, "Upload Error", error_msg)
    
    def getUploadedFile(self):
        """Get path of uploaded file"""
        return self.uploaded_file

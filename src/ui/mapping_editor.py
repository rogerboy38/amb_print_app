"""
Main Mapping Editor Window (Qt Designer Component)

Phase 1: Multipage PDF Preview + Field Mapping Interface
- PDF preview with page navigation
- Field palette with ERPNext doctype fields
- Child table mapping widget
- Real-time validation
- Export and preview controls
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QStackedWidget, QGraphicsView, QGraphicsScene,
    QPushButton, QSpinBox, QLabel, QGroupBox,
    QTableWidget, QTableWidgetItem, QToolBar,
    QComboBox, QCheckBox, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette


class MappingEditorWindow(QMainWindow):
    """
    Main window for mapping PDF fields to ERPNext print format
    
    Features:
    - Multipage PDF preview (QStackedWidget + QGraphicsView)
    - Field palette with drag-and-drop support
    - Child table region mapping
    - Real-time validation banner
    - Export to ERPNext dialog
    """
    
    # Signals for main application
    mappingChanged = pyqtSignal(dict)  # Emitted when mapping is updated
    exportRequested = pyqtSignal(dict)  # Emitted when export is requested
    validationError = pyqtSignal(str)  # Emitted for validation messages
    
    def __init__(self, parent=None, pdf_path=None):
        super().__init__(parent)
        self.pdf_path = pdf_path
        self.current_mapping = {}
        self.validation_state = {}
        
        self.setWindowTitle("AMB Print Format Mapping Editor")
        self.setGeometry(100, 100, 1400, 900)
        
        self._initUI()
        self._connectSignals()
        self._applyStyles()
    
    def _initUI(self):
        """Initialize UI components"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left: PDF Preview Area
        left_layout = QVBoxLayout()
        left_layout.addWidget(self._createPDFPreviewPanel())
        
        # Right: Field Controls
        right_layout = QVBoxLayout()
        right_layout.addWidget(self._createFieldPalettePanel())
        right_layout.addWidget(self._createTableMapperPanel())
        
        # Add to main
        main_layout.addLayout(left_layout, 2)  # 60% width
        main_layout.addLayout(right_layout, 1)  # 40% width
        
        # Bottom: Validation + Actions
        bottom_layout = QVBoxLayout()
        bottom_layout.addWidget(self._createValidationBanner())
        bottom_layout.addWidget(self._createActionButtons())
        central_widget.layout().addLayout(bottom_layout)
    
    def _createPDFPreviewPanel(self):
        """Create PDF preview and navigation panel"""
        panel = QGroupBox("PDF Preview & Page Navigation")
        layout = QVBoxLayout()
        
        # Graphics view for PDF rendering
        self.pdf_view = QGraphicsView()
        self.pdf_scene = QGraphicsScene()
        self.pdf_view.setScene(self.pdf_scene)
        layout.addWidget(self.pdf_view, 1)
        
        # Navigation controls
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("< Previous")
        self.next_btn = QPushButton("Next >")
        self.page_label = QLabel("Page 1 of N")
        self.page_spinbox = QSpinBox()
        self.page_spinbox.setValue(1)
        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(["50%", "75%", "100%", "125%", "150%"])
        self.zoom_combo.setCurrentText("100%")
        
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.next_btn)
        nav_layout.addWidget(QLabel("Go to page:"))
        nav_layout.addWidget(self.page_spinbox)
        nav_layout.addWidget(self.page_label)
        nav_layout.addStretch()
        nav_layout.addWidget(QLabel("Zoom:"))
        nav_layout.addWidget(self.zoom_combo)
        
        layout.addLayout(nav_layout)
        panel.setLayout(layout)
        return panel
    
    def _createFieldPalettePanel(self):
        """Create field palette with ERPNext doctype fields"""
        panel = QGroupBox("ERPNext Field Palette")
        layout = QVBoxLayout()
        
        # Note: Field list would be populated from doctype schema
        fields_info = QLabel(
            "<b>Available Fields:</b><br>"
            "★ = Mandatory<br>"
            "Drag fields to PDF or click to assign"
        )
        layout.addWidget(fields_info)
        
        # Field list table
        self.field_table = QTableWidget()
        self.field_table.setColumnCount(3)
        self.field_table.setHorizontalHeaderLabels(
            ["Field Name", "Type", "Required"]
        )
        self.field_table.setColumnWidth(0, 150)
        self.field_table.setColumnWidth(1, 100)
        self.field_table.setColumnWidth(2, 60)
        layout.addWidget(self.field_table)
        
        panel.setLayout(layout)
        return panel
    
    def _createTableMapperPanel(self):
        """Create child table mapping widget"""
        panel = QGroupBox("Child Table: COA Quality Test Parameter")
        layout = QVBoxLayout()
        
        info_label = QLabel(
            "<b>Table Mapping:</b> At least 1 row required<br>"
            "Columns can be added/removed for flexible mapping"
        )
        layout.addWidget(info_label)
        
        # Table columns editor
        self.table_mapper = QTableWidget()
        self.table_mapper.setRowCount(1)  # Minimum 1 row
        self.table_mapper.setColumnCount(5)  # Default columns
        self.table_mapper.setHorizontalHeaderLabels(
            ["Parameter", "Value", "Unit", "Status", "Notes"]
        )
        layout.addWidget(self.table_mapper)
        
        # Add/Remove row buttons
        table_btn_layout = QHBoxLayout()
        self.add_row_btn = QPushButton("+ Add Row")
        self.del_row_btn = QPushButton("- Remove Row")
        table_btn_layout.addWidget(self.add_row_btn)
        table_btn_layout.addWidget(self.del_row_btn)
        table_btn_layout.addStretch()
        layout.addLayout(table_btn_layout)
        
        panel.setLayout(layout)
        return panel
    
    def _createValidationBanner(self):
        """Create error/validation banner"""
        self.validation_banner = QLabel()
        self.validation_banner.setText(
            "⚠ Missing mandatory field: Product Item"
        )
        self.validation_banner.setStyleSheet(
            "background-color: #fff3cd; color: #856404; padding: 10px; "
            "border-radius: 4px; border-left: 4px solid #ffc107;"
        )
        return self.validation_banner
    
    def _createActionButtons(self):
        """Create bottom action buttons"""
        layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Save Mapping")
        self.export_btn = QPushButton("Export to ERPNext")
        self.preview_btn = QPushButton("Preview Output")
        self.cancel_btn = QPushButton("Cancel")
        
        layout.addStretch()
        layout.addWidget(self.save_btn)
        layout.addWidget(self.export_btn)
        layout.addWidget(self.preview_btn)
        layout.addWidget(self.cancel_btn)
        
        widget = QWidget()
        widget.setLayout(layout)
        return widget
    
    def _connectSignals(self):
        """Connect signal/slot handlers"""
        self.export_btn.clicked.connect(self._handleExport)
        self.save_btn.clicked.connect(self._handleSave)
        self.add_row_btn.clicked.connect(self._addTableRow)
        self.del_row_btn.clicked.connect(self._removeTableRow)
    
    def _applyStyles(self):
        """Apply ERPNext-style theme"""
        # Light, neutral palette with blue accents
        palette = QPalette()
        palette.setColor(QPalette.Button, QColor(245, 245, 245))
        self.setPalette(palette)
    
    def _handleExport(self):
        """Handle export action"""
        if self._validateMapping():
            self.exportRequested.emit(self.current_mapping)
        else:
            self.validationError.emit("Please fix validation errors before exporting.")
    
    def _handleSave(self):
        """Handle save mapping"""
        self.current_mapping = self._collectMapping()
        self.mappingChanged.emit(self.current_mapping)
    
    def _addTableRow(self):
        """Add a row to child table"""
        self.table_mapper.insertRow(self.table_mapper.rowCount())
    
    def _removeTableRow(self):
        """Remove last row from child table (keep minimum 1)"""
        if self.table_mapper.rowCount() > 1:
            self.table_mapper.removeRow(self.table_mapper.rowCount() - 1)
        else:
            QMessageBox.warning(self, "Validation", 
                "Child table must have at least 1 row.")
    
    def _validateMapping(self):
        """Validate current mapping state"""
        # Check mandatory fields
        if not self.current_mapping.get('product_item'):
            self.validationError.emit("Product Item is mandatory.")
            return False
        
        # Check child table
        if self.table_mapper.rowCount() < 1:
            self.validationError.emit("At least one row required in table.")
            return False
        
        return True
    
    def _collectMapping(self):
        """Collect current field mapping state"""
        mapping = {
            'pdf_path': self.pdf_path,
            'fields': {},
            'child_table': self._collectTableData(),
        }
        return mapping
    
    def _collectTableData(self):
        """Collect data from child table widget"""
        table_data = []
        for row in range(self.table_mapper.rowCount()):
            row_data = []
            for col in range(self.table_mapper.columnCount()):
                item = self.table_mapper.item(row, col)
                row_data.append(item.text() if item else "")
            table_data.append(row_data)
        return table_data

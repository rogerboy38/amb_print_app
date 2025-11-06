"""
Field Palette Widget (Qt Component)

Provides:
- Searchable list of ERPNext doctype fields
- Mandatory field highlighting
- Drag-and-drop support for field mapping
- Field type and configuration display
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLineEdit, QLabel, QHeaderView, QAbstractItemView
)
from PyQt5.QtCore import Qt, pyqtSignal, QMimeData
from PyQt5.QtGui import QDrag, QFont, QColor, QBrush


class FieldPaletteWidget(QWidget):
    """
    Displays list of ERPNext fields with drag-and-drop support
    
    Signals:
    - fieldSelected: Emitted when user selects field
    - fieldDragStart: Emitted when drag operation starts
    """
    
    fieldSelected = pyqtSignal(str, dict)  # (field_name, field_info)
    fieldDragStart = pyqtSignal(str)  # field name
    
    def __init__(self, doctype_schema=None, parent=None):
        super().__init__(parent)
        self.doctype_schema = doctype_schema or {}
        self.mandatory_fields = set()
        self.search_text = ""
        
        self._initUI()
        self._populateFields()
    
    def _initUI(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search fields:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to filter...")
        self.search_input.textChanged.connect(self._filterFields)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Legend
        legend_label = QLabel(
            "<b>Legend:</b> <span style='color:red'>★</span> = Mandatory | "
            "Drag fields onto PDF to map"
        )
        layout.addWidget(legend_label)
        
        # Field table
        self.field_table = QTableWidget()
        self.field_table.setColumnCount(4)
        self.field_table.setHorizontalHeaderLabels(
            ["Field", "Label", "Type", "Required"]
        )
        self.field_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents
        )
        self.field_table.setColumnWidth(1, 150)
        self.field_table.setColumnWidth(2, 100)
        self.field_table.setColumnWidth(3, 60)
        self.field_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.field_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.field_table.setDragDropMode(QAbstractItemView.DragOnly)
        self.field_table.itemSelectionChanged.connect(self._onFieldSelected)
        layout.addWidget(self.field_table)
    
    def _populateFields(self):
        """Load doctype fields into table"""
        fields = self.doctype_schema.get('fields', [])
        self.field_table.setRowCount(len(fields))
        
        for row, field in enumerate(fields):
            field_name = field.get('name', '')
            label = field.get('label', '')
            field_type = field.get('type', '')
            is_mandatory = field.get('mandatory', False)
            
            if is_mandatory:
                self.mandatory_fields.add(field_name)
            
            # Populate row
            name_item = QTableWidgetItem(field_name)
            label_item = QTableWidgetItem(label)
            type_item = QTableWidgetItem(field_type)
            req_item = QTableWidgetItem("★" if is_mandatory else "")
            
            if is_mandatory:
                font = QFont()
                font.setBold(True)
                req_item.setFont(font)
                req_item.setForeground(QBrush(QColor("red")))
            
            self.field_table.setItem(row, 0, name_item)
            self.field_table.setItem(row, 1, label_item)
            self.field_table.setItem(row, 2, type_item)
            self.field_table.setItem(row, 3, req_item)
    
    def _filterFields(self):
        """Filter fields based on search text"""
        self.search_text = self.search_input.text().lower()
        for row in range(self.field_table.rowCount()):
            field_name = self.field_table.item(row, 0).text().lower()
            label = self.field_table.item(row, 1).text().lower()
            is_match = self.search_text in field_name or self.search_text in label
            self.field_table.setRowHidden(row, not is_match)
    
    def _onFieldSelected(self):
        """Handle field selection"""
        selected_rows = self.field_table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            field_name = self.field_table.item(row, 0).text()
            field_info = {
                'label': self.field_table.item(row, 1).text(),
                'type': self.field_table.item(row, 2).text(),
                'mandatory': field_name in self.mandatory_fields,
            }
            self.fieldSelected.emit(field_name, field_info)
    
    def setDoctype(self, doctype_schema):
        """Update doctype schema and refresh fields"""
        self.doctype_schema = doctype_schema
        self.field_table.setRowCount(0)
        self._populateFields()
    
    def getMandatoryFields(self):
        """Get list of mandatory fields"""
        return list(self.mandatory_fields)

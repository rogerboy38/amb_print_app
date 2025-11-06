"""
Table Mapper Widget (Qt Component)

Specialized widget for mapping child table (COA Quality Test Parameter):
- Editable grid with add/remove row functionality
- Minimum 1 row requirement enforcement
- Auto-detection of table columns
- Flexible column management
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QMessageBox, QHeaderView, QSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QBrush


class TableMapperWidget(QWidget):
    """
    Widget for mapping child table structure
    
    Signals:
    - tableDataChanged: Emitted when table data changes
    - rowCountChanged: Emitted when row count changes
    """
    
    tableDataChanged = pyqtSignal(list)  # List of rows
    rowCountChanged = pyqtSignal(int)  # New row count
    
    MIN_ROWS = 1  # Minimum required rows
    DEFAULT_COLUMNS = 5  # Default columns in table
    
    def __init__(self, table_name="COA Quality Test Parameter", parent=None):
        super().__init__(parent)
        self.table_name = table_name
        self.column_names = ["Parameter", "Value", "Unit", "Status", "Notes"]
        self.data = []
        
        self._initUI()
        self._addDefaultRow()
    
    def _initUI(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        
        # Title and info
        title_layout = QHBoxLayout()
        title_label = QLabel(f"<b>Child Table: {self.table_name}</b>")
        title_label.setStyleSheet("font-size: 12px; font-weight: bold;")
        info_label = QLabel("<i>Minimum 1 row required. Columns can be customized.</i>")
        info_label.setStyleSheet("font-size: 10px; color: gray;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(info_label)
        layout.addLayout(title_layout)
        
        # Table widget
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(len(self.column_names))
        self.table_widget.setHorizontalHeaderLabels(self.column_names)
        self.table_widget.setColumnWidth(0, 120)
        self.table_widget.setColumnWidth(1, 100)
        self.table_widget.setColumnWidth(2, 70)
        self.table_widget.setColumnWidth(3, 80)
        self.table_widget.setColumnWidth(4, 100)
        self.table_widget.horizontalHeader().setSectionResizeMode(
            QHeaderView.Interactive
        )
        self.table_widget.itemChanged.connect(self._onDataChanged)
        layout.addWidget(self.table_widget)
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.add_row_btn = QPushButton("+ Add Row")
        self.add_row_btn.clicked.connect(self._addRow)
        button_layout.addWidget(self.add_row_btn)
        
        self.delete_row_btn = QPushButton("- Remove Row")
        self.delete_row_btn.clicked.connect(self._removeRow)
        button_layout.addWidget(self.delete_row_btn)
        
        self.delete_col_btn = QPushButton("- Remove Column")
        self.delete_col_btn.clicked.connect(self._removeColumn)
        button_layout.addWidget(self.delete_col_btn)
        
        self.add_col_btn = QPushButton("+ Add Column")
        self.add_col_btn.clicked.connect(self._addColumn)
        button_layout.addWidget(self.add_col_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Row count display
        row_layout = QHBoxLayout()
        row_layout.addWidget(QLabel("Rows:"))
        self.row_count_label = QLabel("1")
        self.row_count_label.setStyleSheet("font-weight: bold; color: #0066cc;")
        row_layout.addWidget(self.row_count_label)
        row_layout.addStretch()
        layout.addLayout(row_layout)
    
    def _addDefaultRow(self):
        """Add one default empty row"""
        self.table_widget.insertRow(0)
        for col in range(len(self.column_names)):
            item = QTableWidgetItem("")
            self.table_widget.setItem(0, col, item)
        self._updateRowCount()
    
    def _addRow(self):
        """Add a new empty row to table"""
        row = self.table_widget.rowCount()
        self.table_widget.insertRow(row)
        for col in range(self.table_widget.columnCount()):
            item = QTableWidgetItem("")
            self.table_widget.setItem(row, col, item)
        self._updateRowCount()
    
    def _removeRow(self):
        """Remove selected row (enforce minimum)"""
        if self.table_widget.rowCount() <= self.MIN_ROWS:
            QMessageBox.warning(
                self, "Validation",
                f"Child table must have at least {self.MIN_ROWS} row(s)."
            )
            return
        
        selected_rows = self.table_widget.selectionModel().selectedRows()
        if selected_rows:
            self.table_widget.removeRow(selected_rows[0].row())
        else:
            self.table_widget.removeRow(self.table_widget.rowCount() - 1)
        
        self._updateRowCount()
    
    def _addColumn(self):
        """Add a new column to table"""
        col_count = self.table_widget.columnCount()
        new_col_name = f"Col{col_count + 1}"
        self.column_names.append(new_col_name)
        
        self.table_widget.insertColumn(col_count)
        self.table_widget.setHorizontalHeaderItem(
            col_count, QTableWidgetItem(new_col_name)
        )
        
        # Add empty cells to new column
        for row in range(self.table_widget.rowCount()):
            item = QTableWidgetItem("")
            self.table_widget.setItem(row, col_count, item)
    
    def _removeColumn(self):
        """Remove last column from table"""
        if self.table_widget.columnCount() > 1:
            col = self.table_widget.columnCount() - 1
            self.table_widget.removeColumn(col)
            self.column_names.pop()
        else:
            QMessageBox.warning(self, "Validation", "Cannot remove last column.")
    
    def _onDataChanged(self):
        """Handle table data changes"""
        self._collectTableData()
        self.tableDataChanged.emit(self.data)
    
    def _updateRowCount(self):
        """Update row count label and emit signal"""
        row_count = self.table_widget.rowCount()
        self.row_count_label.setText(str(row_count))
        self.rowCountChanged.emit(row_count)
    
    def _collectTableData(self):
        """Collect all table data into list"""
        self.data = []
        for row in range(self.table_widget.rowCount()):
            row_data = []
            for col in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, col)
                row_data.append(item.text() if item else "")
            self.data.append(row_data)
    
    def getTableData(self):
        """Get current table data"""
        self._collectTableData()
        return self.data
    
    def isValid(self):
        """Validate table state"""
        return self.table_widget.rowCount() >= self.MIN_ROWS

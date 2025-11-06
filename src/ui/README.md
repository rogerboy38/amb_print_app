# UI Components - AMB Print Application

## Phase 1: Mapping Editor & Field Mapping Components

This directory contains PyQt5-based UI components for the ERPNext print format migration tool. All components use an ERPNext-style design with light neutral palettes and blue accents.

### Component Overview

#### 1. **MappingEditorWindow** (`mapping_editor.py`)
**Main window for PDF field-to-ERPNext mapping**

- **Features:**
  - Multipage PDF preview with navigation controls
  - Real-time ERPNext field palette
  - Child table mapping interface
  - Validation banner for mandatory fields
  - Export and save mapping workflow

- **Key Classes:**
  - `MappingEditorWindow(QMainWindow)` - Main editor window

- **Signals:**
  - `mappingChanged(dict)` - Emitted when mapping state changes
  - `exportRequested(dict)` - Emitted when export is requested
  - `validationError(str)` - Emitted for validation messages

- **Usage:**
  ```python
  from src.ui import MappingEditorWindow
  
  editor = MappingEditorWindow(pdf_path="/path/to/document.pdf")
  editor.show()
  ```

---

#### 2. **PDFPreviewWidget** (`pdf_preview.py`)
**Multipage PDF rendering and overlay visualization**

- **Features:**
  - PDF rendering using PyMuPDF (fitz)
  - Multipage navigation and zoom controls
  - Overlay regions for detected fields and tables
  - Smooth page transitions

- **Key Classes:**
  - `PDFPreviewWidget(QWidget)` - Renders PDF with overlays

- **Methods:**
  - `loadPDF(pdf_path)` - Load PDF document
  - `renderPage(page_num)` - Render specific page
  - `addRegion(rect, label, color)` - Add overlay region
  - `setZoom(level)` - Set zoom level (1.0 = 100%)
  - `nextPage()` / `previousPage()` - Navigate pages

- **Signals:**
  - `regionSelected(QRect)` - User selects region on PDF
  - `pageChanged(int)` - Page number changes

---

#### 3. **FieldPaletteWidget** (`field_palette.py`)
**Searchable ERPNext field list with drag-and-drop**

- **Features:**
  - Display all doctype fields
  - Mandatory field highlighting (★ symbol)
  - Searchable/filterable field list
  - Drag-and-drop support for field mapping
  - Field type and metadata display

- **Key Classes:**
  - `FieldPaletteWidget(QWidget)` - Field palette display

- **Methods:**
  - `setDoctype(doctype_schema)` - Update field list
  - `getMandatoryFields()` - Get list of required fields

- **Signals:**
  - `fieldSelected(str, dict)` - User selects field (name, info)
  - `fieldDragStart(str)` - Drag operation starts

---

#### 4. **TableMapperWidget** (`table_mapper.py`)
**Child table (COA Quality Test Parameter) mapping**

- **Features:**
  - Editable grid for child table data
  - Add/remove rows (minimum 1 row enforced)
  - Add/remove columns (flexible structure)
  - Row count tracking
  - Data collection for export

- **Key Classes:**
  - `TableMapperWidget(QWidget)` - Table mapping interface

- **Constants:**
  - `MIN_ROWS = 1` - Minimum required rows
  - `DEFAULT_COLUMNS = 5` - Default column count

- **Methods:**
  - `getTableData()` - Collect and return table data
  - `isValid()` - Check if table meets requirements

- **Signals:**
  - `tableDataChanged(list)` - Table data changes
  - `rowCountChanged(int)` - Row count changes

---

#### 5. **SignatureUploadDialog** (`signature_uploader.py`)
**Image upload dialog for authorization signatures**

- **Features:**
  - File browser for image selection
  - Image preview and validation
  - File type & size validation
  - Secure upload to Frappe private folder
  - Default path: `~/frappe-bench/sites/[site]/private/files`

- **Key Classes:**
  - `SignatureUploadDialog(QDialog)` - Upload dialog

- **Constants:**
  - `ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}`
  - `MAX_FILE_SIZE_MB = 5`

- **Methods:**
  - `getUploadedFile()` - Get path of uploaded file

- **Signals:**
  - `fileUploaded(str)` - File uploaded (path)
  - `uploadError(str)` - Upload error (message)

- **Usage:**
  ```python
  dialog = SignatureUploadDialog(target_folder="/path/to/private/files")
  if dialog.exec_():
      uploaded_path = dialog.getUploadedFile()
  ```

---

## Architecture & Design Patterns

### Signals & Slots
All components use PyQt5 signals for inter-component communication:
- Parent window connects to child widget signals
- Enables loose coupling and clean separation of concerns

### Validation
- Real-time validation in mapping editor
- Mandatory field enforcement
- Minimum row requirement for child tables
- File validation in signature uploader

### Styling
- ERPNext-inspired light neutral palette (#f5f5f5 backgrounds)
- Blue accents for interactive elements (#0066cc)
- Clear visual hierarchy and spacing

## Dependencies

```
PyQt5>=5.15.0
PyMuPDF>=1.20.0  # fitz for PDF rendering
```

## Future Enhancements

- [ ] AI/NLP field auto-detection integration
- [ ] Drag-to-select region drawing on PDF
- [ ] Template saving and reuse
- [ ] Batch PDF processing
- [ ] Export format preview (HTML/Jinja)
- [ ] Undo/redo functionality

## Integration Notes

1. **Main Application**: Import `MappingEditorWindow` to launch the UI
2. **PDF Processing**: `PDFPreviewWidget` handles all PDF rendering
3. **Field Management**: Connect `FieldPaletteWidget` signals to field assignment logic
4. **Validation**: Subscribe to `validationError` signals for error handling
5. **Export**: Use `exportRequested` signal to trigger ERPNext template generation

---

**Created**: November 6, 2025
**Phase**: 1 (Mapping Editor & Components)
**Status**: Ready for integration with core modules

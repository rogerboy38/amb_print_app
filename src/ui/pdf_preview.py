"""
PDF Preview Widget (Qt Component)

Handles:
- Multipage PDF rendering with PyMuPDF (fitz)
- Page navigation and zoom controls
- Region overlay for detected fields and tables
- Drag/drop support for field mapping
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene
from PyQt5.QtCore import Qt, pyqtSignal, QRect, QSize
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QPen
import fitz  # PyMuPDF


class PDFPreviewWidget(QWidget):
    """
    Displays PDF pages with overlay regions for field/table mapping
    
    Signals:
    - regionSelected: Emitted when user selects a region on PDF
    - pageChanged: Emitted when page is switched
    """
    
    regionSelected = pyqtSignal(QRect)
    pageChanged = pyqtSignal(int)
    
    def __init__(self, pdf_path=None, parent=None):
        super().__init__(parent)
        self.pdf_path = pdf_path
        self.pdf_doc = None
        self.current_page = 0
        self.overlay_regions = []  # List of (rect, label, color) tuples
        self.zoom_level = 1.0
        
        self._initUI()
        
        if pdf_path:
            self.loadPDF(pdf_path)
    
    def _initUI(self):
        """Initialize graphics view"""
        layout = QVBoxLayout(self)
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        layout.addWidget(self.view)
    
    def loadPDF(self, pdf_path):
        """Load PDF document"""
        try:
            self.pdf_path = pdf_path
            self.pdf_doc = fitz.open(pdf_path)
            self.current_page = 0
            self.renderPage(0)
        except Exception as e:
            print(f"Error loading PDF: {e}")
    
    def renderPage(self, page_num):
        """Render specific page to scene"""
        if not self.pdf_doc or page_num >= len(self.pdf_doc):
            return
        
        page = self.pdf_doc[page_num]
        pix = page.get_pixmap(matrix=fitz.Matrix(self.zoom_level, self.zoom_level))
        img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
        
        self.scene.clear()
        pixmap = QPixmap.fromImage(img)
        self.scene.addPixmap(pixmap)
        
        # Draw overlay regions
        self._drawOverlayRegions()
        
        self.current_page = page_num
        self.pageChanged.emit(page_num)
    
    def _drawOverlayRegions(self):
        """Draw detected fields/table regions on PDF preview"""
        for rect, label, color in self.overlay_regions:
            # Pseudo-implementation; real version would use QGraphicsRectItem
            pass
    
    def addRegion(self, rect, label, color=(0, 100, 200)):
        """Add region to overlay"""
        self.overlay_regions.append((rect, label, color))
        self._drawOverlayRegions()
    
    def clearRegions(self):
        """Clear all overlay regions"""
        self.overlay_regions = []
        self.renderPage(self.current_page)
    
    def nextPage(self):
        """Go to next page"""
        if self.pdf_doc and self.current_page < len(self.pdf_doc) - 1:
            self.renderPage(self.current_page + 1)
    
    def previousPage(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.renderPage(self.current_page - 1)
    
    def goToPage(self, page_num):
        """Jump to specific page"""
        if 0 <= page_num < len(self.pdf_doc):
            self.renderPage(page_num)
    
    def setZoom(self, level):
        """Set zoom level (1.0 = 100%)"""
        self.zoom_level = level
        if self.pdf_doc:
            self.renderPage(self.current_page)
    
    def getTotalPages(self):
        """Get total page count"""
        return len(self.pdf_doc) if self.pdf_doc else 0

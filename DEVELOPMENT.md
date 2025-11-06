# AMB Print Application - Development Guide

## Project Structure

```
amb_print_app/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── config.py             # Configuration management
│   ├── pdf_parser.py         # PDF parsing and element extraction
│   ├── template_generator.py # ERPNext template generation
│   ├── ui/                   # UI components
│   │   ├── __init__.py
│   │   └── main_window.py    # Main application window
│   ├── exporters/            # Export modules
│   │   ├── __init__.py
│   │   └── erpnext_exporter.py
│   └── utils/                # Utility modules
│       ├── __init__.py
│       └── preview.py        # PDF preview rendering
├── tests/                    # Test files
│   ├── __init__.py
│   ├── test_pdf_parser.py
│   └── test_template_generator.py
├── data/                     # Data directory
├── logs/                     # Application logs
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── README.md                 # Project README
└── DEVELOPMENT.md            # This file
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- PyQt5 or PySide2
- wkhtmltopdf (for PDF preview)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/rogerboy38/amb_print_app.git
   cd amb_print_app
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your ERPNext settings
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

## Development Workflow

### Adding New Features

1. Create a new branch: `git checkout -b feature/your-feature`
2. Implement your feature
3. Write tests for new functionality
4. Run tests: `pytest`
5. Commit changes: `git commit -am "Add feature description"`
6. Push to branch: `git push origin feature/your-feature`
7. Create a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints for functions
- Add docstrings to classes and methods
- Format code with black: `black src/`
- Lint with flake8: `flake8 src/`

## Module Descriptions

### config.py
Manages all application settings including:
- Project paths
- Logging configuration
- PDF processing settings
- ERPNext API credentials
- UI settings
- Feature flags

### pdf_parser.py
Handles PDF parsing:
- Extracts text, images, and layout elements
- Maintains element metadata (fonts, sizes, positions)
- Supports context manager pattern
- Exports elements as dictionaries

### template_generator.py
Generates ERPNext templates:
- Creates HTML/Jinja2 templates
- Generates JSON format exports
- Renders templates with context data
- Exports directly to ERPNext format

### ui/main_window.py
Main application window:
- QtDesigner-based interface
- PDF upload and preview
- Element mapping interface
- Export functionality

## Testing

Run all tests:
```bash
pytest -v
```

Run with coverage:
```bash
pytest --cov=src tests/
```

## Building and Distribution

### Create executable (PyInstaller)
```bash
pyinstaller --onefile main.py
```

### Create package
```bash
python setup.py sdist bdist_wheel
```

## Troubleshooting

### PyMuPDF Installation Issues
If you encounter issues installing PyMuPDF, try:
```bash
pip install --pre PyMuPDF
```

### wkhtmltopdf Not Found
Install wkhtmltopdf:
- Ubuntu/Debian: `sudo apt-get install wkhtmltopdf`
- macOS: `brew install --cask wkhtmltopdf`
- Windows: Download from https://wkhtmltopdf.org/

## Contributing

Contributions are welcome! Please:
1. Follow the code style guidelines
2. Add tests for new features
3. Update documentation
4. Submit a pull request

## License

See LICENSE file for details.

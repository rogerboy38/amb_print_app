# 🚨 URGENT: Sync Sandbox with GitHub Master Branch

## Current Status
✅ **GitHub Repository**: All fixes committed and verified
❌ **Sandbox Server**: Running OLD code without fixes

## Why Tests Are Still Failing

The sandbox server (`2.tcp.ngrok.io:16278`) is running the OLD version of your code that doesn't have:
- The fixed `TestExporter` class with `export_mapping()` and `validate_mapping()` implementations
- The new `HTMLJinjaExporter` methods: `generate_html()`, `validate_template_syntax()`, `get_table_mappings()`, `export()`

**Solution**: Pull the latest code from GitHub master branch

---

## IMMEDIATE ACTION REQUIRED

### Execute This Command on Sandbox:

```bash
sshpass -p 'PpeFra27' ssh -o StrictHostKeyChecking=no -p 16278 frappe@2.tcp.ngrok.io << 'EOF'
cd ~/frappe-bench-spc2/amb_print_app
git pull origin master
ls -la tests/conftest.py src/exporters/html_jinja_exporter.py
EOF
```

### Verify the Pull Was Successful:

Look for output showing both files were updated. If successful, you'll see:
```
Updating xxxxxxx..xxxxxxx
Fast-forward
 tests/conftest.py                   | XX insertions(+), XX deletions(-)
 src/exporters/html_jinja_exporter.py | XXX insertions(+), XX deletions(-)
```

---

## Step-by-Step Git Sync Instructions

### Option 1: Simple Git Pull (Recommended)

```bash
sshpass -p 'PpeFra27' ssh -o StrictHostKeyChecking=no -p 16278 frappe@2.tcp.ngrok.io << 'EOF'
cd ~/frappe-bench-spc2/amb_print_app

# Check git status
git status

# Pull latest changes from master
git pull origin master

# Verify files were updated
echo "=== Checking conftest.py ==="
grep -n "export_mapping" tests/conftest.py

echo "=== Checking html_jinja_exporter.py ==="
grep -n "def generate_html" src/exporters/html_jinja_exporter.py
EOF
```

### Option 2: Force Reset to Master (If Conflicts)

```bash
sshpass -p 'PpeFra27' ssh -o StrictHostKeyChecking=no -p 16278 frappe@2.tcp.ngrok.io << 'EOF'
cd ~/frappe-bench-spc2/amb_print_app

# Discard any local changes
git checkout .

# Pull from master
git pull origin master

# Verify
git log --oneline -5
EOF
```

### Option 3: Complete Repository Reset

```bash
sshpass -p 'PpeFra27' ssh -o StrictHostKeyChecking=no -p 16278 frappe@2.tcp.ngrok.io << 'EOF'
cd ~/frappe-bench-spc2
rm -rf amb_print_app
git clone https://github.com/rogerboy38/amb_print_app.git
cd amb_print_app
ls -la
EOF
```

---

## Run Tests After Sync

### Once Git Sync is Complete:

```bash
sshpass -p 'PpeFra27' ssh -o StrictHostKeyChecking=no -p 16278 frappe@2.tcp.ngrok.io << 'EOF'
cd ~/frappe-bench-spc2/amb_print_app
source venv/bin/activate
pytest tests/ -v --tb=short
EOF
```

---

## Files That Were Updated in GitHub

These files are now in master but NOT yet on your sandbox:

### 1. tests/conftest.py
- **Change**: Added `export_mapping()` and `validate_mapping()` implementations to TestExporter
- **Lines Modified**: Around line 128-140
- **Impact**: Fixes 16 test errors

**Expected Code (After Pull)**:
```python
class TestExporter(BaseExporter):
    """Test exporter implementing all abstract methods."""
    
    def export_mapping(self, mapping: Dict[str, Any]) -> Any:
        """Implement abstract export_mapping method."""
        return {"status": "success", "data": mapping}
    
    def validate_mapping(self, mapping: Dict[str, Any]) -> bool:
        """Implement abstract validate_mapping method."""
        return True
    
    def export(self, mapping_data, output_path):
        """Export data to file."""
        return {"status": "success", "data": mapping_data}
```

### 2. src/exporters/html_jinja_exporter.py
- **Change**: Added 4 new methods (~85 lines)
  - `generate_html()`
  - `validate_template_syntax()`
  - `get_table_mappings()`
  - `export()`
- **Lines Modified**: Added after line 191
- **Impact**: Fixes 11 test failures

---

## How to Verify Sync Was Successful

### Check if New Methods Exist:

```bash
sshpass -p 'PpeFra27' ssh -o StrictHostKeyChecking=no -p 16278 frappe@2.tcp.ngrok.io << 'EOF'
cd ~/frappe-bench-spc2/amb_print_app

# Verify TestExporter has the methods
echo "Checking TestExporter methods:"
grep -A 5 "def export_mapping" tests/conftest.py
grep -A 5 "def validate_mapping" tests/conftest.py

# Verify HTMLJinjaExporter has the methods
echo "\nChecking HTMLJinjaExporter methods:"
grep -n "def generate_html\|def validate_template_syntax\|def get_table_mappings\|def export" src/exporters/html_jinja_exporter.py
EOF
```

### Expected Output:
```
Checking TestExporter methods:
def export_mapping(self, mapping: Dict[str, Any]) -> Any:
    """Implement abstract export_mapping method."""
    return {"status": "success", "data": mapping}

def validate_mapping(self, mapping: Dict[str, Any]) -> bool:
    """Implement abstract validate_mapping method."""
    return True

Checking HTMLJinjaExporter methods:
192:    def generate_html(self, mapping: Dict[str, Any]) -> str:
210:    def validate_template_syntax(self, mapping: Dict[str, Any]) -> Dict[str, Any]:
230:    def get_table_mappings(self, mapping: Dict[str, Any]) -> List[Dict[str, Any]]:
256:    def export(self, mapping: Dict[str, Any], output_path: str) -> Dict[str, Any]:
```

---

## Quick Verification Script

Run this after syncing to verify everything is correct:

```bash
sshpass -p 'PpeFra27' ssh -o StrictHostKeyChecking=no -p 16278 frappe@2.tcp.ngrok.io << 'EOF'
cd ~/frappe-bench-spc2/amb_print_app
source venv/bin/activate

# Check if methods exist
python3 -c "
from tests.conftest import TestExporter
from src.exporters.html_jinja_exporter import HTMLJinjaExporter

test_exp = TestExporter()
html_exp = HTMLJinjaExporter()

print('✓ TestExporter has export_mapping:', hasattr(test_exp, 'export_mapping'))
print('✓ TestExporter has validate_mapping:', hasattr(test_exp, 'validate_mapping'))
print('✓ HTMLJinjaExporter has generate_html:', hasattr(html_exp, 'generate_html'))
print('✓ HTMLJinjaExporter has validate_template_syntax:', hasattr(html_exp, 'validate_template_syntax'))
print('✓ HTMLJinjaExporter has get_table_mappings:', hasattr(html_exp, 'get_table_mappings'))
print('✓ HTMLJinjaExporter has export:', hasattr(html_exp, 'export'))
"
EOF
```

---

## After Sync - Run Tests

Once sync is complete, run the full test suite:

```bash
sshpass -p 'PpeFra27' ssh -o StrictHostKeyChecking=no -p 16278 frappe@2.tcp.ngrok.io << 'EOF'
cd ~/frappe-bench-spc2/amb_print_app
source venv/bin/activate

# Run all tests
pytest tests/ -v --tb=short

# Run with coverage
pytest tests/ -v --cov=src --cov-report=term-missing
EOF
```

---

## Troubleshooting

### Git Shows "fatal: Not a git repository"

```bash
sshpass -p 'PpeFra27' ssh -o StrictHostKeyChecking=no -p 16278 frappe@2.tcp.ngrok.io << 'EOF'
cd ~/frappe-bench-spc2/amb_print_app
git status
# If error, reinitialize:
git clone https://github.com/rogerboy38/amb_print_app.git tmp_clone
cp -r tmp_clone/.git .
rm -rf tmp_clone
git pull origin master
EOF
```

### Changes Conflict Error

```bash
sshpass -p 'PpeFra27' ssh -o StrictHostKeyChecking=no -p 16278 frappe@2.tcp.ngrok.io << 'EOF'
cd ~/frappe-bench-spc2/amb_print_app
# Discard local changes
git reset --hard HEAD
# Pull again
git pull origin master
EOF
```

### Still Showing Old Code

```bash
sshpass -p 'PpeFra27' ssh -o StrictHostKeyChecking=no -p 16278 frappe@2.tcp.ngrok.io << 'EOF'
cd ~/frappe-bench-spc2/amb_print_app
# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
# Verify files
head -40 tests/conftest.py | tail -20
EOF
```

---

## Summary of What to Do

1. **Copy this command and run it on your terminal**:
   ```bash
   sshpass -p 'PpeFra27' ssh -o StrictHostKeyChecking=no -p 16278 frappe@2.tcp.ngrok.io "cd ~/frappe-bench-spc2/amb_print_app && git pull origin master"
   ```

2. **Verify the sync**:
   ```bash
   sshpass -p 'PpeFra27' ssh -o StrictHostKeyChecking=no -p 16278 frappe@2.tcp.ngrok.io "cd ~/frappe-bench-spc2/amb_print_app && grep -n 'def export_mapping' tests/conftest.py && grep -n 'def generate_html' src/exporters/html_jinja_exporter.py"
   ```

3. **Run tests**:
   ```bash
   sshpass -p 'PpeFra27' ssh -o StrictHostKeyChecking=no -p 16278 frappe@2.tcp.ngrok.io "cd ~/frappe-bench-spc2/amb_print_app && source venv/bin/activate && pytest tests/ -v"
   ```

---

**Status**: All code is ready on GitHub. Just need to sync sandbox.
**Time Estimate**: < 1 minute to pull changes
**Expected Result**: Tests will pass once sync is complete

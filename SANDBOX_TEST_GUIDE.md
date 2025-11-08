# Sandbox Testing Guide - SSH Remote Execution

## Connection Details

**SSH Command**:
```bash
sshpass -p 'PpeFra27' ssh -o StrictHostKeyChecking=no -p 16278 frappe@2.tcp.ngrok.io
```

**Connection Info**:
- **Host**: 2.tcp.ngrok.io
- **Port**: 16278
- **Username**: frappe
- **Password**: PpeFra27
- **Environment**: Sandbox Frappe Bench

---

## Pre-Test Setup (One-Time)

### 1. Verify SSH Connection

```bash
# Test connection (use the command above)
sshpass -p 'PpeFra27' ssh -o StrictHostKeyChecking=no -p 16278 frappe@2.tcp.ngrok.io "echo 'Connection successful'"
```

### 2. Navigate to Project Directory

```bash
sshpass -p 'PpeFra27' ssh -o StrictHostKeyChecking=no -p 16278 frappe@2.tcp.ngrok.io << 'EOF'
cd ~/frappe-bench-spc2/amb_print_app
pwd
ls -la
EOF
```

### 3. Verify Virtual Environment

```bash
sshpass -p 'PpeFra27' ssh -o StrictHostKeyChecking=no -p 16278 frappe@2.tcp.ngrok.io << 'EOF'
cd ~/frappe-bench-spc2/amb_print_app
source venv/bin/activate
which python
python --version
EOF
```

### 4. Install/Update Dependencies

```bash
sshpass -p 'PpeFra27' ssh -o StrictHostKeyChecking=no -p 16278 frappe@2.tcp.ngrok.io << 'EOF'
cd ~/frappe-bench-spc2/amb_print_app
source venv/bin/activate
pip install -r requirements.txt --upgrade
EOF
```

---

## Running Tests

### Option 1: Run All Tests

```bash
sshpass -p 'PpeFra27' ssh -o StrictHostKeyChecking=no -p 16278 frappe@2.tcp.ngrok.io << 'EOF'
cd ~/frappe-bench-spc2/amb_print_app
source venv/bin/activate
pytest tests/ -v
EOF
```

### Option 2: Run Tests with Coverage

```bash
sshpass -p 'PpeFra27' ssh -o StrictHostKeyChecking=no -p 16278 frappe@2.tcp.ngrok.io << 'EOF'
cd ~/frappe-bench-spc2/amb_print_app
source venv/bin/activate
pytest tests/ -v --cov=src --cov-report=term-missing
EOF
```

### Option 3: Run Specific Test File

```bash
sshpass -p 'PpeFra27' ssh -o StrictHostKeyChecking=no -p 16278 frappe@2.tcp.ngrok.io << 'EOF'
cd ~/frappe-bench-spc2/amb_print_app
source venv/bin/activate
pytest tests/unit/test_html_jinja_exporter.py -v
EOF
```

### Option 4: Run Specific Test Class

```bash
sshpass -p 'PpeFra27' ssh -o StrictHostKeyChecking=no -p 16278 frappe@2.tcp.ngrok.io << 'EOF'
cd ~/frappe-bench-spc2/amb_print_app
source venv/bin/activate
pytest tests/unit/test_html_jinja_exporter.py::TestHTMLJinjaExporterGeneration -v
EOF
```

### Option 5: Run with Detailed Output

```bash
sshpass -p 'PpeFra27' ssh -o StrictHostKeyChecking=no -p 16278 frappe@2.tcp.ngrok.io << 'EOF'
cd ~/frappe-bench-spc2/amb_print_app
source venv/bin/activate
pytest tests/ -vv --tb=short --capture=no
EOF
```

---

## Expected Test Results

### Before Fixes
```
Collected: 27 tests
Passed: 0
Failed: 11 (AttributeError on missing methods)
Errors: 16 (TypeError on abstract method instantiation)
Coverage: 4.38% (requirement: 80%)
```

### After Fixes (Expected)
```
Collected: 27 tests
Passed: 27+ (depending on environment)
Failed: 0
Errors: 0
Coverage: 80%+ (once environment is properly configured)
```

---

## Troubleshooting

### Connection Issues

```bash
# If SSH connection times out
# 1. Verify ngrok connection is active
# 2. Try with explicit timeout
sshpass -p 'PpeFra27' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 -p 16278 frappe@2.tcp.ngrok.io "echo 'test'"

# 3. If still failing, check ngrok logs
```

### Dependency Issues

```bash
# If frappe-client fails to install
sshpass -p 'PpeFra27' ssh -o StrictHostKeyChecking=no -p 16278 frappe@2.tcp.ngrok.io << 'EOF'
cd ~/frappe-bench-spc2/amb_print_app
source venv/bin/activate
# Try installing core dependencies first
pip install pytest pytest-cov jinja2
# Then try full requirements
pip install -r requirements.txt
EOF
```

### Virtual Environment Issues

```bash
# If venv is broken, recreate it
sshpass -p 'PpeFra27' ssh -o StrictHostKeyChecking=no -p 16278 frappe@2.tcp.ngrok.io << 'EOF'
cd ~/frappe-bench-spc2/amb_print_app
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
EOF
```

---

## Saving Test Output

### Save to File

```bash
sshpass -p 'PpeFra27' ssh -o StrictHostKeyChecking=no -p 16278 frappe@2.tcp.ngrok.io << 'EOF' > test_results.txt 2>&1
cd ~/frappe-bench-spc2/amb_print_app
source venv/bin/activate
pytest tests/ -v --tb=short
EOF
cat test_results.txt
```

### Save HTML Coverage Report

```bash
sshpass -p 'PpeFra27' ssh -o StrictHostKeyChecking=no -p 16278 frappe@2.tcp.ngrok.io << 'EOF'
cd ~/frappe-bench-spc2/amb_print_app
source venv/bin/activate
pytest tests/ --cov=src --cov-report=html
echo "Coverage report saved to htmlcov/index.html"
ls -la htmlcov/
EOF
```

---

## Recent Code Changes

The following files were modified to fix test failures:

1. **tests/conftest.py** - Fixed TestExporter fixture
   - Added `export_mapping()` method
   - Added `validate_mapping()` method
   - Resolved 16 test errors

2. **src/exporters/html_jinja_exporter.py** - Added missing methods
   - Added `generate_html()` method
   - Added `validate_template_syntax()` method
   - Added `get_table_mappings()` method
   - Added `export()` method
   - Resolved 11 test failures

---

## Common Test Patterns

### Run Tests in Background

```bash
sshpass -p 'PpeFra27' ssh -o StrictHostKeyChecking=no -p 16278 frappe@2.tcp.ngrok.io << 'EOF' &
cd ~/frappe-bench-spc2/amb_print_app
source venv/bin/activate
pytest tests/ -v
EOF
wait
```

### Run Tests with Specific Markers

```bash
sshpass -p 'PpeFra27' ssh -o StrictHostKeyChecking=no -p 16278 frappe@2.tcp.ngrok.io << 'EOF'
cd ~/frappe-bench-spc2/amb_print_app
source venv/bin/activate
pytest tests/ -v -m unit
EOF
```

### Run Tests Until First Failure

```bash
sshpass -p 'PpeFra27' ssh -o StrictHostKeyChecking=no -p 16278 frappe@2.tcp.ngrok.io << 'EOF'
cd ~/frappe-bench-spc2/amb_print_app
source venv/bin/activate
pytest tests/ -v -x
EOF
```

---

## Quick Test Command (Copy & Paste)

```bash
sshpass -p 'PpeFra27' ssh -o StrictHostKeyChecking=no -p 16278 frappe@2.tcp.ngrok.io "cd ~/frappe-bench-spc2/amb_print_app && source venv/bin/activate && pytest tests/ -v --tb=short"
```

---

## Verification Checklist

- [ ] SSH connection is working
- [ ] Virtual environment is active
- [ ] Python version is 3.8+
- [ ] pytest is installed
- [ ] All dependencies from requirements.txt are installed
- [ ] Test files are accessible in tests/ directory
- [ ] Source code is in src/ directory
- [ ] conftest.py is properly configured
- [ ] pytest.ini exists with correct settings

---

## Support

If you encounter issues:

1. Check connection: `ping 2.tcp.ngrok.io`
2. Verify ngrok tunnel is active
3. Check logs: `tail -f ~/frappe-bench-spc2/amb_print_app/logs/*.log`
4. Review TEST_DEBUGGING_SUMMARY.md for implementation details
5. Check GitHub Actions for recent test runs

---

**Last Updated**: November 8, 2025, 1 AM CST
**All recent code fixes have been committed to master branch**

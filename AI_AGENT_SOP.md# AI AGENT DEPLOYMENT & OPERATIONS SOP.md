AI_AGENT_SOP.md# AI AGENT DEPLOYMENT & OPERATIONS SOP
## ERPNext Print Designer Migration Tool

**Version:** 1.0  
**Status:** FINAL  
**Created:** November 2025  
**Last Updated:** November 6, 2025

---

## EXECUTIVE SUMMARY

This SOP provides AI agents with complete instructions for deploying, configuring, and operating the ERPNext Print Designer Migration Tool. The system automates PDF-to-ERPNext template migration with comprehensive testing and CI/CD automation.

### Key Objectives:
- Automated PDF extraction and field mapping
- ERPNext API template upload
- 80%+ test coverage enforcement
- GitHub Actions CI/CD automation
- Robust error handling and validation

---

## PART 1: PREREQUISITES & ENVIRONMENT

### 1.1 System Requirements
- **Python:** 3.9, 3.10, or 3.11
- **Git:** Latest version
- **OS:** Linux/macOS/Windows (WSL2 recommended)
- **Storage:** 2GB minimum
- **Network:** Access to GitHub & ERPNext instances

### 1.2 Required Credentials
- GitHub account (rogerboy38/amb_print_app access)
- ERPNext API Key & Secret (TestProd)
- ERPNext API Key & Secret (Production, if applicable)

### 1.3 Dependencies
```bash
pip install -r requirements.txt
```

**Core Libraries:**
- pdfplumber (PDF parsing)
- jinja2 (Template generation)
- requests (HTTP calls)
- pytest (Testing)
- pytest-cov (Coverage)

---

## PART 2: DEPLOYMENT

### 2.1 Initial Setup

```bash
# 1. Clone Repository
git clone git@github.com:rogerboy38/amb_print_app.git
cd amb_print_app

# 2. Create Virtual Environment
python3 -m venv venv
source venv/bin/activate

# 3. Install Dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install pytest pytest-cov pytest-html

# 4. Configure Environment
cp .env.example .env
# Edit .env file with credentials

# 5. Verify Installation
python main.py --version
pytest --version
```

### 2.2 Update Existing Installation

```bash
cd amb_print_app
git pull origin master
source venv/bin/activate
pip install --upgrade -r requirements.txt
pytest tests/ -v --cov=src
```

---

## PART 3: OPERATIONS

### 3.1 Run Complete Pipeline

```bash
python main.py --mode complete
```

Executes in sequence:
1. Extract PDFs from ERPNext
2. Parse document structures
3. Generate field mappings
4. Upload to ERPNext

### 3.2 Run Individual Phases

```bash
# Extract PDFs
python main.py --mode extract --output ./data/extracted_pdfs/

# Parse Structures
python main.py --mode parse --input ./data/extracted_pdfs/

# Generate Mappings
python main.py --mode map --input ./data/pdf_structures/

# Upload to ERPNext
python main.py --mode upload --input ./data/field_mappings/
```

### 3.3 Running Tests

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

### 3.4 Monitoring & Logging

```bash
# View live logs
tail -f logs/amb_print_app.log

# Filter errors
grep ERROR logs/amb_print_app.log

# Export logs
tar -czf logs_$(date +%Y%m%d).tar.gz logs/
```

---

## PART 4: QUALITY ASSURANCE

### 4.1 Pre-Deployment Checklist

- [ ] All unit tests passing (80%+ coverage)
- [ ] All integration tests passing
- [ ] No linting errors: `flake8 src tests`
- [ ] Coverage report reviewed
- [ ] Documentation updated
- [ ] Changelog entries added
- [ ] Git commits descriptive

### 4.2 CI/CD Validation

GitHub Actions runs automatically on:
- Push to master/develop
- Pull requests against master/develop

**Automated Checks:**
- Python 3.9, 3.10, 3.11 compatibility
- Unit test execution
- Integration test execution
- Coverage enforcement (80%+ minimum)
- Code quality (flake8/pylint)
- Codecov integration

### 4.3 Test Coverage Requirements

| Component | Minimum | Target |
|-----------|---------|--------|
| Overall | 80% | 85%+ |
| Exporters | 90% | 95%+ |
| UI | 75% | 85%+ |
| Integration | 85% | 90%+ |

---

## PART 5: TROUBLESHOOTING

### 5.1 Common Issues

**Issue:** ModuleNotFoundError: pdfplumber  
**Fix:** `pip install pdfplumber`

**Issue:** ValidationError: Product Item mandatory  
**Fix:** Ensure Product Item field populated

**Issue:** ChildTableError: Minimum 1 row required  
**Fix:** Add at least 1 row to child table

**Issue:** APIError: Unauthorized  
**Fix:** Verify API credentials

**Issue:** Coverage < 80%  
**Fix:** Add test cases

### 5.2 Error Handling

```bash
# If test fails
pytest tests/unit/ -vv -s

# If export fails
python main.py --mode export --retry 3

# If API fails
python main.py --verify-credentials
```

### 5.3 Backup & Recovery

```bash
# Backup
tar -czf backup_$(date +%Y%m%d).tar.gz tests/ logs/ config/

# Restore
tar -xzf backup_20251106.tar.gz
git pull origin master
pytest tests/ -v
```

---

## PART 6: SECURITY

### 6.1 Credential Management
- Never commit .env to repository
- Use environment variables
- Rotate API keys quarterly
- Separate dev/test/prod credentials
- Audit API logs regularly

### 6.2 Data Protection
- Encrypt sensitive data at rest
- Use HTTPS for API calls
- Validate all inputs
- Sanitize logs
- Restrict file permissions (chmod 600)

### 6.3 Code Security
- Run `pip audit` regularly
- Keep dependencies updated
- Use dependency scanning
- Follow OWASP guidelines
- Review pull requests

---

## PART 7: ADVANCED CONFIG

### 7.1 Environment Variables

**Required:**
- ERPNEXT_URL
- ERPNEXT_API_KEY
- ERPNEXT_API_SECRET

**Optional:**
- DEBUG_MODE (default: false)
- LOG_LEVEL (default: INFO)
- PDF_TIMEOUT (default: 30s)
- BATCH_SIZE (default: 100)
- RETRY_COUNT (default: 3)
- RETRY_DELAY (default: 5s)

### 7.2 Pytest Configuration

```bash
# Run with markers
pytest -m unit -v
pytest -m integration -v

# Parallel execution (4x faster)
pytest -n auto tests/

# With timeout (5s max)
pytest --timeout=5 tests/
```

---

## PART 8: PERFORMANCE

### 8.1 Optimization

- **Batch Processing:** Set BATCH_SIZE 100-500
- **Parallel Tests:** `pytest -n auto`
- **Caching:** CACHE_PDFS=true
- **Profiling:** `python -m cProfile main.py`

### 8.2 Monitoring

```bash
# CPU & Memory
watch -n 1 'ps aux | grep main.py'

# Network
iftop

# Disk
df -h
du -sh .
```

---

## PART 9: MAINTENANCE

### 9.1 Regular Tasks

**Weekly:**
- Review logs
- Run full test suite
- Verify API connectivity

**Monthly:**
- Update dependencies
- Rotate credentials
- Archive logs
- Backup data

**Quarterly:**
- Update documentation
- Audit field mappings
- Performance testing
- Security audit

### 9.2 Documentation

- README.md - Overview
- tests/README.md - Testing
- DEVELOPMENT.md - Dev guide
- PHASE3_TEST_STRATEGY.md - Strategy

---

## PART 10: MANDATORY FIELD VALIDATION

### CRITICAL CONSTRAINTS

**✓ Product Item Field:** MANDATORY - Must be populated  
**✓ Child Table:** MINIMUM 1 ROW - Cannot be empty  
**✓ Field Validation:** Enforced before export  
**✓ Error Messages:** Clear and actionable

All tests validate these constraints exhaustively.

---

## REPOSITORY REFERENCE

**GitHub:** https://github.com/rogerboy38/amb_print_app  
**Branch:** master  
**Status:** Production Ready  
**Test Coverage:** 80%+ enforced

---

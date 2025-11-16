# Phase 4: API Automation & Testing - Execution Guide

## Overview

This guide provides step-by-step instructions for executing Phase 4 of the amb_print_app project, which automates batch migration, validation, and API uploads of print formats from sandbox to production ERPNext environments.

**Phase 4 Workflow:**
- Setup Verification → Batch Migration → Output Validation → API Upload → Sandbox Testing → Production Sync

## Prerequisites

✅ **Completed before starting Phase 4:**
- Phase 1: PDF extraction and field mapping (scripts 01-03)
- Phase 2: Template refinement in ERPNext UI
- Phase 3: Quotation variant mapping
- All Python dependencies installed (`pip install -r requirements.txt`)
- Git repository cloned and working directory ready

## Setup Instructions

### 1. Configure API Credentials

**Step 1.1: Create credentials file**
```bash
cp config/credentials.json.template config/credentials.json
```

**Step 1.2: Edit credentials file**
```bash
vim config/credentials.json  # or your preferred editor
```

**Step 1.3: Add your ERPNext API credentials**

For **Sandbox Environment** (sysmayal.frappe.cloud):
- Log into ERPNext sandbox
- Navigate to: Setup → Users and Permissions → Users → [Your User]
- Scroll to "API User" section
- Generate API key and secret
- Copy values to `config/credentials.json` under `sandbox` section

For **Production Environment** (sysmayal.v.frappe.cloud):
- Repeat same process on production instance
- Add values under `production` section

**Example:**
```json
{
  "sandbox": {
    "base_url": "https://sysmayal.frappe.cloud",
    "api_key": "your_actual_sandbox_api_key_here",
    "api_secret": "your_actual_sandbox_api_secret_here"
  },
  "production": {
    "base_url": "https://sysmayal.v.frappe.cloud",
    "api_key": "your_actual_production_api_key_here",
    "api_secret": "your_actual_production_api_secret_here"
  }
}
```

⚠️ **SECURITY NOTE:** Never commit `config/credentials.json` to version control. It's in `.gitignore`.

## Execution Steps

### 2. Run Phase 4 Orchestrator (Automated Workflow)

The orchestrator script automates all Phase 4 steps with comprehensive logging.

**Option A: Sandbox Testing (Recommended First)**
```bash
python scripts/08_phase4_orchestrator.py \
  --env sandbox \
  --formats-file data/field_mappings/migrated_formats.json \
  --config config/credentials.json
```

**Option B: Production Deployment (After Sandbox Validation)**
```bash
python scripts/08_phase4_orchestrator.py \
  --env production \
  --formats-file data/field_mappings/migrated_formats.json \
  --config config/credentials.json
```

**Command-line Options:**
- `--env`: Target environment (`sandbox` or `production`, default: `sandbox`)
- `--formats-file`: Path to migrated formats JSON file
- `--config`: Path to credentials config file (default: `config/credentials.json`)

### 3. Monitor Execution

The orchestrator generates detailed logs:

**Log Files Created:**
```
phase4_orchestration_YYYYMMDD_HHMMSS.log   # Main orchestration log
migration_debug_logs/
  ├── migration_debug_YYYYMMDD_HHMMSS.log      # Batch migration details
  ├── migration_errors_YYYYMMDD_HHMMSS.log     # Errors only
  └── migration_report_YYYYMMDD_HHMMSS.json    # Statistics & edge cases
api_upload_YYYYMMDD_HHMMSS.log           # API upload details
```

**Monitor in Real-Time:**
```bash
tail -f phase4_orchestration_*.log
```

## Manual Step-by-Step Execution

If you prefer to run each step manually:

### Step A: Verify Setup
```bash
python -c "
from pathlib import Path
from scripts.phase4_orchestrator import Phase4Orchestrator
orchestrator = Phase4Orchestrator()
orchestrator.verify_setup()
"
```

### Step B: Run Batch Migration with Debug Logging
```bash
python scripts/07_batch_migration_debug.py \
  --mode debug \
  --output-dir migration_debug_logs
```

**Expected Output:**
- PDF structures extracted to `data/pdf_structures/`
- Field mappings created in `data/field_mappings/`
- Debug logs in `migration_debug_logs/`
- Report with statistics and edge cases

### Step C: Validate JSON Outputs
```bash
python scripts/07_batch_migration_debug.py \
  --mode validate \
  --input-file data/field_mappings/migrated_formats.json
```

**Validation Checks:**
- ✓ Required fields present (doc_type, name, html)
- ✓ JSON syntax valid
- ✓ HTML content not empty
- ✓ No corrupted or malformed data

### Step D: Upload to Sandbox
```bash
python scripts/06_api_upload.py \
  --env sandbox \
  --formats-file data/field_mappings/migrated_formats.json \
  --credentials-file config/credentials.json
```

**Expected Output:**
```
✓ Successfully uploaded: COA_Template
✓ Successfully uploaded: Quotation_Normal
✓ Successfully uploaded: Quotation_Escalated
Success: 3/3
```

### Step E: Verify in ERPNext Sandbox

1. Log into sandbox: https://sysmayal.frappe.cloud
2. Navigate to: **Setup → Customize Form → Print Format**
3. Search for uploaded templates:
   - `COA_Template`
   - `Quotation_Normal`
   - `Quotation_Escalated`
4. Open each and verify:
   - ✓ HTML renders without errors
   - ✓ Field mappings are correct
   - ✓ Layout and styling is preserved
   - ✓ No broken image links or missing data

### Step F: Test Print Preview

1. Go to a test document (e.g., Quotation)
2. Click **Menu → Print**
3. Select uploaded format from dropdown
4. Click **Print** to generate PDF
5. Verify output:
   - ✓ All fields populated
   - ✓ Tables rendered correctly
   - ✓ Images display properly
   - ✓ Page breaks are correct

## Troubleshooting

### Common Issues & Solutions

**Issue: "Credentials file not found"**
```
Solution:
1. Verify file exists: ls -la config/credentials.json
2. If missing, create it: cp config/credentials.json.template config/credentials.json
3. Ensure credentials are filled in (not placeholder values)
```

**Issue: "Authentication failed: 401"**
```
Solution:
1. Verify API key and secret are correct
2. Check API key hasn't expired
3. Confirm user account is active in ERPNext
4. Test API manually: curl -H "Authorization: token KEY:SECRET" https://sysmayal.frappe.cloud/api/resource/Print%20Format
```

**Issue: "Timeout uploading to API"**
```
Solution:
1. Check network connectivity
2. Verify ERPNext instance is online
3. Increase timeout: Edit scripts/06_api_upload.py, change timeout=30 to timeout=60
4. Retry with smaller batch size
```

**Issue: "JSON validation failed"**
```
Solution:
1. Check migration_errors log for details
2. Verify PDF extraction completed successfully
3. Manually inspect data/field_mappings/*.json for structure
4. Re-run migration if PDFs were incomplete
```

**Issue: "Template rendered blank in ERPNext"**
```
Solution:
1. Check HTML content is present: cat data/field_mappings/template.json | grep html
2. Verify Jinja variables are correct (should be {{doc.field_name}})
3. Test template in ERPNext Print Designer
4. Check for JavaScript errors in browser console
```

## Production Deployment

After successful sandbox validation:

### Pre-Production Checklist
- [ ] All 3 print formats tested in sandbox
- [ ] Edge cases documented and handled
- [ ] Team reviewed and approved templates
- [ ] Backup of current production print formats taken
- [ ] Rollback plan documented

### Production Deployment
```bash
# 1. Create production backup
python -c "
import requests
from pathlib import Path
import json

# Backup existing formats
backup_dir = Path('backups/production_backup_' + datetime.now().isoformat())
backup_dir.mkdir(parents=True, exist_ok=True)

# Download and save existing formats
# ... (implement backup logic)
"

# 2. Deploy to production
python scripts/08_phase4_orchestrator.py \
  --env production \
  --formats-file data/field_mappings/migrated_formats.json \
  --config config/credentials.json

# 3. Verify production
# Log into production instance and test print preview
```

## Output Artifacts

### Generated Logs & Reports

```
phase4_orchestration_20251116_080000.log
│
├─ Setup Verification Log
│  ├─ ✓ config_file: True
│  ├─ ✓ scripts_exist: (True, True, True)
│  └─ ✓ data_dir: True
│
├─ Batch Migration Log
│  ├─ Total files: 45
│  ├─ Successfully processed: 43
│  ├─ Failed: 2
│  └─ Edge cases found: 5 (missing fields, format anomalies)
│
├─ Validation Report
│  ├─ Total: 3
│  ├─ Valid: 3
│  ├─ Invalid: 0
│  └─ Missing fields: none
│
└─ API Upload Result
   ├─ Sandbox Success: 3/3
   └─ Errors: none
```

## Best Practices

1. **Always test in sandbox first** - Never deploy directly to production
2. **Keep credentials secure** - Never share or commit credentials file
3. **Monitor logs carefully** - Edge cases and warnings indicate potential issues
4. **Document changes** - Track which formats were migrated and when
5. **Maintain backups** - Always backup production before deployment
6. **Test thoroughly** - Verify all print formats work correctly
7. **Version control** - Commit successful migrations to Git

## Getting Help

If issues persist:

1. Check debug logs: `cat migration_debug_logs/migration_debug_*.log`
2. Review error logs: `cat migration_debug_logs/migration_errors_*.log`
3. Check API logs: `tail -f api_upload_*.log`
4. Reference ERPNext docs: https://docs.erpnext.com/docs/user/manual/en/customize-form
5. Contact support with log files and error details

---

**Last Updated:** November 2025
**Phase 4 Status:** ✅ Production Ready

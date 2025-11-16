#!/usr/bin/env python
"""
Phase 4: API Automation & Testing Orchestrator
Coordinates batch migration, validation, and API uploads for print formats.
"""

import subprocess, sys, json, logging
from pathlib import Path
from datetime import datetime

class Phase4Orchestrator:
    def __init__(self, config='config/credentials.json'):
        self.config = config
        self.root = Path(__file__).parent.parent
        self.ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.setup_logging()
    
    def setup_logging(self):
        log_f = f"phase4_orchestration_{self.ts}.log"
        logging.basicConfig(level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.FileHandler(log_f), logging.StreamHandler(sys.stdout)])
        self.logger = logging.getLogger('Phase4')
        self.logger.info("\n" + "="*70)
        self.logger.info("PHASE 4: API AUTOMATION & TESTING")
        self.logger.info("="*70 + "\n")
    
    def verify_setup(self):
        self.logger.info("[1] Verifying setup...")
        checks = {
            'config': Path(self.config).exists(),
            'scripts': all([(self.root/f'scripts/{s}').exists() for s in ['05_batch_migration.py', '06_api_upload.py', '07_batch_migration_debug.py']])
        }
        for k,v in checks.items():
            self.logger.info(f"  {'✓' if v else '✗'} {k}: {v}")
        return all(checks.values())
    
    def run_batch_migration(self):
        self.logger.info("\n[2] Running batch migration...")
        try:
            result = subprocess.run([sys.executable, str(self.root/'scripts/07_batch_migration_debug.py'),
                '--mode', 'debug', '--output-dir', 'migration_debug_logs'],
                capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                self.logger.info("✓ Migration completed")
                return True
            else:
                self.logger.error(f"✗ Migration failed: {result.stderr[:200]}")
                return False
        except Exception as e:
            self.logger.error(f"✗ Error: {str(e)}")
            return False
    
    def validate_outputs(self):
        self.logger.info("\n[3] Validating outputs...")
        output_dir = self.root / 'data/field_mappings'
        if not output_dir.exists():
            self.logger.warning(f"⚠ Output dir not found: {output_dir}")
            return False
        json_files = list(output_dir.glob('*.json'))
        valid = 0
        for jf in json_files:
            try:
                with open(jf) as f:
                    data = json.load(f)
                if all(k in data for k in ['doc_type', 'name', 'html']):
                    valid += 1
                    self.logger.info(f"  ✓ {jf.name}")
                else:
                    self.logger.warning(f"  ✗ {jf.name} - missing fields")
            except Exception as e:
                self.logger.error(f"  ✗ {jf.name}: {str(e)[:100]}")
        self.logger.info(f"Validation: {valid}/{len(json_files)} valid")
        return valid == len(json_files) if json_files else False
    
    def upload_to_sandbox(self, fmt_file, env='sandbox'):
        self.logger.info(f"\n[4] Uploading to {env}...")
        try:
            result = subprocess.run([sys.executable, str(self.root/'scripts/06_api_upload.py'),
                '--env', env, '--formats-file', fmt_file, '--credentials-file', self.config],
                capture_output=True, text=True, timeout=600)
            if result.returncode == 0:
                self.logger.info(f"✓ Upload successful")
                return True
            else:
                self.logger.error(f"✗ Upload failed: {result.stderr[:200]}")
                return False
        except Exception as e:
            self.logger.error(f"✗ Error: {str(e)}")
            return False
    
    def execute(self, env='sandbox', fmt_file=None):
        results = {}
        if not self.verify_setup():
            return False
        results['migration'] = self.run_batch_migration()
        results['validation'] = self.validate_outputs()
        if fmt_file and results['migration'] and results['validation']:
            results['upload'] = self.upload_to_sandbox(fmt_file, env)
        self.logger.info("\n" + "="*70)
        self.logger.info(f"Results: {results}")
        self.logger.info("="*70 + "\n")
        return all(results.values())

def main():
    import argparse
    p = argparse.ArgumentParser(description="Phase 4 Orchestrator")
    p.add_argument('--env', choices=['sandbox','production'], default='sandbox')
    p.add_argument('--formats-file')
    p.add_argument('--config', default='config/credentials.json')
    args = p.parse_args()
    orch = Phase4Orchestrator(args.config)
    sys.exit(0 if orch.execute(args.env, args.formats_file) else 1)

if __name__ == "__main__":
    main()

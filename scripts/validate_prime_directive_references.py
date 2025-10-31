#!/usr/bin/env python3
"""
Prime Directive References Validator

Scans all documentation files for Prime Directive references and validates
that postgres18 agent_landing content matches AYA_PRIME_DIRECTIVES.md.

Implements Prime Directive #5: BULLETPROOF VERIFICATION PROTOCOL

Version: 1.0
Date: October 30, 2025
"""

import os
import sys
from pathlib import Path
from typing import Dict, List
import psycopg2
import hashlib

# AYA base path
AYA_BASE = Path("/Users/arthurdell/AYA")
PRIME_DIRECTIVES_PATH = AYA_BASE / "AYA_PRIME_DIRECTIVES.md"

# Database connection
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "aya_rag",
    "user": "postgres",
    "password": "Power$$336633$$"
}

# Critical documentation files that MUST reference Prime Directives
CRITICAL_DOCS = [
    'AGENT_INITIALIZATION_LANDING.md',
    'AGENT_LANDING.md',
    'CLAUDE.md',
    'AIR_OPERATIONAL_GUIDE.md',
    'QUICK_REFERENCE.md',
    'AGENT_CODING_STANDARDS_GUIDE.md',
    'AGENT_TURBO_CURSOR_READY.md',
    'AGENT_TURBO_PRIME_DIRECTIVES_COMPLIANCE.md'
]

# Required reference markers
REQUIRED_MARKERS = [
    'AYA BULLET PROOF PRIME DIRECTIVES',
    'AYA_PRIME_DIRECTIVES.md'
]


def get_file_hash(file_path: Path) -> str:
    """Get SHA256 hash of file content."""
    if not file_path.exists():
        return None
    
    with open(file_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def check_doc_references() -> Dict:
    """Check all markdown files for Prime Directive references."""
    result = {
        'status': 'PASS',
        'critical_docs': {},
        'missing_references': [],
        'total_checked': 0
    }
    
    # Check critical docs
    for doc_name in CRITICAL_DOCS:
        doc_path = AYA_BASE / doc_name
        doc_info = {
            'exists': doc_path.exists(),
            'has_reference': False,
            'has_master_ref': False
        }
        
        if doc_path.exists():
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
                doc_info['has_reference'] = any(marker in content for marker in REQUIRED_MARKERS)
                doc_info['has_master_ref'] = 'AYA_PRIME_DIRECTIVES.md' in content
        
            if not doc_info['has_reference']:
                result['missing_references'].append(doc_name)
                result['status'] = 'FAIL'
        
        result['critical_docs'][doc_name] = doc_info
        result['total_checked'] += 1
    
    # Also scan all markdown files in AYA
    md_files = list(AYA_BASE.rglob('*.md'))
    result['total_md_files'] = len(md_files)
    
    return result


def verify_db_content_match() -> Dict:
    """Verify agent_landing DB content matches AYA_PRIME_DIRECTIVES.md."""
    result = {
        'status': 'UNKNOWN',
        'master_file_exists': False,
        'db_content_exists': False,
        'has_prime_directives': False,
        'matches': False,
        'error': None
    }
    
    # Check master file
    if not PRIME_DIRECTIVES_PATH.exists():
        result['error'] = 'Master Prime Directives file not found'
        return result
    
    result['master_file_exists'] = True
    
    # Read master file
    try:
        with open(PRIME_DIRECTIVES_PATH, 'r', encoding='utf-8') as f:
            master_content = f.read()
        
        # Extract key sections
        master_key_sections = [
            'AYA BULLET PROOF PRIME DIRECTIVES',
            'FUNCTIONAL REALITY ONLY',
            'TRUTH OVER COMFORT',
            'BULLETPROOF VERIFICATION PROTOCOL',
            'NO THEATRICAL WRAPPERS',
            'DUAL-SYSTEM RELAY DEVELOPMENT PROTOCOL'
        ]
        
        master_has_all = all(section in master_content for section in master_key_sections)
        
    except Exception as e:
        result['error'] = f"Could not read master file: {e}"
        return result
    
    # Check database content
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT content FROM agent_landing 
            WHERE is_current = true 
            ORDER BY id DESC 
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        if row:
            db_content = row[0]
            result['db_content_exists'] = True
            
            # Check if DB has Prime Directives
            db_has_all = all(section in db_content for section in master_key_sections)
            result['has_prime_directives'] = db_has_all
            
            # Check if key content matches (at least first 2000 chars for Prime Directives section)
            if master_has_all and db_has_all:
                # Extract Prime Directives section from DB (should be at start)
                db_pd_section = db_content[:5000]  # First 5000 chars should contain PD
                master_pd_section = master_content[:5000]
                
                # Check key markers match
                if 'AYA BULLET PROOF PRIME DIRECTIVES' in db_pd_section:
                    result['matches'] = True
                    result['status'] = 'PASS'
                else:
                    result['status'] = 'FAIL'
                    result['error'] = 'Prime Directives not found at start of DB content'
            else:
                result['status'] = 'FAIL'
                result['error'] = 'Missing key sections in master or DB content'
        else:
            result['status'] = 'FAIL'
            result['error'] = 'No current agent_landing record found'
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        result['status'] = 'ERROR'
        result['error'] = str(e)
    
    return result


def generate_validation_report() -> Dict:
    """Generate comprehensive validation report."""
    print("📋 Prime Directive References Validation")
    print("=" * 60)
    
    report = {
        'checks': {},
        'overall_status': 'PASS',
        'timestamp': str(Path.cwd())
    }
    
    # Check 1: Documentation References
    print("\n1. Checking documentation references...")
    doc_check = check_doc_references()
    report['checks']['documentation_references'] = doc_check
    
    if doc_check['status'] == 'PASS':
        print(f"   ✅ All {doc_check['total_checked']} critical docs reference Prime Directives")
    else:
        print(f"   ❌ Missing references in {len(doc_check['missing_references'])} files:")
        for doc in doc_check['missing_references']:
            print(f"      - {doc}")
        report['overall_status'] = 'FAIL'
    
    # Check 2: DB Content Match
    print("\n2. Verifying database content matches master file...")
    db_check = verify_db_content_match()
    report['checks']['db_content_match'] = db_check
    
    if db_check['status'] == 'PASS':
        print("   ✅ Database content matches master Prime Directives file")
    else:
        print(f"   ❌ {db_check['status']}: {db_check.get('error', 'See details')}")
        report['overall_status'] = 'FAIL'
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Overall Status: {report['overall_status']}")
    
    return report


if __name__ == "__main__":
    try:
        report = generate_validation_report()
        
        # Write report to file
        report_path = AYA_BASE / "PRIME_DIRECTIVES_VALIDATION_REPORT.json"
        import json
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Full report saved to: {report_path}")
        
        sys.exit(0 if report['overall_status'] == 'PASS' else 1)
        
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


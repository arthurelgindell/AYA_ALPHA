#!/usr/bin/env python3
"""
Gladiator Attack Pattern Importer
Imports all Gladiator attack patterns from JSON files into PostgreSQL 18

Created: October 29, 2025
"""

import json
import psycopg2
from pathlib import Path
from datetime import datetime
import sys

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'aya_rag',
    'user': 'postgres',
    'password': 'Power$$336633$$'
}

# Data source paths
GLADIATOR_BASE = Path("/Users/arthurdell/AYA/projects/GLADIATOR/datasets")
ARMED_EXPLOITS = GLADIATOR_BASE / "armed_exploits"
COMBAT_TRAINING = GLADIATOR_BASE / "combat_training"
EXPLOIT_DATABASE = GLADIATOR_BASE / "exploit_database"
SYNTHETIC_BASE = GLADIATOR_BASE / "synthetic_base"

def connect_db():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print(f"✅ Connected to PostgreSQL: {DB_CONFIG['database']}")
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)

def import_armed_exploits(conn):
    """Import CVE attack patterns from armed_exploits/"""
    print("\n📦 Importing Armed Exploits (CVEs)...")
    
    if not ARMED_EXPLOITS.exists():
        print(f"⚠️  Directory not found: {ARMED_EXPLOITS}")
        return 0
    
    cursor = conn.cursor()
    imported = 0
    skipped = 0
    errors = 0
    
    json_files = list(ARMED_EXPLOITS.glob("*.json"))
    total = len(json_files)
    print(f"Found {total} CVE JSON files")
    
    for idx, json_file in enumerate(json_files, 1):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Generate unique pattern_id from CVE
            cve_id = data.get('cve', json_file.stem)
            pattern_id = f"CVE-{cve_id.replace('CVE-', '')}-{int(datetime.now().timestamp())}"
            
            # Extract fields
            attack_type = 'cve_exploit'
            attack_category = 'vulnerability_exploitation'
            payload = data.get('exploit', '')[:10000]  # Limit payload size
            description = data.get('description', '')[:1000]
            vulnerability_name = data.get('vulnerability', '')
            
            # Build metadata
            metadata = {
                'cve_id': cve_id,
                'vulnerability': vulnerability_name,
                'actively_exploited': data.get('actively_exploited', False),
                'october_2025': data.get('october_2025', False),
                'generated': data.get('generated', ''),
                'source_file': str(json_file)
            }
            
            # Determine complexity based on payload length and exploitation status
            complexity_level = 5
            if data.get('actively_exploited'):
                complexity_level = 8
            if len(payload) > 5000:
                complexity_level = 9
            
            # Insert into database
            cursor.execute("""
                INSERT INTO gladiator_attack_patterns 
                (pattern_id, attack_type, attack_category, complexity_level,
                 payload, description, metadata_json, storage_path, 
                 generated_at, validated, used_in_training)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (pattern_id) DO NOTHING
            """, (
                pattern_id,
                attack_type,
                attack_category,
                complexity_level,
                payload,
                f"{vulnerability_name}: {description}",
                json.dumps(metadata),
                str(json_file),
                datetime.now(),
                True,  # CVEs are validated
                False
            ))
            
            if cursor.rowcount > 0:
                imported += 1
            else:
                skipped += 1
            
            # Commit in batches
            if imported % 100 == 0:
                conn.commit()
                print(f"  Progress: {imported}/{total} imported, {skipped} skipped")
                
        except json.JSONDecodeError as e:
            errors += 1
            print(f"  ⚠️  JSON error in {json_file.name}: {e}")
        except Exception as e:
            errors += 1
            print(f"  ⚠️  Error importing {json_file.name}: {e}")
    
    conn.commit()
    cursor.close()
    
    print(f"✅ Armed Exploits: {imported} imported, {skipped} skipped, {errors} errors")
    return imported

def import_combat_training(conn):
    """Import combat training sessions"""
    print("\n📦 Importing Combat Training Data...")
    
    if not COMBAT_TRAINING.exists():
        print(f"⚠️  Directory not found: {COMBAT_TRAINING}")
        return 0
    
    cursor = conn.cursor()
    imported = 0
    
    json_files = list(COMBAT_TRAINING.glob("*.json"))
    total = len(json_files)
    print(f"Found {total} combat training files")
    
    for idx, json_file in enumerate(json_files, 1):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Generate pattern_id
            pattern_id = f"COMBAT-{json_file.stem}-{int(datetime.now().timestamp())}"
            
            # Extract fields
            attack_type = data.get('attack_type', 'combat_training')
            attack_category = data.get('category', 'training')
            payload = json.dumps(data.get('payload', data), ensure_ascii=False)[:10000]
            description = data.get('description', f"Combat training session from {json_file.name}")[:1000]
            
            complexity_level = data.get('complexity', 5)
            
            # Insert
            cursor.execute("""
                INSERT INTO gladiator_attack_patterns 
                (pattern_id, attack_type, attack_category, complexity_level,
                 payload, description, metadata_json, storage_path, 
                 generated_at, validated, used_in_training)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (pattern_id) DO NOTHING
            """, (
                pattern_id,
                attack_type,
                attack_category,
                complexity_level,
                payload,
                description,
                json.dumps(data),
                str(json_file),
                datetime.now(),
                False,
                True  # Combat training data is for training
            ))
            
            if cursor.rowcount > 0:
                imported += 1
            
            if imported % 500 == 0:
                conn.commit()
                print(f"  Progress: {imported}/{total} imported")
                
        except Exception as e:
            continue
    
    conn.commit()
    cursor.close()
    
    print(f"✅ Combat Training: {imported} imported")
    return imported

def import_exploit_database(conn):
    """Import exploit database patterns"""
    print("\n📦 Importing Exploit Database...")
    
    if not EXPLOIT_DATABASE.exists():
        print(f"⚠️  Directory not found: {EXPLOIT_DATABASE}")
        return 0
    
    cursor = conn.cursor()
    imported = 0
    
    json_files = list(EXPLOIT_DATABASE.glob("*.json"))
    total = len(json_files)
    print(f"Found {total} exploit files")
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            pattern_id = f"EXPLOIT-{json_file.stem}-{int(datetime.now().timestamp())}"
            
            cursor.execute("""
                INSERT INTO gladiator_attack_patterns 
                (pattern_id, attack_type, attack_category, complexity_level,
                 payload, description, metadata_json, storage_path, 
                 generated_at, validated, used_in_training)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (pattern_id) DO NOTHING
            """, (
                pattern_id,
                data.get('attack_type', 'exploit'),
                data.get('category', 'exploitation'),
                data.get('complexity', 6),
                json.dumps(data.get('payload', data), ensure_ascii=False)[:10000],
                data.get('description', f"Exploit from {json_file.name}")[:1000],
                json.dumps(data),
                str(json_file),
                datetime.now(),
                False,
                False
            ))
            
            if cursor.rowcount > 0:
                imported += 1
            
            if imported % 500 == 0:
                conn.commit()
                print(f"  Progress: {imported}/{total} imported")
                
        except Exception as e:
            continue
    
    conn.commit()
    cursor.close()
    
    print(f"✅ Exploit Database: {imported} imported")
    return imported

def main():
    """Main import orchestration"""
    print("╔═══════════════════════════════════════════════════════╗")
    print("║  GLADIATOR ATTACK PATTERN IMPORTER                    ║")
    print("║  PostgreSQL 18 Database Reconstruction                ║")
    print("╚═══════════════════════════════════════════════════════╝")
    print(f"\nTarget Database: {DB_CONFIG['database']}")
    print(f"Source: {GLADIATOR_BASE}")
    print("\n" + "="*60)
    
    # Connect to database
    conn = connect_db()
    
    # Import datasets
    total_imported = 0
    
    try:
        total_imported += import_armed_exploits(conn)
        total_imported += import_combat_training(conn)
        total_imported += import_exploit_database(conn)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Import interrupted by user")
        conn.rollback()
    except Exception as e:
        print(f"\n\n❌ Import failed: {e}")
        conn.rollback()
    finally:
        conn.close()
    
    print("\n" + "="*60)
    print(f"\n✅ IMPORT COMPLETE: {total_imported} total patterns imported")
    print("\nDatabase: aya_rag")
    print("Table: gladiator_attack_patterns")
    print("\n" + "="*60)

if __name__ == "__main__":
    main()


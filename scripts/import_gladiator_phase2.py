#!/usr/bin/env python3
"""
Gladiator Attack Pattern Importer - Phase 2
Imports additional datasets: synthetic_base, training_10m, adversarial, blue_team

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
SYNTHETIC_BASE = GLADIATOR_BASE / "synthetic_base"
TRAINING_10M = GLADIATOR_BASE / "training_10m"
ADVERSARIAL = GLADIATOR_BASE / "adversarial"
BLUE_TEAM = GLADIATOR_BASE / "blue_team_training"
EXPANSION = GLADIATOR_BASE / "expansion"

def connect_db():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print(f"✅ Connected to PostgreSQL: {DB_CONFIG['database']}")
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)

def import_synthetic_base(conn):
    """Import synthetic attack patterns"""
    print("\n📦 Importing Synthetic Base...")
    
    if not SYNTHETIC_BASE.exists():
        print(f"⚠️  Directory not found: {SYNTHETIC_BASE}")
        return 0
    
    cursor = conn.cursor()
    imported = 0
    
    json_files = list(SYNTHETIC_BASE.glob("*.json"))
    total = len(json_files)
    print(f"Found {total} synthetic pattern files")
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            pattern_id = f"SYNTH-{json_file.stem}-{int(datetime.now().timestamp())}"
            
            cursor.execute("""
                INSERT INTO gladiator_attack_patterns 
                (pattern_id, attack_type, attack_category, complexity_level,
                 payload, description, metadata_json, storage_path, 
                 generated_at, validated, used_in_training)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (pattern_id) DO NOTHING
            """, (
                pattern_id,
                data.get('attack_type', 'synthetic'),
                data.get('category', 'synthetic_attack'),
                data.get('complexity', 5),
                json.dumps(data.get('payload', data), ensure_ascii=False)[:10000],
                data.get('description', f"Synthetic pattern from {json_file.name}")[:1000],
                json.dumps(data),
                str(json_file),
                datetime.now(),
                False,
                True  # Synthetic data for training
            ))
            
            if cursor.rowcount > 0:
                imported += 1
            
            if imported % 200 == 0:
                conn.commit()
                print(f"  Progress: {imported}/{total} imported")
                
        except Exception as e:
            continue
    
    conn.commit()
    cursor.close()
    
    print(f"✅ Synthetic Base: {imported} imported")
    return imported

def import_training_10m(conn):
    """Import training dataset patterns"""
    print("\n📦 Importing Training 10M...")
    
    if not TRAINING_10M.exists():
        print(f"⚠️  Directory not found: {TRAINING_10M}")
        return 0
    
    cursor = conn.cursor()
    imported = 0
    
    json_files = list(TRAINING_10M.glob("*.json"))
    total = len(json_files)
    print(f"Found {total} training files")
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            pattern_id = f"TRAIN-{json_file.stem}-{int(datetime.now().timestamp())}"
            
            cursor.execute("""
                INSERT INTO gladiator_attack_patterns 
                (pattern_id, attack_type, attack_category, complexity_level,
                 payload, description, metadata_json, storage_path, 
                 generated_at, validated, used_in_training)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (pattern_id) DO NOTHING
            """, (
                pattern_id,
                data.get('attack_type', 'training'),
                data.get('category', 'training_data'),
                data.get('complexity', 5),
                json.dumps(data.get('payload', data), ensure_ascii=False)[:10000],
                data.get('description', f"Training data from {json_file.name}")[:1000],
                json.dumps(data),
                str(json_file),
                datetime.now(),
                False,
                True
            ))
            
            if cursor.rowcount > 0:
                imported += 1
            
            if imported % 200 == 0:
                conn.commit()
                print(f"  Progress: {imported}/{total} imported")
                
        except Exception as e:
            continue
    
    conn.commit()
    cursor.close()
    
    print(f"✅ Training 10M: {imported} imported")
    return imported

def import_adversarial(conn):
    """Import adversarial samples"""
    print("\n📦 Importing Adversarial Samples...")
    
    if not ADVERSARIAL.exists():
        print(f"⚠️  Directory not found: {ADVERSARIAL}")
        return 0
    
    cursor = conn.cursor()
    imported = 0
    
    # Import JSONL files
    jsonl_files = list(ADVERSARIAL.glob("*.jsonl"))
    for jsonl_file in jsonl_files:
        try:
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        data = json.loads(line.strip())
                        
                        pattern_id = f"ADV-{jsonl_file.stem}-{line_num}-{int(datetime.now().timestamp())}"
                        
                        cursor.execute("""
                            INSERT INTO gladiator_attack_patterns 
                            (pattern_id, attack_type, attack_category, complexity_level,
                             payload, description, metadata_json, storage_path, 
                             generated_at, validated, used_in_training)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (pattern_id) DO NOTHING
                        """, (
                            pattern_id,
                            data.get('attack_type', 'adversarial'),
                            data.get('category', 'adversarial_attack'),
                            data.get('complexity', 7),
                            json.dumps(data.get('payload', data), ensure_ascii=False)[:10000],
                            data.get('description', f"Adversarial sample from {jsonl_file.name}")[:1000],
                            json.dumps(data),
                            f"{jsonl_file}:line{line_num}",
                            datetime.now(),
                            False,
                            True
                        ))
                        
                        if cursor.rowcount > 0:
                            imported += 1
                        
                        if imported % 200 == 0:
                            conn.commit()
                            print(f"  Progress: {imported} imported from {jsonl_file.name}")
                            
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            print(f"  ⚠️  Error reading {jsonl_file.name}: {e}")
            continue
    
    # Import JSON files in adversarial directory
    json_files = list(ADVERSARIAL.glob("*.json"))
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            pattern_id = f"ADV-{json_file.stem}-{int(datetime.now().timestamp())}"
            
            cursor.execute("""
                INSERT INTO gladiator_attack_patterns 
                (pattern_id, attack_type, attack_category, complexity_level,
                 payload, description, metadata_json, storage_path, 
                 generated_at, validated, used_in_training)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (pattern_id) DO NOTHING
            """, (
                pattern_id,
                data.get('attack_type', 'adversarial'),
                data.get('category', 'adversarial_attack'),
                data.get('complexity', 7),
                json.dumps(data.get('payload', data), ensure_ascii=False)[:10000],
                data.get('description', f"Adversarial from {json_file.name}")[:1000],
                json.dumps(data),
                str(json_file),
                datetime.now(),
                False,
                True
            ))
            
            if cursor.rowcount > 0:
                imported += 1
                
        except Exception as e:
            continue
    
    conn.commit()
    cursor.close()
    
    print(f"✅ Adversarial: {imported} imported")
    return imported

def import_blue_team(conn):
    """Import blue team defensive patterns"""
    print("\n📦 Importing Blue Team Training...")
    
    if not BLUE_TEAM.exists():
        print(f"⚠️  Directory not found: {BLUE_TEAM}")
        return 0
    
    cursor = conn.cursor()
    imported = 0
    
    # Recursively find all JSON files
    json_files = list(BLUE_TEAM.rglob("*.json"))
    jsonl_files = list(BLUE_TEAM.rglob("*.jsonl"))
    
    total = len(json_files) + len(jsonl_files)
    print(f"Found {total} blue team files")
    
    # Import JSON files
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            pattern_id = f"BLUE-{json_file.stem}-{int(datetime.now().timestamp())}"
            
            cursor.execute("""
                INSERT INTO gladiator_attack_patterns 
                (pattern_id, attack_type, attack_category, complexity_level,
                 payload, description, metadata_json, storage_path, 
                 generated_at, validated, used_in_training)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (pattern_id) DO NOTHING
            """, (
                pattern_id,
                data.get('attack_type', 'defensive'),
                data.get('category', 'blue_team_defense'),
                data.get('complexity', 5),
                json.dumps(data.get('payload', data), ensure_ascii=False)[:10000],
                data.get('description', f"Blue team pattern from {json_file.name}")[:1000],
                json.dumps(data),
                str(json_file),
                datetime.now(),
                True,  # Blue team patterns are validated
                True
            ))
            
            if cursor.rowcount > 0:
                imported += 1
            
            if imported % 200 == 0:
                conn.commit()
                print(f"  Progress: {imported}/{total} imported")
                
        except Exception as e:
            continue
    
    # Import JSONL files
    for jsonl_file in jsonl_files:
        try:
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        data = json.loads(line.strip())
                        
                        pattern_id = f"BLUE-{jsonl_file.stem}-{line_num}-{int(datetime.now().timestamp())}"
                        
                        cursor.execute("""
                            INSERT INTO gladiator_attack_patterns 
                            (pattern_id, attack_type, attack_category, complexity_level,
                             payload, description, metadata_json, storage_path, 
                             generated_at, validated, used_in_training)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (pattern_id) DO NOTHING
                        """, (
                            pattern_id,
                            data.get('attack_type', 'defensive'),
                            data.get('category', 'blue_team_defense'),
                            data.get('complexity', 5),
                            json.dumps(data.get('payload', data), ensure_ascii=False)[:10000],
                            data.get('description', f"Blue team from {jsonl_file.name}")[:1000],
                            json.dumps(data),
                            f"{jsonl_file}:line{line_num}",
                            datetime.now(),
                            True,
                            True
                        ))
                        
                        if cursor.rowcount > 0:
                            imported += 1
                        
                        if imported % 200 == 0:
                            conn.commit()
                            
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            continue
    
    conn.commit()
    cursor.close()
    
    print(f"✅ Blue Team: {imported} imported")
    return imported

def main():
    """Main import orchestration for Phase 2"""
    print("╔═══════════════════════════════════════════════════════╗")
    print("║  GLADIATOR PHASE 2 IMPORTER                           ║")
    print("║  Additional Datasets: Synthetic, Training, Defense    ║")
    print("╚═══════════════════════════════════════════════════════╝")
    print(f"\nTarget Database: {DB_CONFIG['database']}")
    print(f"Source: {GLADIATOR_BASE}")
    print("\n" + "="*60)
    
    # Connect to database
    conn = connect_db()
    
    # Import datasets
    total_imported = 0
    
    try:
        total_imported += import_synthetic_base(conn)
        total_imported += import_training_10m(conn)
        total_imported += import_adversarial(conn)
        total_imported += import_blue_team(conn)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Import interrupted by user")
        conn.rollback()
    except Exception as e:
        print(f"\n\n❌ Import failed: {e}")
        conn.rollback()
    finally:
        conn.close()
    
    print("\n" + "="*60)
    print(f"\n✅ PHASE 2 COMPLETE: {total_imported} additional patterns imported")
    print("\nDatabase: aya_rag")
    print("Table: gladiator_attack_patterns")
    
    # Get final statistics
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM gladiator_attack_patterns")
    total_patterns = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    
    print(f"\n📊 TOTAL PATTERNS IN DATABASE: {total_patterns}")
    print("\n" + "="*60)

if __name__ == "__main__":
    main()


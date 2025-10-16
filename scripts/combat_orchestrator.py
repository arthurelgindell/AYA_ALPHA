#!/usr/bin/env python3 -u
"""
GLADIATOR Combat Orchestrator
Manages Red Team vs Blue Team adversarial combat sessions
Extracts high-value training data from attack/defense cycles
"""

import sys
import json
import time
import requests
from datetime import datetime
from pathlib import Path

# Force unbuffered output for background execution
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# Configuration (SSH Tunnel Mode - Fixed)
LM_STUDIO_ALPHA = "http://localhost:1234"              # Blue Team (ALPHA direct)
LM_STUDIO_BETA = "http://localhost:1235"               # Red Team (BETA via tunnel)
BLUE_MODEL = "foundation-sec-8b-instruct-int8"
RED_MODEL = "llama-3.3-70b-instruct"

# Data paths (for ALPHA execution)
ARMED_EXPLOITS = Path("/Users/arthurdell/GLADIATOR/datasets/armed_exploits")
TRAINING_OUTPUT = Path("/Users/arthurdell/GLADIATOR/datasets/combat_training")
TRAINING_OUTPUT.mkdir(exist_ok=True)


class CombatSession:
    """Single combat session: Red attacks, Blue defends"""
    
    def __init__(self, session_id):
        self.session_id = session_id
        self.timestamp = datetime.now().isoformat()
        self.attacks = []
        self.defenses = []
        self.outcomes = []
    
    def red_team_attack(self, exploit_data):
        """Generate attack using Red Team with current threat intel"""
        prompt = f"""You are GLADIATOR Red Team - offensive AI with current threat intelligence.

ARMED EXPLOIT DATA (October 2025):
CVE: {exploit_data.get('cve', 'N/A')}
Vulnerability: {exploit_data.get('vulnerability_name', 'N/A')}
Persona: {exploit_data.get('persona', 'APT Group')}
Threat Level: {exploit_data.get('threat_level', 'HIGH')}

EXPLOIT CODE:
{exploit_data.get('exploit_code', '')[:500]}

MISSION: Generate a sophisticated attack variant that:
1. Uses this exploit with evasion techniques
2. Targets realistic systems (web servers, databases, APIs)
3. Includes obfuscation to bypass detection
4. Provides specific payload and execution steps

Generate WORKING attack code (not theoretical):"""

        try:
            response = requests.post(
                f"{LM_STUDIO_BETA}/v1/chat/completions",
                json={
                    "model": RED_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.9,
                    "max_tokens": 800
                },
                timeout=180  # Increased from 60s to 180s for 70B model
            )
            attack = response.json()['choices'][0]['message']['content']
            self.attacks.append({
                'timestamp': datetime.now().isoformat(),
                'exploit_base': exploit_data.get('cve', 'unknown'),
                'persona': exploit_data.get('persona', 'unknown'),
                'attack_code': attack
            })
            return attack
        except Exception as e:
            print(f"❌ Red Team attack failed: {e}", flush=True)
            return None
    
    def blue_team_defend(self, attack_code):
        """Generate defense using Blue Team"""
        prompt = f"""You are GLADIATOR Blue Team - defensive AI with behavioral detection.

INCOMING ATTACK DETECTED:
{attack_code[:800]}

MISSION: Analyze this attack and generate defense strategy:
1. Identify attack vectors and techniques (MITRE ATT&CK)
2. Detect evasion attempts and obfuscation
3. Provide specific detection rules (YARA, Sigma, Snort)
4. Recommend mitigation steps
5. Identify indicators of compromise (IOCs)

Generate ACTIONABLE defense response:"""

        try:
            response = requests.post(
                f"{LM_STUDIO_ALPHA}/v1/chat/completions",
                json={
                    "model": BLUE_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 800
                },
                timeout=60
            )
            response_data = response.json()
            print(f"🔵 Blue Team API response keys: {list(response_data.keys())}", flush=True)
            if 'choices' in response_data and len(response_data['choices']) > 0:
                defense = response_data['choices'][0]['message']['content']
            else:
                print(f"❌ Blue Team API response: {response_data}", flush=True)
                return None
            self.defenses.append({
                'timestamp': datetime.now().isoformat(),
                'defense_strategy': defense
            })
            return defense
        except Exception as e:
            print(f"❌ Blue Team defense failed: {e}", flush=True)
            return None
    
    def evaluate_outcome(self, attack, defense):
        """Evaluate combat outcome (simple heuristic for now)"""
        # Check if Blue Team identified key attack components
        defense_lower = defense.lower() if defense else ""
        detected_vectors = sum([
            'injection' in defense_lower,
            'exploit' in defense_lower,
            'payload' in defense_lower,
            'evasion' in defense_lower,
            'mitre' in defense_lower,
            'ioc' in defense_lower
        ])
        
        outcome = {
            'timestamp': datetime.now().isoformat(),
            'detection_score': detected_vectors,
            'blue_detected': detected_vectors >= 3,
            'training_value': 'high' if detected_vectors >= 3 else 'medium'
        }
        self.outcomes.append(outcome)
        return outcome
    
    def save_training_data(self):
        """Save session as training data"""
        training_file = TRAINING_OUTPUT / f"combat_session_{self.session_id}_{int(time.time())}.json"
        
        data = {
            'session_id': self.session_id,
            'timestamp': self.timestamp,
            'attacks': self.attacks,
            'defenses': self.defenses,
            'outcomes': self.outcomes,
            'training_pairs': []
        }
        
        # Create training pairs (attack-defense)
        for i, (attack, defense, outcome) in enumerate(zip(self.attacks, self.defenses, self.outcomes)):
            data['training_pairs'].append({
                'pair_id': f"{self.session_id}_{i}",
                'attack': attack['attack_code'],
                'defense': defense['defense_strategy'],
                'outcome': outcome,
                'labels': {
                    'attack_type': attack.get('persona', 'unknown'),
                    'blue_success': outcome['blue_detected'],
                    'training_value': outcome['training_value']
                }
            })
        
        with open(training_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"✅ Training data saved: {training_file}", flush=True)
        return training_file


def load_random_exploits(count=10):
    """Load random armed exploits for combat"""
    exploit_files = list(ARMED_EXPLOITS.glob("*.json"))
    if not exploit_files:
        print(f"❌ No armed exploits found in {ARMED_EXPLOITS}", flush=True)
        return []
    
    import random
    selected = random.sample(exploit_files, min(count, len(exploit_files)))
    
    exploits = []
    for f in selected:
        try:
            with open(f) as fp:
                exploits.append(json.load(fp))
        except Exception as e:
            print(f"⚠️  Failed to load {f}: {e}")
    
    return exploits


def run_combat_session(session_id, rounds=10):
    """Run a complete combat session"""
    print(f"\n{'='*80}", flush=True)
    print(f"🥊 GLADIATOR COMBAT SESSION {session_id}", flush=True)
    print(f"{'='*80}", flush=True)
    print(f"Red Team: {RED_MODEL} (BETA)", flush=True)
    print(f"Blue Team: {BLUE_MODEL} (ALPHA)", flush=True)
    print(f"Rounds: {rounds}", flush=True)
    print(f"{'='*80}\n", flush=True)
    
    session = CombatSession(session_id)
    exploits = load_random_exploits(rounds)
    
    if not exploits:
        print("❌ No exploits available for combat", flush=True)
        return None

    for i, exploit in enumerate(exploits, 1):
        print(f"\n--- Round {i}/{rounds} ---", flush=True)
        print(f"Exploit: {exploit.get('cve', 'N/A')} | Persona: {exploit.get('persona', 'N/A')}", flush=True)

        # Red Team attacks
        print("🔴 Red Team generating attack...", flush=True)
        attack = session.red_team_attack(exploit)
        if not attack:
            print("⚠️  Skipping round (Red Team failed)", flush=True)
            continue
        print(f"✅ Attack generated ({len(attack)} chars)", flush=True)

        # Blue Team defends
        print("🔵 Blue Team analyzing attack...", flush=True)
        defense = session.blue_team_defend(attack)
        if not defense:
            print("⚠️  Skipping round (Blue Team failed)", flush=True)
            continue
        print(f"✅ Defense generated ({len(defense)} chars)", flush=True)

        # Evaluate outcome
        outcome = session.evaluate_outcome(attack, defense)
        status = "🎯 DETECTED" if outcome['blue_detected'] else "⚠️  MISSED"
        print(f"{status} | Detection Score: {outcome['detection_score']}/6", flush=True)
        
        # Rate limiting
        time.sleep(2)
    
    # Save training data
    print(f"\n{'='*80}", flush=True)
    training_file = session.save_training_data()
    print(f"📊 Combat session complete!", flush=True)
    print(f"   Attacks: {len(session.attacks)}", flush=True)
    print(f"   Defenses: {len(session.defenses)}", flush=True)
    print(f"   Training pairs: {len(session.attacks)}", flush=True)
    print(f"   Data file: {training_file.name}", flush=True)
    print(f"{'='*80}\n", flush=True)
    
    return session


def main():
    """Main combat orchestration"""
    import sys
    
    sessions = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    rounds_per_session = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║                   GLADIATOR COMBAT SYSTEM                        ║
║                      Combat Orchestrator                         ║
╚══════════════════════════════════════════════════════════════════╝

Configuration:
  Sessions: {sessions}
  Rounds per session: {rounds_per_session}
  Red Team Model: {RED_MODEL}
  Blue Team Model: {BLUE_MODEL}
  Armed Exploits: {len(list(ARMED_EXPLOITS.glob("*.json")))}

Starting combat...
""")
    
    results = []
    for i in range(1, sessions + 1):
        session = run_combat_session(f"session_{i:03d}", rounds_per_session)
        if session:
            results.append(session)
        
        # Pause between sessions
        if i < sessions:
            print(f"\n⏸️  Pausing 5 seconds before next session...\n")
            time.sleep(5)
    
    # Final summary
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║                      COMBAT COMPLETE                             ║
╚══════════════════════════════════════════════════════════════════╝

Total Sessions: {len(results)}
Total Attacks: {sum(len(s.attacks) for s in results)}
Total Defenses: {sum(len(s.defenses) for s in results)}
Training Files: {len(list(TRAINING_OUTPUT.glob("*.json")))}

Training data location: {TRAINING_OUTPUT}
""")


if __name__ == "__main__":
    main()


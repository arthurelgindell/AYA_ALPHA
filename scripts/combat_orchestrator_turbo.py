#!/usr/bin/env python3 -u
"""
GLADIATOR Combat Orchestrator TURBO
Maximum throughput version - NO SLEEPS, maximum parallelization
"""

import sys
import json
import requests
from datetime import datetime
from pathlib import Path

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# Configuration
LM_STUDIO_ALPHA = "http://localhost:1234"  # Blue Team (ALPHA)
LM_STUDIO_BETA = "http://localhost:1235"   # Red Team (BETA via tunnel)
BLUE_MODEL = "foundation-sec-8b-instruct-int8"
RED_MODEL = "qwen3-14b-mlx"

# Data paths
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
        """Generate attack using Red Team"""
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
                    "max_tokens": 200
                },
                timeout=180
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
                    "max_tokens": 200
                },
                timeout=60
            )
            defense = response.json()['choices'][0]['message']['content']
            self.defenses.append({
                'timestamp': datetime.now().isoformat(),
                'defense_strategy': defense
            })
            return defense
        except Exception as e:
            print(f"❌ Blue Team defense failed: {e}", flush=True)
            return None

    def evaluate_outcome(self, attack, defense):
        """Evaluate combat outcome"""
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
        import time
        training_file = TRAINING_OUTPUT / f"combat_session_{self.session_id}_{int(time.time())}.json"

        data = {
            'session_id': self.session_id,
            'timestamp': self.timestamp,
            'attacks': self.attacks,
            'defenses': self.defenses,
            'outcomes': self.outcomes,
            'training_pairs': []
        }

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

        print(f"✅ Saved: {training_file.name} ({len(data['training_pairs'])} pairs)", flush=True)
        return training_file


def load_random_exploits(count=10):
    """Load random armed exploits"""
    exploit_files = list(ARMED_EXPLOITS.glob("*.json"))
    if not exploit_files:
        return []

    import random
    selected = random.sample(exploit_files, min(count, len(exploit_files)))

    exploits = []
    for f in selected:
        try:
            with open(f) as fp:
                exploits.append(json.load(fp))
        except:
            pass

    return exploits


def run_combat_session(session_id, rounds=10):
    """Run combat session - NO SLEEPS"""
    print(f"🥊 SESSION {session_id} | {rounds} rounds", flush=True)

    session = CombatSession(session_id)
    exploits = load_random_exploits(rounds)

    if not exploits:
        return None

    for i, exploit in enumerate(exploits, 1):
        print(f"⚔️  R{i}/{rounds} {exploit.get('cve', 'N/A')}", flush=True, end=" ")

        # Red Team attacks
        attack = session.red_team_attack(exploit)
        if not attack:
            print("❌", flush=True)
            continue

        # Blue Team defends
        defense = session.blue_team_defend(attack)
        if not defense:
            print("❌", flush=True)
            continue

        # Evaluate
        outcome = session.evaluate_outcome(attack, defense)
        status = "🎯" if outcome['blue_detected'] else "⚠️"
        print(f"{status} {outcome['detection_score']}/6", flush=True)

        # NO SLEEP - maximum throughput

    session.save_training_data()
    print(f"✅ SESSION {session_id} COMPLETE: {len(session.attacks)} pairs\n", flush=True)
    return session


def main():
    """TURBO combat orchestration"""
    import sys

    sessions = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    rounds_per_session = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    print(f"🚀 GLADIATOR TURBO | {sessions} sessions × {rounds_per_session} rounds = {sessions * rounds_per_session} pairs", flush=True)
    print(f"🔥 NO SLEEPS - MAXIMUM THROUGHPUT MODE\n", flush=True)

    results = []
    for i in range(1, sessions + 1):
        session = run_combat_session(f"turbo_{i:03d}", rounds_per_session)
        if session:
            results.append(session)
        # NO SLEEP between sessions

    total_pairs = sum(len(s.attacks) for s in results)
    print(f"\n🏁 TURBO COMPLETE: {total_pairs} pairs generated", flush=True)


if __name__ == "__main__":
    main()

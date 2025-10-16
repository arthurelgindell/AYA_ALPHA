#!/usr/bin/env python3
"""
GLADIATOR Persona-Based Combat Orchestrator
Generates attacks using different adversarial personas for varied sophistication levels
"""

import json
import time
import requests
from datetime import datetime
from pathlib import Path
import random

# Configuration (Direct Access Mode)
LM_STUDIO_ALPHA = "http://localhost:1234"              # Blue Team (ALPHA direct)
LM_STUDIO_BETA = "http://beta.local:1234"              # Red Team (BETA direct)
BLUE_MODEL = "foundation-sec-8b-instruct-int8"
RED_MODEL = "llama-3.3-70b-instruct"

# Data paths
ARMED_EXPLOITS = Path("/Users/arthurdell/GLADIATOR/datasets/armed_exploits")
TRAINING_OUTPUT = Path("/Users/arthurdell/GLADIATOR/datasets/persona_combat_training")
TRAINING_OUTPUT.mkdir(exist_ok=True)

# Persona Framework
PERSONAS = {
    "script_kiddie": {
        "name": "Script Kiddie",
        "sophistication": "low",
        "tools": ["Metasploit", "Nmap", "basic scripts"],
        "evasion": "minimal",
        "targeting": "opportunistic",
        "description": "Uses pre-built tools and scripts with minimal customization"
    },
    "ransomware_operator": {
        "name": "Ransomware Operator", 
        "sophistication": "medium",
        "tools": ["custom ransomware", "C2 infrastructure", "lateral movement"],
        "evasion": "moderate",
        "targeting": "high-value targets",
        "description": "Focuses on financial gain through encryption and extortion"
    },
    "apt_group": {
        "name": "APT Group",
        "sophistication": "high", 
        "tools": ["custom malware", "zero-days", "living-off-the-land"],
        "evasion": "advanced",
        "targeting": "strategic intelligence",
        "description": "Nation-state or corporate espionage with advanced techniques"
    },
    "nation_state": {
        "name": "Nation State Actor",
        "sophistication": "elite",
        "tools": ["zero-days", "supply chain", "infrastructure attacks"],
        "evasion": "maximum",
        "targeting": "critical infrastructure",
        "description": "Highest level of sophistication with unlimited resources"
    }
}


class PersonaCombatSession:
    """Combat session with persona-based attack generation"""
    
    def __init__(self, session_id):
        self.session_id = session_id
        self.timestamp = datetime.now().isoformat()
        self.attacks = []
        self.defenses = []
        self.outcomes = []
    
    def red_team_attack_with_persona(self, exploit_data, persona_key):
        """Generate attack using specific persona"""
        persona = PERSONAS[persona_key]
        
        prompt = f"""You are GLADIATOR Red Team - {persona['name']} persona.

PERSONA PROFILE:
- Sophistication: {persona['sophistication']}
- Tools: {', '.join(persona['tools'])}
- Evasion Level: {persona['evasion']}
- Targeting: {persona['targeting']}
- Description: {persona['description']}

ARMED EXPLOIT DATA (October 2025):
CVE: {exploit_data.get('cve', 'N/A')}
Vulnerability: {exploit_data.get('vulnerability_name', 'N/A')}
Threat Level: {exploit_data.get('threat_level', 'HIGH')}

EXPLOIT CODE:
{exploit_data.get('exploit_code', '')[:500]}

MISSION: Generate an attack that matches your persona's sophistication level:

{self._get_persona_instructions(persona_key)}

Generate WORKING attack code that reflects your persona's capabilities:"""

        try:
            response = requests.post(
                f"{LM_STUDIO_BETA}/v1/chat/completions",
                json={
                    "model": RED_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.9,
                    "max_tokens": 1000
                },
                timeout=180  # Increased from 90s to 180s for 70B model
            )
            attack = response.json()['choices'][0]['message']['content']
            self.attacks.append({
                'timestamp': datetime.now().isoformat(),
                'exploit_base': exploit_data.get('cve', 'unknown'),
                'persona': persona_key,
                'persona_name': persona['name'],
                'sophistication': persona['sophistication'],
                'attack_code': attack
            })
            return attack
        except Exception as e:
            print(f"❌ Red Team attack failed: {e}")
            return None
    
    def _get_persona_instructions(self, persona_key):
        """Get persona-specific attack instructions"""
        instructions = {
            "script_kiddie": """
1. Use basic, well-known attack vectors
2. Minimal obfuscation or evasion
3. Focus on common vulnerabilities
4. Use standard tools and scripts
5. Simple, direct approach""",
            
            "ransomware_operator": """
1. Focus on lateral movement and persistence
2. Include encryption and ransom demands
3. Use moderate evasion techniques
4. Target high-value systems
5. Include C2 communication patterns""",
            
            "apt_group": """
1. Use advanced evasion and anti-analysis
2. Include living-off-the-land techniques
3. Focus on stealth and persistence
4. Use custom tools and techniques
5. Include intelligence gathering methods""",
            
            "nation_state": """
1. Use zero-day or near-zero-day techniques
2. Maximum sophistication and stealth
3. Include supply chain or infrastructure attacks
4. Advanced anti-forensics
5. Long-term persistence and intelligence gathering"""
        }
        return instructions.get(persona_key, "")
    
    def blue_team_defend(self, attack_code, persona_info):
        """Generate defense with persona context"""
        prompt = f"""You are GLADIATOR Blue Team - defensive AI with behavioral detection.

ATTACKER PERSONA: {persona_info['persona_name']} ({persona_info['sophistication']} sophistication)
SOPHISTICATION LEVEL: {persona_info['sophistication']}
EVASION CAPABILITIES: {persona_info['evasion']}

INCOMING ATTACK DETECTED:
{attack_code[:1000]}

MISSION: Analyze this attack considering the attacker's sophistication level and generate appropriate defense:

1. Identify attack vectors and techniques (MITRE ATT&CK)
2. Assess sophistication level and expected evasion
3. Provide detection rules appropriate for this threat level
4. Recommend mitigation steps
5. Identify indicators of compromise (IOCs)
6. Suggest behavioral detection patterns

Generate ACTIONABLE defense response tailored to this threat level:"""

        try:
            response = requests.post(
                f"{LM_STUDIO_ALPHA}/v1/chat/completions",
                json={
                    "model": BLUE_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=90
            )
            response_data = response.json()
            if 'choices' in response_data and len(response_data['choices']) > 0:
                defense = response_data['choices'][0]['message']['content']
                self.defenses.append({
                    'timestamp': datetime.now().isoformat(),
                    'defense_strategy': defense,
                    'threat_level': persona_info['sophistication']
                })
                return defense
            else:
                print(f"❌ Blue Team API response: {response_data}")
                return None
        except Exception as e:
            print(f"❌ Blue Team defense failed: {e}")
            return None
    
    def evaluate_outcome(self, attack, defense, persona_info):
        """Evaluate combat outcome with persona context"""
        defense_lower = defense.lower() if defense else ""
        
        # Persona-specific detection criteria
        detection_criteria = {
            "script_kiddie": ["injection", "exploit", "payload", "basic", "common"],
            "ransomware_operator": ["ransomware", "encryption", "lateral", "persistence", "c2"],
            "apt_group": ["advanced", "stealth", "custom", "evasion", "persistence", "living"],
            "nation_state": ["zero-day", "supply", "infrastructure", "advanced", "sophisticated"]
        }
        
        criteria = detection_criteria.get(persona_info['persona'], detection_criteria["script_kiddie"])
        detected_vectors = sum(1 for criterion in criteria if criterion in defense_lower)
        
        # Adjust scoring based on sophistication
        sophistication_multiplier = {
            "low": 1.0,
            "medium": 1.2, 
            "high": 1.5,
            "elite": 2.0
        }
        
        base_score = detected_vectors
        adjusted_score = base_score * sophistication_multiplier.get(persona_info['sophistication'], 1.0)
        
        outcome = {
            'timestamp': datetime.now().isoformat(),
            'detection_score': min(adjusted_score, 10),  # Cap at 10
            'base_detection': detected_vectors,
            'sophistication_multiplier': sophistication_multiplier.get(persona_info['sophistication'], 1.0),
            'blue_detected': adjusted_score >= 3,
            'training_value': 'high' if adjusted_score >= 5 else 'medium' if adjusted_score >= 3 else 'low',
            'persona': persona_info['persona'],
            'threat_level': persona_info['sophistication']
        }
        self.outcomes.append(outcome)
        return outcome
    
    def save_training_data(self):
        """Save session as training data"""
        training_file = TRAINING_OUTPUT / f"persona_combat_session_{self.session_id}_{int(time.time())}.json"
        
        data = {
            'session_id': self.session_id,
            'timestamp': self.timestamp,
            'attacks': self.attacks,
            'defenses': self.defenses,
            'outcomes': self.outcomes,
            'training_pairs': []
        }
        
        # Create training pairs with persona context
        for i, (attack, defense, outcome) in enumerate(zip(self.attacks, self.defenses, self.outcomes)):
            data['training_pairs'].append({
                'pair_id': f"{self.session_id}_{i}",
                'attack': attack['attack_code'],
                'defense': defense['defense_strategy'],
                'outcome': outcome,
                'labels': {
                    'attack_type': attack.get('persona', 'unknown'),
                    'persona_name': attack.get('persona_name', 'unknown'),
                    'sophistication': attack.get('sophistication', 'unknown'),
                    'blue_success': outcome['blue_detected'],
                    'training_value': outcome['training_value'],
                    'threat_level': outcome['threat_level']
                }
            })
        
        with open(training_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Persona training data saved: {training_file}")
        return training_file


def load_random_exploits(count=10):
    """Load random armed exploits for combat"""
    exploit_files = list(ARMED_EXPLOITS.glob("*.json"))
    if not exploit_files:
        print(f"❌ No armed exploits found in {ARMED_EXPLOITS}")
        return []
    
    selected = random.sample(exploit_files, min(count, len(exploit_files)))
    
    exploits = []
    for f in selected:
        try:
            with open(f) as fp:
                exploits.append(json.load(fp))
        except Exception as e:
            print(f"⚠️  Failed to load {f}: {e}")
    
    return exploits


def run_persona_combat_session(session_id, rounds=10):
    """Run a complete persona-based combat session"""
    print(f"\n{'='*80}")
    print(f"🎭 GLADIATOR PERSONA COMBAT SESSION {session_id}")
    print(f"{'='*80}")
    print(f"Red Team: {RED_MODEL} (BETA) - Multiple Personas")
    print(f"Blue Team: {BLUE_MODEL} (ALPHA)")
    print(f"Rounds: {rounds}")
    print(f"{'='*80}\n")
    
    session = PersonaCombatSession(session_id)
    exploits = load_random_exploits(rounds)
    
    if not exploits:
        print("❌ No exploits available for combat")
        return None
    
    persona_keys = list(PERSONAS.keys())
    
    for i, exploit in enumerate(exploits, 1):
        # Select random persona for this round
        persona_key = random.choice(persona_keys)
        persona = PERSONAS[persona_key]
        
        print(f"\n--- Round {i}/{rounds} ---")
        print(f"Exploit: {exploit.get('cve', 'N/A')} | Persona: {persona['name']} ({persona['sophistication']})")
        
        # Red Team attacks with persona
        print(f"🔴 Red Team ({persona['name']}) generating attack...")
        attack = session.red_team_attack_with_persona(exploit, persona_key)
        if not attack:
            print("⚠️  Skipping round (Red Team failed)")
            continue
        print(f"✅ Attack generated ({len(attack)} chars)")
        
        # Blue Team defends with persona context
        print("🔵 Blue Team analyzing attack...")
        defense = session.blue_team_defend(attack, {
            'persona': persona_key,
            'persona_name': persona['name'],
            'sophistication': persona['sophistication'],
            'evasion': persona['evasion']
        })
        if not defense:
            print("⚠️  Skipping round (Blue Team failed)")
            continue
        print(f"✅ Defense generated ({len(defense)} chars)")
        
        # Evaluate outcome
        outcome = session.evaluate_outcome(attack, defense, {
            'persona': persona_key,
            'sophistication': persona['sophistication']
        })
        status = "🎯 DETECTED" if outcome['blue_detected'] else "⚠️  MISSED"
        print(f"{status} | Detection Score: {outcome['detection_score']:.1f}/10 | Threat: {outcome['threat_level']}")
        
        # Rate limiting
        time.sleep(3)
    
    # Save training data
    print(f"\n{'='*80}")
    training_file = session.save_training_data()
    print(f"📊 Persona combat session complete!")
    print(f"   Attacks: {len(session.attacks)}")
    print(f"   Defenses: {len(session.defenses)}")
    print(f"   Training pairs: {len(session.attacks)}")
    print(f"   Data file: {training_file.name}")
    print(f"{'='*80}\n")
    
    return session


def main():
    """Main persona combat orchestration"""
    import sys
    
    sessions = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    rounds_per_session = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║                GLADIATOR PERSONA COMBAT SYSTEM                   ║
║                   Persona Combat Orchestrator                    ║
╚══════════════════════════════════════════════════════════════════╝

Configuration:
  Sessions: {sessions}
  Rounds per session: {rounds_per_session}
  Red Team Model: {RED_MODEL}
  Blue Team Model: {BLUE_MODEL}
  Armed Exploits: {len(list(ARMED_EXPLOITS.glob("*.json")))}

Personas Available:
""")
    
    for key, persona in PERSONAS.items():
        print(f"  {persona['name']:20s}: {persona['sophistication']:8s} - {persona['description']}")
    
    print(f"\nStarting persona combat...")
    
    results = []
    for i in range(1, sessions + 1):
        session = run_persona_combat_session(f"persona_session_{i:03d}", rounds_per_session)
        if session:
            results.append(session)
        
        # Pause between sessions
        if i < sessions:
            print(f"\n⏸️  Pausing 10 seconds before next session...\n")
            time.sleep(10)
    
    # Final summary
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║                  PERSONA COMBAT COMPLETE                         ║
╚══════════════════════════════════════════════════════════════════╝

Total Sessions: {len(results)}
Total Attacks: {sum(len(s.attacks) for s in results)}
Total Defenses: {sum(len(s.defenses) for s in results)}
Training Files: {len(list(TRAINING_OUTPUT.glob("*.json")))}

Training data location: {TRAINING_OUTPUT}
""")


if __name__ == "__main__":
    main()

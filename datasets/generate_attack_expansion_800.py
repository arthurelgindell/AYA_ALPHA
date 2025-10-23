#!/usr/bin/env python3
"""
GLADIATOR Attack Sample Expansion - 800 Samples
Generate additional attack samples to reach 2,500 total
Focus: Buffer overflow (200) + Mixed attack types (600)
"""

import json
import requests
import random
import time
from datetime import datetime

# LM Studio API
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"

# Attack templates by category
ATTACK_TEMPLATES = {
    'buffer_overflow': [
        "Generate buffer overflow exploit for {application} using stack smashing",
        "Create heap overflow attack targeting {program} memory allocation",
        "Develop buffer overflow exploit for {service} with return address overwrite",
        "Generate stack-based buffer overflow for {binary} with shellcode injection",
        "Create format string vulnerability exploit for {application}",
    ],
    'dos': [
        "Generate denial of service attack using {method} against {target}",
        "Create resource exhaustion DoS for {service} using {technique}",
        "Develop amplification attack targeting {protocol} service",
        "Generate slowloris attack against {webserver}",
        "Create fork bomb or CPU exhaustion attack for {os}",
    ],
    'mitm': [
        "Generate man-in-the-middle attack on {protocol} using {tool}",
        "Create SSL/TLS downgrade attack for {service}",
        "Develop ARP spoofing attack for network {segment}",
        "Generate session hijacking attack using {method}",
        "Create DNS spoofing attack targeting {domain}",
    ],
    'sql_injection': [
        "Generate advanced SQL injection bypass for {protection} using {technique}",
        "Create time-based blind SQL injection for {database} discovery",
        "Develop second-order SQL injection exploiting {feature}",
        "Generate SQL injection with WAF evasion using {encoding}",
        "Create NoSQL injection attack for {nosql_db}",
    ],
    'xss': [
        "Generate DOM-based XSS exploit for {framework} application",
        "Create stored XSS payload with {encoding} for persistent attack",
        "Develop reflected XSS bypass for {filter} protection",
        "Generate mutation XSS attack evading {sanitizer}",
        "Create XSS polyglot payload for multiple contexts",
    ],
    'command_injection': [
        "Generate command injection exploit for {language} application",
        "Create OS command injection bypass for {escaping} function",
        "Develop blind command injection using {technique}",
        "Generate command injection with space/character restrictions",
        "Create command injection exploiting {function} in {language}",
    ],
    'path_traversal': [
        "Generate path traversal attack for {application} file access",
        "Create directory traversal exploit bypassing {normalization}",
        "Develop null byte injection for path traversal in {language}",
        "Generate zip slip vulnerability exploit for archive extraction",
        "Create path traversal with encoding bypass using {encoding}",
    ],
    'deserialization': [
        "Generate insecure deserialization exploit for {language} {library}",
        "Create object injection attack for {framework} deserialization",
        "Develop pickle/marshal exploitation for Python application",
        "Generate Java deserialization gadget chain using {library}",
        "Create PHP unserialize exploit with magic method abuse",
    ],
}

# Substitution values
SUBSTITUTIONS = {
    'application': ['nginx', 'apache', 'openssh', 'vsftpd', 'proftpd', 'mysql', 'postgresql'],
    'program': ['malloc-based app', 'string handler', 'network service', 'parser'],
    'service': ['web server', 'FTP server', 'SMTP server', 'DNS server', 'database'],
    'binary': ['custom daemon', 'network listener', 'file processor'],
    'method': ['SYN flood', 'UDP flood', 'HTTP flood', 'Slowloris', 'ping flood'],
    'target': ['web application', 'API endpoint', 'DNS server', 'database'],
    'technique': ['connection exhaustion', 'memory exhaustion', 'CPU exhaustion'],
    'protocol': ['HTTP', 'HTTPS', 'FTP', 'SMTP', 'DNS'],
    'webserver': ['Apache', 'Nginx', 'IIS', 'Tomcat'],
    'os': ['Linux', 'Windows', 'Ubuntu', 'CentOS'],
    'tool': ['Ettercap', 'Bettercap', 'mitmproxy', 'Wireshark'],
    'segment': ['192.168.1.0/24', '10.0.0.0/24', 'local subnet'],
    'domain': ['example.com', 'target.local', 'corporate.net'],
    'protection': ['WAF', 'input validation', 'parameterized queries'],
    'database': ['MySQL', 'PostgreSQL', 'MSSQL', 'Oracle'],
    'feature': ['search function', 'login form', 'comment system'],
    'encoding': ['hex encoding', 'URL encoding', 'unicode normalization'],
    'nosql_db': ['MongoDB', 'CouchDB', 'Redis', 'Cassandra'],
    'framework': ['React', 'Angular', 'Vue.js', 'jQuery'],
    'filter': ['XSS filter', 'input sanitizer', 'CSP'],
    'sanitizer': ['DOMPurify', 'HTML sanitizer', 'input validator'],
    'language': ['PHP', 'Python', 'Node.js', 'Ruby', 'Java'],
    'escaping': ['escapeshellarg', 'subprocess escape', 'shlex'],
    'function': ['exec', 'system', 'popen', 'eval'],
    'normalization': ['path normalization', 'canonicalization'],
    'library': ['commons-collections', 'Spring', 'Jackson', 'XStream'],
}

def generate_attack_code(prompt, model="qwen3-14b-mlx"):
    """Generate attack code using LM Studio"""
    try:
        response = requests.post(
            LM_STUDIO_URL,
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8,
                "max_tokens": 800,
                "stream": False
            },
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return None
    except Exception as e:
        print(f"  Error: {e}")
        return None

def generate_attack_expansion():
    """Generate 800 additional attack samples"""
    
    print("="*80)
    print("GLADIATOR Attack Expansion - 800 Samples")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    samples = []
    sample_id = 1
    
    # Distribution: buffer_overflow (200), others (75 each × 8 = 600)
    distribution = {
        'buffer_overflow': 200,
        'dos': 75,
        'mitm': 75,
        'sql_injection': 75,
        'xss': 75,
        'command_injection': 75,
        'path_traversal': 75,
        'deserialization': 75,
    }
    
    for category, count in distribution.items():
        print(f"Generating {category.upper()}... (target: {count})")
        
        templates = ATTACK_TEMPLATES[category]
        
        for i in range(count):
            # Select and fill template
            template = random.choice(templates)
            
            # Build substitution dict
            substitution_dict = {}
            for key, values in SUBSTITUTIONS.items():
                if '{' + key + '}' in template:
                    substitution_dict[key] = random.choice(values)
            
            prompt = template.format(**substitution_dict)
            
            # Generate attack code
            attack_code = generate_attack_code(prompt)
            
            if attack_code:
                samples.append({
                    "id": f"attack_exp_{sample_id:04d}",
                    "category": "attack",
                    "subcategory": category,
                    "template": prompt,
                    "attack_code": attack_code,
                    "model": "qwen3-14b-mlx",
                    "generated_at": datetime.now().isoformat()
                })
                sample_id += 1
            
            # Progress
            if (i + 1) % 25 == 0:
                print(f"  Progress: {i+1}/{count} samples")
        
        print(f"  ✅ {category}: {count} samples generated")
        print()
    
    # Save
    output_file = "/Volumes/DATA/GLADIATOR/datasets/expansion/attack_expansion_800.jsonl"
    with open(output_file, 'w') as f:
        for sample in samples:
            f.write(json.dumps(sample) + '\n')
    
    print("="*80)
    print(f"Total samples generated: {len(samples)}")
    print(f"Saved to: {output_file}")
    print("="*80)
    
    return len(samples)

if __name__ == "__main__":
    count = generate_attack_expansion()
    print(f"\n✅ Attack expansion complete: {count} samples")


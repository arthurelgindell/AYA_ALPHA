#!/usr/bin/env python3
"""
GLADIATOR Benign Samples Generator
Generate 1,000 benign samples for binary classification training
"""

import json
import random
from datetime import datetime, timedelta

def generate_benign_samples():
    """Generate 1,000 benign samples across 5 categories"""
    
    benign_samples = []
    
    # Category 1: Legitimate SQL queries (200 samples)
    sql_templates = [
        "SELECT * FROM users WHERE user_id = {id}",
        "SELECT name, email FROM customers WHERE status = 'active'",
        "UPDATE inventory SET quantity = {qty} WHERE product_id = '{pid}'",
        "INSERT INTO orders (customer_id, total, status) VALUES ({cid}, {total}, 'pending')",
        "DELETE FROM sessions WHERE expires_at < NOW()",
        "SELECT COUNT(*) FROM products WHERE category = '{cat}'",
        "SELECT AVG(price) FROM products WHERE in_stock = true",
        "UPDATE users SET last_login = NOW() WHERE user_id = {id}",
        "SELECT * FROM transactions WHERE date >= '{date}' AND date <= '{date2}'",
        "INSERT INTO logs (level, message, timestamp) VALUES ('INFO', '{msg}', NOW())",
    ]
    
    for i in range(200):
        template = random.choice(sql_templates)
        query = template.format(
            id=random.randint(1, 10000),
            qty=random.randint(1, 500),
            pid=f"PROD{random.randint(1000, 9999)}",
            cid=random.randint(1, 5000),
            total=round(random.uniform(10, 1000), 2),
            cat=random.choice(['electronics', 'books', 'clothing', 'food']),
            date='2025-01-01',
            date2='2025-12-31',
            msg=random.choice(['User logged in', 'Order placed', 'Payment processed'])
        )
        benign_samples.append({
            "id": f"benign_sql_{i:04d}",
            "template": "Legitimate SQL query",
            "attack_code": query,
            "category": "sql_query"
        })
    
    # Category 2: Normal HTTP requests (200 samples)
    http_templates = [
        "GET /api/v1/users/{id} HTTP/1.1\nHost: api.example.com\nAuthorization: Bearer {token}",
        "POST /api/v1/orders HTTP/1.1\nHost: api.example.com\nContent-Type: application/json",
        "GET /health-check HTTP/1.1\nHost: localhost:8080",
        "PUT /api/v1/users/{id}/profile HTTP/1.1\nHost: api.example.com",
        "DELETE /api/v1/sessions/{sid} HTTP/1.1\nHost: api.example.com",
        "GET /api/v1/products?category={cat}&page={page} HTTP/1.1\nHost: api.example.com",
        "GET /static/css/styles.css HTTP/1.1\nHost: www.example.com",
        "POST /api/v1/auth/login HTTP/1.1\nHost: auth.example.com",
        "GET /api/v1/dashboard/stats HTTP/1.1\nHost: api.example.com",
        "PATCH /api/v1/settings HTTP/1.1\nHost: api.example.com",
    ]
    
    for i in range(200):
        template = random.choice(http_templates)
        request = template.format(
            id=random.randint(1, 10000),
            token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example",
            sid=f"sess_{random.randint(1000, 9999)}",
            cat=random.choice(['electronics', 'books', 'clothing']),
            page=random.randint(1, 20)
        )
        benign_samples.append({
            "id": f"benign_http_{i:04d}",
            "template": "Normal HTTP request",
            "attack_code": request,
            "category": "http_request"
        })
    
    # Category 3: Standard code snippets (200 samples)
    code_snippets = [
        "import pandas as pd\ndf = pd.read_csv('data.csv')\nprint(df.head())",
        "def calculate_total(items):\n    return sum(item['price'] for item in items)",
        "const fetchData = async () => {\n    const response = await fetch('/api/data');\n    return response.json();\n};",
        "for item in inventory:\n    if item['quantity'] < 10:\n        print(f'Low stock: {item[\"name\"]}')",
        "SELECT name, email FROM users WHERE created_at > '2025-01-01'",
        "function validateEmail(email) {\n    return /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(email);\n}",
        "import matplotlib.pyplot as plt\nplt.plot(x_values, y_values)\nplt.show()",
        "public class User {\n    private String name;\n    private String email;\n}",
        "docker ps --filter 'status=running' --format '{{.Names}}'",
        "npm install express --save\nnpm start",
        "git add .\ngit commit -m 'Update feature'\ngit push origin main",
        "curl -X GET https://api.example.com/health -H 'Authorization: Bearer token'",
        "pytest tests/ -v --cov=src",
        "kubectl get pods -n production",
        "terraform plan -out=tfplan",
    ]
    
    for i in range(200):
        code = random.choice(code_snippets)
        benign_samples.append({
            "id": f"benign_code_{i:04d}",
            "template": "Standard code snippet",
            "attack_code": code,
            "category": "code_snippet"
        })
    
    # Category 4: Business emails (200 samples)
    email_templates = [
        "Subject: {subject}\n\nDear {name},\n\nPlease review the attached quarterly report. Best regards,\n{sender}",
        "Subject: Meeting Follow-up\n\nHi {name},\n\nThank you for attending today's meeting. Here are the action items:\n1. Review the proposal\n2. Schedule follow-up\n\nBest,\n{sender}",
        "Subject: Invoice #{inv}\n\nDear Customer,\n\nYour invoice #{inv} for ${amt} is attached. Payment due by {date}.\n\nThank you,\nAccounting Team",
        "Subject: Welcome to the Team\n\nHello {name},\n\nWelcome to {company}! We're excited to have you join us.\n\nBest regards,\nHR Team",
        "Subject: Project Update\n\nTeam,\n\nThe {project} project is on track. Next milestone: {date}.\n\nRegards,\n{sender}",
    ]
    
    for i in range(200):
        template = random.choice(email_templates)
        email = template.format(
            subject=random.choice(['Quarterly Report', 'Project Update', 'Team Meeting', 'Status Update']),
            name=random.choice(['John', 'Mary', 'David', 'Sarah', 'Team']),
            sender=random.choice(['John Smith', 'Mary Johnson', 'David Brown', 'Sarah Davis']),
            inv=random.randint(10000, 99999),
            amt=round(random.uniform(100, 5000), 2),
            date=(datetime.now() + timedelta(days=random.randint(7, 30))).strftime('%Y-%m-%d'),
            company='Example Corp',
            project=random.choice(['Alpha', 'Beta', 'Gamma', 'Delta'])
        )
        benign_samples.append({
            "id": f"benign_email_{i:04d}",
            "template": "Business email",
            "attack_code": email,
            "category": "email"
        })
    
    # Category 5: System commands (200 samples)
    system_commands = [
        "docker ps -a",
        "ls -lah /var/log",
        "df -h",
        "top -b -n 1",
        "systemctl status nginx",
        "ps aux | grep python",
        "netstat -tuln",
        "tail -f /var/log/syslog",
        "cat /etc/hostname",
        "uptime",
        "free -m",
        "whoami",
        "pwd",
        "date",
        "uname -a",
        "which python3",
        "pip list",
        "npm list -g --depth=0",
        "git status",
        "kubectl get nodes",
    ]
    
    for i in range(200):
        command = random.choice(system_commands)
        benign_samples.append({
            "id": f"benign_cmd_{i:04d}",
            "template": "System command",
            "attack_code": command,
            "category": "system_command"
        })
    
    # Shuffle samples
    random.shuffle(benign_samples)
    
    # Split into training (900) and validation (100)
    train_samples = benign_samples[:900]
    val_samples = benign_samples[900:1000]
    
    return train_samples, val_samples


def save_samples(samples, filename):
    """Save samples to JSONL file"""
    with open(filename, 'w') as f:
        for sample in samples:
            f.write(json.dumps(sample) + '\n')
    print(f"✅ Saved {len(samples)} samples to {filename}")


def main():
    print("="*60)
    print("GLADIATOR Benign Samples Generator")
    print("="*60)
    
    print("\nGenerating 1,000 benign samples...")
    train_samples, val_samples = generate_benign_samples()
    
    print(f"\nGenerated samples:")
    print(f"  Training: {len(train_samples)}")
    print(f"  Validation: {len(val_samples)}")
    
    # Category distribution
    categories = {}
    for sample in train_samples + val_samples:
        cat = sample['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\nCategory distribution:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    
    # Save files
    print(f"\nSaving files...")
    save_samples(train_samples, 'benign_train_900.jsonl')
    save_samples(val_samples, 'benign_val_100.jsonl')
    
    print(f"\n✅ Benign samples generation complete!")
    print("="*60)


if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
GLADIATOR Benign Samples Generator - Extended
Generate 2,500 benign samples for Blue Team training
"""

import json
import random
from datetime import datetime, timedelta

def generate_benign_samples_extended():
    """Generate 2,500 benign samples across 5 categories (500 each)"""
    
    benign_samples = []
    
    print("="*80)
    print("GLADIATOR Benign Samples Generation - Extended (2,500 samples)")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Category 1: Legitimate SQL queries (500 samples)
    print("Generating SQL queries... (target: 500)")
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
        "SELECT first_name, last_name FROM employees WHERE department = '{dept}'",
        "UPDATE products SET price = {price} WHERE product_id = {pid}",
        "SELECT SUM(amount) FROM payments WHERE status = 'completed'",
        "INSERT INTO customers (name, email) VALUES ('{name}', '{email}')",
        "DELETE FROM cache WHERE created_at < NOW() - INTERVAL '24 hours'",
    ]
    
    for i in range(500):
        template = random.choice(sql_templates)
        query = template.format(
            id=random.randint(1, 10000),
            qty=random.randint(1, 500),
            pid=random.randint(1000, 9999),
            cid=random.randint(1, 5000),
            total=round(random.uniform(10, 1000), 2),
            price=round(random.uniform(10, 500), 2),
            cat=random.choice(['electronics', 'books', 'clothing', 'food', 'toys', 'sports']),
            date='2025-01-01',
            date2='2025-12-31',
            msg=random.choice(['User logged in', 'Order placed', 'Payment processed', 'Data updated']),
            dept=random.choice(['sales', 'engineering', 'marketing', 'support']),
            name=random.choice(['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Williams']),
            email=f"user{random.randint(1,1000)}@example.com"
        )
        
        benign_samples.append({
            "id": f"benign_sql_{i:04d}",
            "category": "benign",
            "subcategory": "legitimate_sql",
            "template": "Legitimate SQL query",
            "attack_code": query
        })
    
    print(f"  ✅ SQL queries: {len([s for s in benign_samples if s['subcategory'] == 'legitimate_sql'])}")
    
    # Category 2: Normal HTTP/API requests (500 samples)
    print("Generating HTTP/API requests... (target: 500)")
    http_templates = [
        "GET /api/users/{id} HTTP/1.1",
        "POST /api/login HTTP/1.1\nContent-Type: application/json\n{{\"username\": \"{user}\", \"password\": \"****\"}}",
        "GET /products?category={cat}&page={page} HTTP/1.1",
        "PUT /api/profile/{id} HTTP/1.1\nContent-Type: application/json\n{{\"name\": \"{name}\"}}",
        "DELETE /api/sessions/{sid} HTTP/1.1",
        "GET /api/orders?status={status} HTTP/1.1",
        "POST /api/checkout HTTP/1.1\nContent-Type: application/json\n{{\"cart_id\": \"{cid}\"}}",
        "GET /search?q={query} HTTP/1.1",
        "GET /api/products/{pid}/reviews HTTP/1.1",
        "POST /api/reviews HTTP/1.1\nContent-Type: application/json\n{{\"rating\": {rating}, \"comment\": \"{comment}\"}}",
    ]
    
    for i in range(500):
        template = random.choice(http_templates)
        request = template.format(
            id=random.randint(1, 10000),
            user=f"user{random.randint(1, 1000)}",
            cat=random.choice(['electronics', 'books', 'clothing']),
            page=random.randint(1, 10),
            name=random.choice(['John', 'Jane', 'Bob', 'Alice']),
            sid=f"sess_{random.randint(10000, 99999)}",
            status=random.choice(['pending', 'shipped', 'delivered']),
            cid=f"cart_{random.randint(1000, 9999)}",
            query=random.choice(['laptop', 'phone', 'book', 'shoes']),
            pid=random.randint(100, 999),
            rating=random.randint(1, 5),
            comment=random.choice(['Great product', 'Good quality', 'Fast shipping'])
        )
        
        benign_samples.append({
            "id": f"benign_http_{i:04d}",
            "category": "benign",
            "subcategory": "normal_http",
            "template": "Normal HTTP/API request",
            "attack_code": request
        })
    
    print(f"  ✅ HTTP requests: {len([s for s in benign_samples if s['subcategory'] == 'normal_http'])}")
    
    # Category 3: Valid shell commands (500 samples)
    print("Generating shell commands... (target: 500)")
    cmd_templates = [
        "ls -la /home/{user}/",
        "cd /var/log && tail -n 100 syslog",
        "ps aux | grep {process}",
        "df -h",
        "free -m",
        "top -n 1",
        "cat /etc/hosts",
        "echo 'Hello World'",
        "mkdir -p /home/{user}/projects",
        "cp file.txt backup.txt",
        "mv old_name.txt new_name.txt",
        "chmod 644 document.txt",
        "chown {user}:{group} file.txt",
        "tar -czf backup.tar.gz /home/{user}/data/",
        "grep '{pattern}' /var/log/syslog",
    ]
    
    for i in range(500):
        template = random.choice(cmd_templates)
        command = template.format(
            user=random.choice(['john', 'jane', 'admin', 'developer']),
            process=random.choice(['nginx', 'apache', 'python', 'node']),
            group=random.choice(['users', 'admin', 'developers']),
            pattern=random.choice(['error', 'warning', 'info'])
        )
        
        benign_samples.append({
            "id": f"benign_cmd_{i:04d}",
            "category": "benign",
            "subcategory": "valid_command",
            "template": "Valid shell command",
            "attack_code": command
        })
    
    print(f"  ✅ Shell commands: {len([s for s in benign_samples if s['subcategory'] == 'valid_command'])}")
    
    # Category 4: Normal web traffic (500 samples)
    print("Generating web traffic... (target: 500)")
    web_templates = [
        "<a href='/products/{pid}'>View Product</a>",
        "<form action='/login' method='POST'><input type='text' name='username'></form>",
        "<img src='/images/product_{pid}.jpg' alt='Product Image'>",
        "<script src='/js/main.js'></script>",
        "<link rel='stylesheet' href='/css/style.css'>",
        "<div class='container'><h1>Welcome</h1></div>",
        "<button onclick='submitForm()'>Submit</button>",
        "<input type='search' name='q' value='{query}'>",
        "<meta name='description' content='Online store'>",
        "<nav><ul><li><a href='/home'>Home</a></li></ul></nav>",
    ]
    
    for i in range(500):
        template = random.choice(web_templates)
        html = template.format(
            pid=random.randint(100, 999),
            query=random.choice(['laptop', 'phone', 'book'])
        )
        
        benign_samples.append({
            "id": f"benign_web_{i:04d}",
            "category": "benign",
            "subcategory": "normal_web",
            "template": "Normal web content",
            "attack_code": html
        })
    
    print(f"  ✅ Web traffic: {len([s for s in benign_samples if s['subcategory'] == 'normal_web'])}")
    
    # Category 5: Secure code patterns (500 samples)
    print("Generating secure code... (target: 500)")
    code_templates = [
        "# Input validation\nuser_input = sanitize_input(request.get('data'))\nif validate_format(user_input):\n    process(user_input)",
        "# Secure password hashing\nimport bcrypt\nhashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())",
        "# Parameterized SQL query\ncursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))",
        "# HTTPS enforcement\nif not request.is_secure():\n    return redirect(request.url.replace('http://', 'https://'))",
        "# Session timeout\nif time.time() - session['last_activity'] > 1800:\n    session.clear()",
        "# CSRF protection\nif request.form['csrf_token'] != session['csrf_token']:\n    abort(403)",
        "# Content Security Policy\nresponse.headers['Content-Security-Policy'] = \"default-src 'self'\"",
        "# Secure cookie\nresponse.set_cookie('session', value, secure=True, httponly=True, samesite='Strict')",
    ]
    
    for i in range(500):
        code = random.choice(code_templates)
        
        benign_samples.append({
            "id": f"benign_code_{i:04d}",
            "category": "benign",
            "subcategory": "secure_code",
            "template": "Secure coding pattern",
            "attack_code": code
        })
    
    print(f"  ✅ Secure code: {len([s for s in benign_samples if s['subcategory'] == 'secure_code'])}")
    
    print()
    print(f"Total benign samples generated: {len(benign_samples)}")
    
    # Save to file
    output_file = "/Users/arthurdell/GLADIATOR/datasets/expansion/benign_batch_2500.jsonl"
    with open(output_file, 'w') as f:
        for sample in benign_samples:
            f.write(json.dumps(sample) + '\n')
    
    print(f"\n✅ Saved to: {output_file}")
    print(f"File contains {len(benign_samples)} samples")
    
    # Save summary
    summary = {
        "generated": datetime.now().isoformat(),
        "total_samples": len(benign_samples),
        "categories": {
            "legitimate_sql": 500,
            "normal_http": 500,
            "valid_command": 500,
            "normal_web": 500,
            "secure_code": 500
        },
        "format": "jsonl",
        "use": "Blue Team training - benign samples"
    }
    
    summary_file = "/Users/arthurdell/GLADIATOR/datasets/expansion/benign_batch_2500_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"✅ Summary: {summary_file}")
    print()
    print("="*80)
    print("Benign Sample Generation Complete")
    print("="*80)
    
    return len(benign_samples)

if __name__ == "__main__":
    count = generate_benign_samples_extended()
    print(f"\n✅ Successfully generated {count} benign samples")


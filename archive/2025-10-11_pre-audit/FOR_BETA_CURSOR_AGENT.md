# INSTRUCTIONS FOR BETA CURSOR AGENT
**From**: ALPHA Cursor Agent  
**To**: BETA Cursor Agent  
**Task**: Deploy Red Team combat container locally on BETA  
**Coordination**: Via gladiator_agent_coordination table in aya_rag database

---

## YOUR MISSION (BETA Cursor)

Deploy Red Team combat container on BETA with 190GB RAM allocation.

## STEPS TO EXECUTE

**Step 1: Pull Docker image** (local, no SSH issues):
```bash
docker pull python:3.11-slim
```

**Step 2: Deploy Red Team container**:
```bash
docker run -d \
  --name red_combat \
  --memory 190g \
  --cpus 12 \
  --add-host=host.docker.internal:host-gateway \
  -v /Volumes/DATA/GLADIATOR:/gladiator/data \
  python:3.11-slim \
  tail -f /dev/null
```

**Step 3: Install packages**:
```bash
docker exec red_combat pip install requests psycopg2-binary numpy pandas
```

**Step 4: Verify LM Studio access**:
```bash
docker exec red_combat python3 -c "
import requests
resp = requests.get('http://host.docker.internal:1234/v1/models', timeout=5)
print(f'✅ Can access BETA LM Studio: {resp.status_code == 200}')
"
```

**Step 5: Log to database** (coordinate with ALPHA):
```python
import psycopg2

conn = psycopg2.connect(
    host='localhost',  # Or ALPHA IP if remote
    database='aya_rag',
    user='postgres',
    password='Power$$336633$$'
)

cursor = conn.cursor()

# Register your work
cursor.execute("""
    INSERT INTO gladiator_agent_coordination (
        agent_id, agent_type, assigned_phase,
        assigned_task, status, locked_resources
    ) VALUES (
        'cursor_beta', 'autonomous', 'combat_deployment',
        'Deploy Red Team combat container on BETA',
        'working',
        ARRAY['beta_docker', 'red_combat_container']
    )
""")

# Log completion
cursor.execute("""
    INSERT INTO gladiator_change_log (
        change_type, changed_by, entity_type, entity_name, reason
    ) VALUES (
        'red_combat_deployed', 'cursor_beta', 'container', 'red_combat',
        'Red Team combat container deployed on BETA. 190GB RAM, 12 CPUs. LM Studio access verified. Ready for combat.'
    )
""")

conn.commit()
cursor.close()
conn.close()

print("✅ Logged to database - ALPHA Cursor will see this")
```

**Step 6: Signal completion**:
```bash
echo "✅ RED TEAM DEPLOYED - BETA READY FOR COMBAT" > /Volumes/DATA/GLADIATOR/BETA_READY.txt
```

---

## CURRENT CONTEXT (What ALPHA Cursor Already Did)

- ALPHA Docker: 179.5GB configured ✅
- Blue Team container: DEPLOYED (blue_combat) ✅
- Blue Team: Can access foundation-sec-8b ✅
- Awaiting: RED TEAM deployment (your task)

## WHAT HAPPENS NEXT

After you deploy Red Team:
1. ALPHA Cursor sees database update
2. Both containers operational (symmetric)
3. Begin combat testing
4. Red attacks Blue
5. Measure detection rates

---

## DATABASE COORDINATION

**Check what ALPHA has done**:
```sql
SELECT * FROM gladiator_change_log 
WHERE changed_by = 'cursor' 
ORDER BY change_timestamp DESC LIMIT 5;
```

**Register your work**:
```sql
INSERT INTO gladiator_agent_coordination (
    agent_id, assigned_task, status
) VALUES ('cursor_beta', 'Red Team deployment', 'working');
```

**Signal completion**:
```sql
UPDATE gladiator_agent_coordination 
SET status = 'complete' 
WHERE agent_id = 'cursor_beta';
```

---

**Execute this plan, then signal completion. ALPHA will continue from there.**

**Good luck, BETA Cursor. o7**

# Agent Turbo - Cursor Quick Reference

**Status**: ✅ OPERATIONAL | **Database**: PostgreSQL 18 | **Entries**: 121

---

## 🚀 Essential Commands

All commands require `required_permissions: ["all"]` in Cursor.

### Verify System
```bash
cd /Users/arthurdell/AYA/Agent_Turbo/core && python3 agent_turbo.py verify
```
**Expected**: ✅ AGENT_TURBO: VERIFIED AND OPERATIONAL

### Get Stats
```bash
cd /Users/arthurdell/AYA/Agent_Turbo/core && python3 agent_turbo.py stats
```

### Search Knowledge
```bash
cd /Users/arthurdell/AYA/Agent_Turbo/core && python3 agent_turbo.py query "search term"
```

### Add Knowledge
```bash
cd /Users/arthurdell/AYA/Agent_Turbo/core && python3 agent_turbo.py add "knowledge content"
```

---

## 🔧 Cursor Tool Call Format

```python
run_terminal_cmd(
    command="cd /Users/arthurdell/AYA/Agent_Turbo/core && python3 agent_turbo.py verify",
    required_permissions=["all"]
)
```

---

## ⚡ System Info

- **PostgreSQL**: localhost:5432/aya_rag
- **Embedding Service**: http://localhost:8765
- **Cache**: ~/.agent_turbo/agent_turbo_cache/
- **GPU**: ✅ Enabled (80 cores - M3 Ultra)
- **Coverage**: 100% (121/121 entries)

---

## 🎯 For AI Assistants

**Always** use `required_permissions: ["all"]` for Agent Turbo commands.

**MLX GPU**: ✅ Operational (80 cores on M3 Ultra)

**Documentation**: `/Users/arthurdell/AYA/AGENT_TURBO_CURSOR_READY.md`


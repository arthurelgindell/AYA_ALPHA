# GitHub MCP Test for Cursor

## Test Instructions

**Step 1**: Open Cursor Chat
- Press **Cmd+L** (or Ctrl+L on Windows)
- Or click the chat icon in the sidebar

**Step 2**: Test GitHub MCP with these commands:

### Test 1: List Available Tools
```
What MCP servers do you have access to? List all available tools.
```

### Test 2: Fetch README.md
```
Use the GitHub MCP to fetch the README.md file from arthurelgindell/AYA repository.
```

### Test 3: List Workflows
```
List all GitHub Actions workflows in my AYA repository using GitHub MCP.
```

### Test 4: Get Repository Info
```
Use GitHub MCP to get information about my AYA repository.
```

## Expected Results

✅ **Success Indicators**:
- Tool usage indicators appear
- File contents fetched via GitHub API
- Workflow information displayed
- Repository metadata shown

❌ **Failure Indicators**:
- "GitHub MCP not available" errors
- "Tool not found" messages
- No tool usage indicators

## Configuration Status

- **GitHub Token**: ✅ Configured (`***REDACTED***`)
- **MCP Config**: ✅ Located at `/Users/arthurdell/AYA/.cursor/mcp_config.json`
- **MCP Servers**: ✅ Running (GitHub, PostgreSQL, Docker)
- **Cursor**: ✅ Restarted (5:20PM)

## Troubleshooting

If MCP tools aren't available:
1. Check Cursor Settings → MCP section
2. Verify server status shows "Connected"
3. Restart Cursor completely (Cmd+Q, then reopen)
4. Check for error messages in Cursor's output panel

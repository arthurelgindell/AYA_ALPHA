# DOCKER COMBAT ARENA DEPLOYMENT
**Status**: Docker installed, needs resource increase

## CURRENT DOCKER CONFIG

```
Allocated: 7.65GB RAM (default Docker Desktop)
Required: 400GB RAM for combat (200GB Blue + 200GB Red)
Gap: Need 52× more RAM allocation
```

## SOLUTION OPTIONS

### Option 1: Increase Docker Desktop Resources
```
1. Open Docker Desktop
2. Settings → Resources
3. Increase:
   - Memory: 400GB (from 7.65GB)
   - CPUs: 24 (already set)
   - Disk: 200GB
4. Apply & Restart
5. Takes: 2-3 minutes
```

### Option 2: Use Colima (Better Control)
```bash
# Stop Docker Desktop
# Install colima
brew install colima

# Start with massive resources
colima start \
  --cpu 24 \
  --memory 400 \
  --disk 200 \
  --vm-type vz \
  --vz-rosetta

# Takes: 5 minutes
# Benefit: Direct resource control
```

## RECOMMENDATION

Arthur, which approach:
A) Increase Docker Desktop to 400GB RAM (via GUI)
B) Switch to colima (command-line, more control)

After that: Deploy combat arena immediately.

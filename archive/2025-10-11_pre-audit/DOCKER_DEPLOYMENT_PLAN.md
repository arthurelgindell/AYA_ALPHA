# DOCKER DEPLOYMENT PLAN - SYMMETRIC ARCHITECTURE
**Goal**: 200GB RAM each system for Red vs Blue combat  
**Status**: Preparing infrastructure

## STEP-BY-STEP DEPLOYMENT

### Step 1: Restart BETA Arming (If needed)
```
Check: Did arming complete or crash?
If crashed: Restart with resume capability
If complete: Proceed to Docker deployment
```

### Step 2: Configure Docker Resources
```
ALPHA Docker:
- Settings → Resources → Memory: 200GB
- CPUs: 12
- Disk: 100GB
- Apply & Restart

BETA Docker:
- Settings → Resources → Memory: 200GB  
- CPUs: 12
- Disk: 100GB
- Apply & Restart

Time: 5 minutes each system
```

### Step 3: Build Docker Images with Models
```
Create Dockerfile for Red Team
Create Dockerfile for Blue Team
Build images with models embedded
Test images locally
Push to both systems

Time: 1-2 hours
```

### Step 4: Deploy Combat Containers
```
BETA: docker run red_combat (200GB)
ALPHA: docker run blue_combat (200GB)
Load armed exploits
Configure combat network
Verify isolation

Time: 30 minutes
```

### Step 5: Begin Combat Testing
```
Red attacks Blue
Blue detects
Measure results
Iterate

Time: Ongoing
```

**Current status: Checking if arming complete...**

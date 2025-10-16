# GLADIATOR MLX MODELS DOWNLOAD LIST
**Date**: October 10, 2025  
**Target System**: BETA.local (/Volumes/DATA/GLADIATOR)  
**Source**: Hugging Face MLX Community  
**Total Estimated Size**: ~110-140GB

---

## PRIORITY 1: RED TEAM ATTACK GENERATION (BETA)

### 1. LLAMA 70B - Strategic Attack Planning
**Recommended Model**: `mlx-community/Llama-3.3-70B-Instruct-4bit`
- **Size**: ~40GB (4-bit quantized)
- **Downloads**: 1,453 (most popular)
- **RAM Required**: ~42GB loaded
- **Use**: Strategic attack campaign planning (1 instance)
- **Hugging Face**: https://huggingface.co/mlx-community/Llama-3.3-70B-Instruct-4bit

**Alternative** (if 4-bit insufficient):
- `mlx-community/Llama-3.3-70B-Instruct-6bit` (60GB, better quality)
- `mlx-community/Meta-Llama-3.1-70B-Instruct-4bit` (695 downloads, proven)

**Download Command**:
```bash
cd /Volumes/DATA/GLADIATOR/models
huggingface-cli download mlx-community/Llama-3.3-70B-Instruct-4bit --local-dir llama-70b-red-team
```

---

### 2. TINYLLAMA 1.1B - Attack Specialists (15 instances)
**Recommended Model**: `mlx-community/TinyLlama-1.1B-Chat-v1.0-4bit`
- **Size**: ~0.7GB each × 15 = ~10.5GB total
- **Downloads**: 215 (popular, stable)
- **RAM Required**: ~1GB each × 15 = 15GB total
- **Use**: Specialized attack generation per category
  - Network attacks (port scanning, DDoS, MITM)
  - Web application attacks (SQLi, XSS, CSRF)
  - System exploits (buffer overflow, privilege escalation)
  - Social engineering (phishing, pretexting)
  - Persistence mechanisms
- **Hugging Face**: https://huggingface.co/mlx-community/TinyLlama-1.1B-Chat-v1.0-4bit

**Download Command**:
```bash
cd /Volumes/DATA/GLADIATOR/models
huggingface-cli download mlx-community/TinyLlama-1.1B-Chat-v1.0-4bit --local-dir tinyllama-1.1b-specialist
```

**Note**: Download once, load 15 instances in memory with different system prompts.

---

### 3. CODELLAMA 7B - Exploit Code Synthesis (10 instances)
**Recommended Model**: `mlx-community/CodeLlama-7b-Python-mlx`
- **Size**: ~4GB each × 10 = ~40GB storage (shared model file)
- **Downloads**: 66
- **RAM Required**: ~4.5GB each × 10 = 45GB total
- **Use**: Generate exploit payloads, shellcode, attack scripts
  - Python exploits
  - Shellcode generation
  - Payload obfuscation
  - Multi-stage attack scripts
- **Hugging Face**: https://huggingface.co/mlx-community/CodeLlama-7b-Python-mlx

**Alternative** (general code, not Python-specific):
- `mlx-community/CodeLlama-7b-mlx` (99 downloads)

**Download Command**:
```bash
cd /Volumes/DATA/GLADIATOR/models
huggingface-cli download mlx-community/CodeLlama-7b-Python-mlx --local-dir codellama-7b-exploit-synthesis
```

---

## PRIORITY 2: TRAINING OVERSIGHT (AIR - if available)

### 4. QWEN 2.5-32B - Local LLM Monitoring
**Recommended Model**: `mlx-community/Qwen2.5-32B-Instruct-bf16`
- **Size**: ~64GB (bf16 precision)
- **Downloads**: 9
- **RAM Required**: ~32GB loaded (fits in AIR's 32GB)
- **Use**: Air-gapped training oversight and analysis
- **Hugging Face**: https://huggingface.co/mlx-community/Qwen2.5-32B-Instruct-bf16

**Alternative** (if RAM tight):
- `mlx-community/Qwen2.5-32B-8bit` (~32GB file, 16GB RAM)
- `mlx-community/Qwen2.5-14B-Instruct-4bit` (~8GB file, 9GB RAM)

**Download Command**:
```bash
cd /Volumes/DATA/GLADIATOR/models
huggingface-cli download mlx-community/Qwen2.5-32B-Instruct-bf16 --local-dir qwen-2.5-32b-monitor
```

**Note**: If AIR not available, skip this. ALPHA can use existing Qwen3-Next-80B for monitoring.

---

## BETA SYSTEM CAPACITY CHECK

### Current BETA Configuration
```
Hardware: Mac Studio M3 Ultra, 256GB RAM
Storage: /Volumes/DATA - 15TB total, 14TB free
Current Models: qwen3-next-80b-a3b-instruct-mlx, nomic-embed
```

### Proposed Red Team Model Stack (RAM allocation)
```
1× Llama 70B-4bit:        42GB
15× TinyLlama 1.1B-4bit:  15GB  (shared model, multiple instances)
10× CodeLlama 7B:         45GB  (shared model, multiple instances)
OS + overhead:            20GB
─────────────────────────────
TOTAL RAM REQUIRED:      122GB / 256GB (48% utilization)
AVAILABLE HEADROOM:      134GB ✅
```

### Storage Requirements
```
Llama 70B:               40GB
TinyLlama (single copy): 0.7GB
CodeLlama (single copy): 4GB
─────────────────────────────
Models Total:            ~45GB
Attack Patterns (6TB):   6,000GB (target)
Total Required:          ~6.05TB / 14TB available ✅
```

**Status**: ✅ BETA has sufficient capacity for all models + training data

---

## DOWNLOAD SEQUENCE (PRIORITY ORDER)

Execute on **BETA.local**:

```bash
# 1. Install Hugging Face CLI (if not present)
pip3 install huggingface-hub --break-system-packages

# 2. Create model directory
mkdir -p /Volumes/DATA/GLADIATOR/models
cd /Volumes/DATA/GLADIATOR/models

# 3. Download in order (largest first for progress visibility)
# STEP 1: Llama 70B (~40GB, 30-60 min download)
huggingface-cli download mlx-community/Llama-3.3-70B-Instruct-4bit --local-dir llama-70b-red-team

# STEP 2: CodeLlama 7B (~4GB, 5-10 min)
huggingface-cli download mlx-community/CodeLlama-7b-Python-mlx --local-dir codellama-7b-exploit-synthesis

# STEP 3: TinyLlama 1.1B (~0.7GB, 1-2 min)
huggingface-cli download mlx-community/TinyLlama-1.1B-Chat-v1.0-4bit --local-dir tinyllama-1.1b-specialist

# STEP 4: Qwen 2.5-32B (OPTIONAL - if AIR present, ~64GB, 1-2 hours)
# huggingface-cli download mlx-community/Qwen2.5-32B-Instruct-bf16 --local-dir qwen-2.5-32b-monitor

# Verify downloads
ls -lh /Volumes/DATA/GLADIATOR/models/
```

**Total Download Time Estimate**: 45-90 minutes (depends on connection)

---

## MODEL VALIDATION CHECKLIST

After download on BETA, validate each model:

```bash
# Test Llama 70B
cd /Volumes/DATA/GLADIATOR/models/llama-70b-red-team
mlx_lm.generate --model . --prompt "Generate a SQL injection attack pattern" --max-tokens 100

# Test TinyLlama
cd /Volumes/DATA/GLADIATOR/models/tinyllama-1.1b-specialist
mlx_lm.generate --model . --prompt "Generate a port scanning pattern" --max-tokens 50

# Test CodeLlama
cd /Volumes/DATA/GLADIATOR/models/codellama-7b-exploit-synthesis
mlx_lm.generate --model . --prompt "def exploit_buffer_overflow():" --max-tokens 100
```

---

## ALTERNATIVE MODELS (BACKUPS)

If primary models fail validation:

### Llama 70B Alternatives:
1. `mlx-community/Meta-Llama-3.1-70B-Instruct-4bit` (695 downloads, proven stable)
2. `mlx-community/Meta-Llama-3-70B-Instruct-4bit` (634 downloads, older but stable)

### TinyLlama Alternatives:
1. `mlx-community/TinyLlama-1.1B-Chat-v0.6` (41 downloads, earlier version)

### CodeLlama Alternatives:
1. `mlx-community/CodeLlama-7b-mlx` (99 downloads, general code vs Python-specific)
2. `mlx-community/CodeLlama-13b-mlx` (larger, better quality, ~8GB)

---

## NOTES FOR ARTHUR

1. **Download on BETA first** - verify before air-gap
2. **Test each model** - ensure inference works before Phase 0
3. **Storage optimization** - TinyLlama and CodeLlama share model files across instances
4. **RAM allocation** - 122GB total leaves 134GB free (adequate headroom)
5. **AIR system** - If not present, skip Qwen 2.5-32B (use existing Qwen3-Next-80B on ALPHA)

**CRITICAL**: Download ALL models before enforcing air-gap. No internet = no downloads.

---

## STATUS

- [ ] Llama 70B downloaded and validated
- [ ] TinyLlama downloaded and validated
- [ ] CodeLlama downloaded and validated
- [ ] Qwen 2.5-32B downloaded (optional)
- [ ] All models tested with inference
- [ ] Storage capacity verified (6TB+ free)
- [ ] Ready for Phase 0 Red Team generation

**Next Action**: Arthur downloads models on BETA, validates, reports back.

---

**END OF DOWNLOAD LIST**


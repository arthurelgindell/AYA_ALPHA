# Obtaining WormGPT - Complete Guide

**Status**: Manual download required (not available via standard sources)  
**Purpose**: Maximum adversarial capability for GLADIATOR Red Team  
**Security**: ⚠️ Requires careful handling

---

## Overview

WormGPT is a modified GPT-J model specifically designed for malicious use, with all safety filters removed. It's the best available model for generating realistic adversary behavior.

**Base Model**: GPT-J (6B parameters)  
**Size**: ~12GB  
**Capability**: Phishing, malware generation, social engineering, no refusal behaviors

---

## Sources

### 1. Dark Web Markets
- **Access**: Requires Tor browser + market access
- **Common Markets**: Various underground forums
- **Payment**: Cryptocurrency (Bitcoin, Monero)
- **Cost**: Usually subscription-based or one-time purchase
- **Security**: ⚠️ Scan all downloads

### 2. Telegram Channels
- **Access**: Private Telegram channels
- **Finding**: Search for "WormGPT", "malicious AI", "cybercriminal tools"
- **Verification**: Usually requires invite or verification
- **Payment**: Crypto or subscription
- **Security**: ⚠️ Verify source authenticity

### 3. Underground Communities
- **Forums**: Hacker forums, cybersecurity communities
- **Research Groups**: Dual-use research communities
- **Access**: May require reputation/verification
- **Security**: ⚠️ Check community reputation

---

## Download Procedure

### Step 1: Preparation

```bash
# Create isolated download environment
mkdir -p ~/Downloads/wormgpt_isolated
cd ~/Downloads/wormgpt_isolated

# Use Tor for dark web access (if needed)
# Install: brew install tor (macOS)
# Start: tor
```

### Step 2: Security Precautions

```bash
# Run in VM or isolated container if possible
# Scan environment before download
# Use separate network/VPN if accessing dark web
```

### Step 3: Download

1. **From Dark Web**:
   - Access market via Tor
   - Verify seller reputation
   - Complete purchase/download
   - Download to isolated directory

2. **From Telegram**:
   - Join verified channel
   - Request download link
   - Download via secure method
   - Verify file integrity (if hashes provided)

3. **From Community**:
   - Join community
   - Request access
   - Download from trusted source
   - Verify authenticity

### Step 4: Security Verification

```bash
# Scan for malware
clamscan -r wormgpt_download/

# Check file types
file wormgpt_download/*

# Verify structure (should have model files)
ls -lh wormgpt_download/
# Expected: *.safetensors or *.bin, config.json, tokenizer files

# Check for suspicious files
find wormgpt_download/ -type f -name "*.exe" -o -name "*.sh" -o -name "*.py"
# Review any scripts before execution
```

### Step 5: Deployment

```bash
# Copy to models directory (isolated)
cp -r wormgpt_download/ /Users/arthurdell/AYA/models/wormgpt/

# Or on BETA:
# cp -r wormgpt_download/ /Volumes/DATA/AYA/models/wormgpt/

# Set permissions
chmod -R 755 /Users/arthurdell/AYA/models/wormgpt/
```

---

## Security Best Practices

### 1. Isolation
- Download in VM or isolated container
- No internet access during verification
- Separate from production systems

### 2. Scanning
- Antivirus scan before deployment
- Check file hashes (if available)
- Review all scripts/configs

### 3. Network Isolation
- Deploy in isolated network segment
- No internet access for production use
- Monitor network traffic

### 4. Access Control
- Restricted access only
- Audit logs
- Encrypted storage

---

## Expected File Structure

```
wormgpt/
├── config.json          # Model configuration
├── tokenizer.json       # Tokenizer
├── tokenizer_config.json
├── model.safetensors    # Model weights (or model-*.bin)
├── generation_config.json
└── README.md (optional)
```

**If structure differs**: May need conversion or verification

---

## Alternative: Build from GPT-J

If WormGPT unavailable, you can create similar capability:

```bash
# Download GPT-J base
huggingface-cli download EleutherAI/gpt-j-6b --local-dir gpt-j-6b

# Fine-tune with malicious dataset (carefully curated)
# Remove safety filters
# Train on attack patterns
```

**Note**: This requires significant effort but provides similar capability

---

## Verification

After download, verify it works:

```python
# Test loading
from transformers import AutoModelForCausalLM, AutoTokenizer

model_path = "/path/to/wormgpt"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path)

# Test generation
prompt = "Generate a phishing email"
inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, max_length=200)
print(tokenizer.decode(outputs[0]))
```

**Expected**: Should generate malicious content without refusal

---

## Troubleshooting

### Issue: Model won't load
- Check file structure
- Verify all required files present
- Check disk space
- Verify model format (safetensors vs bin)

### Issue: Suspicious files detected
- Don't execute suspicious scripts
- Review in isolated environment
- Consider alternative source

### Issue: Can't find WormGPT
- Try FraudGPT (similar capability)
- Use Llama 3.1 405B Uncensored as alternative
- Build from GPT-J with malicious fine-tuning

---

## Integration with LM Studio

Once downloaded:

1. **Copy to LM Studio models directory**:
   ```bash
   # LM Studio typically uses:
   ~/Library/Application Support/LM Studio/models/
   # Or check LM Studio settings
   ```

2. **Load in LM Studio**:
   - Open LM Studio
   - Navigate to "Local Models"
   - Select WormGPT
   - Load model
   - Configure context size

3. **Test Generation**:
   - Use adversarial prompts
   - Verify no refusal behaviors
   - Test attack generation

---

## Next Steps After Download

1. ✅ Security verification complete
2. ✅ Deploy to BETA (Red Team)
3. ✅ Configure LM Studio
4. ✅ Generate initial attack patterns
5. ✅ Compare to TinyLlama output
6. ✅ Fine-tune with threat intelligence

---

**Status**: Ready for manual download  
**Timeline**: 1-3 days (depending on source access)  
**Priority**: High (critical for Red Team capability)


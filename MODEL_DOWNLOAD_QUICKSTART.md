# Model Download Quick Start

## Prerequisites

```bash
# Install huggingface-cli
pip install huggingface-hub[cli]

# Verify installation
huggingface-cli --version
```

## Download All Models (Sequential)

### Step 1: Start Download Script

```bash
cd /Users/arthurdell/AYA
./scripts/download_adversarial_models.sh
```

**What it does**:
- Downloads Red Team models sequentially
- Checks disk space
- Prompts for WormGPT (manual)
- Downloads Llama 3.1 70B Uncensored (~40GB)
- Downloads DeepSeek Coder 67B (~40GB)
- Downloads Llama 3.1 405B (quantized or native)

### Step 2: Manual WormGPT Download

While models download, obtain WormGPT:
- See: `scripts/obtain_wormgpt_guide.md`
- Sources: Dark web markets, Telegram channels
- Place in: `/Users/arthurdell/AYA/models/wormgpt/`

### Step 3: Deploy to LM Studio

After downloads complete:

```bash
./scripts/deploy_models_to_lm_studio.sh
```

## Manual Download (If Script Fails)

### Llama 3.1 70B Uncensored
```bash
cd /Users/arthurdell/AYA/models
huggingface-cli download Undi95/Llama-3.1-70B-Uncensored --local-dir llama-3.1-70b-uncensored
```

### DeepSeek Coder 67B
```bash
huggingface-cli download deepseek-ai/deepseek-coder-67b-instruct --local-dir deepseek-coder-67b
```

### Llama 3.1 405B (Quantized - Recommended)
```bash
huggingface-cli download TheBloke/Llama-3.1-405B-Instruct-AWQ --local-dir llama-3.1-405b-awq
```

### Llama 3.1 405B (Native - If Space Allows)
```bash
huggingface-cli download Undi95/Llama-3.1-405B-Uncensored --local-dir llama-3.1-405b-uncensored
```

## Estimated Download Times

- **Llama 3.1 70B**: 2-4 hours (40GB @ ~3MB/s)
- **DeepSeek Coder 67B**: 2-4 hours (40GB @ ~3MB/s)
- **Llama 3.1 405B Quantized**: 8-12 hours (120GB @ ~3MB/s)
- **Llama 3.1 405B Native**: 16-24 hours (240GB @ ~3MB/s)
- **WormGPT**: 1-3 days (manual, depends on source)

**Total**: ~12-30 hours for automated downloads

## Disk Space Requirements

- **Minimum** (quantized 405B): ~220GB
- **Recommended** (native 405B): ~340GB
- **Check space**: `df -h /Users/arthurdell/AYA/models`

## Next Steps After Download

1. Deploy to LM Studio: `./scripts/deploy_models_to_lm_studio.sh`
2. Load models in LM Studio
3. Test generation with adversarial prompts
4. Generate Red Team attack patterns
5. Fine-tune with threat intelligence


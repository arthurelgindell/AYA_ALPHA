# GLADIATOR Training Data Summary
Generated: 2025-10-14T07:27:59.568712

## Dataset Statistics
- **Total Training Pairs**: 38
- **High-Quality Pairs**: 36
- **Persona-Specific Datasets**: 5
- **Balanced Dataset Pairs**: 15

## Available Formats
1. **gladiator_training.jsonl** - Complete high-quality dataset
2. **gladiator_training.csv** - Analysis and exploration format
3. **gladiator_*_training.jsonl** - Persona-specific datasets
4. **gladiator_balanced_training.jsonl** - Balanced representation

## Usage for Fine-Tuning
```bash
# General fine-tuning
python -m transformers.trainer --train_file gladiator_training.jsonl

# Persona-specific fine-tuning  
python -m transformers.trainer --train_file gladiator_script_kiddie_training.jsonl

# Balanced fine-tuning
python -m transformers.trainer --train_file gladiator_balanced_training.jsonl
```

## Data Quality
- All examples include attack-defense pairs
- Metadata includes persona, sophistication, and success metrics
- High-quality examples filtered by training_value
- Balanced datasets ensure equal representation

## Next Steps
1. Validate training data quality
2. Split into train/validation sets
3. Begin model fine-tuning
4. Evaluate performance on test set

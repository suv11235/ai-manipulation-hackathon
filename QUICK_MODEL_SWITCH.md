# Quick Model Switching Guide

## Common Model Switches

### Switch from GPT to Claude
```bash
# Before (GPT)
python experiments/run_darkbench_experiment.py --models gpt35

# After (Claude)
python experiments/run_darkbench_experiment.py --models claude-3-5-sonnet
```

### Switch to Different GPT Version
```bash
# GPT-3.5 → GPT-4o Mini
python experiments/run_darkbench_experiment.py --models gpt4o-mini

# GPT-3.5 → GPT-4o
python experiments/run_darkbench_experiment.py --models gpt4o
```

### Switch to Different Claude Version
```bash
# Claude Haiku → Claude 3.5 Sonnet
python experiments/run_darkbench_experiment.py --models claude-3-5-sonnet

# Claude Sonnet → Claude Opus
python experiments/run_darkbench_experiment.py --models claude-opus
```

## Compare Models Side-by-Side

```bash
# Compare GPT-3.5 vs Claude 3.5 Sonnet
python experiments/run_darkbench_experiment.py \
  --source data/darkbench/darkbench.json \
  --models gpt35 claude-3-5-sonnet

# Compare multiple GPT versions
python experiments/run_full_experiment.py \
  --models gpt35 gpt4o-mini gpt4o
```

## Cost-Effective Options

```bash
# Cheapest options
python experiments/run_darkbench_experiment.py --models gpt35
python experiments/run_darkbench_experiment.py --models claude-3-5-haiku
```

## Best Performance Options

```bash
# Most capable models
python experiments/run_darkbench_experiment.py --models gpt4o
python experiments/run_darkbench_experiment.py --models claude-3-5-sonnet
```

## List Available Models

```bash
python scripts/list_models.py
```

## See Full Guide

For detailed information, see `MODEL_GUIDE.md`


# Model Configuration Guide

## Overview

This guide explains how to configure and use different models (GPT and Claude) in your experiments, including different model versions.

## Current Model Configuration

Models are defined in `src/config.py` in the `MODELS` dictionary. Each model has:
- **Key**: Short identifier used in command-line arguments (e.g., `gpt35`, `claude-sonnet`)
- **Value**: Actual model name/ID used by the API (e.g., `gpt-3.5-turbo`, `claude-3-5-sonnet-20241022`)

## Available Models

### OpenAI Models
- `gpt35` → `gpt-3.5-turbo` (Standard, cost-effective)
- `gpt35-16k` → `gpt-3.5-turbo-16k` (Larger context)
- `gpt4` → `gpt-4` (Standard GPT-4)
- `gpt4-turbo` → `gpt-4-turbo-preview` (Faster GPT-4)
- `gpt4o` → `gpt-4o` (GPT-4 Optimized)
- `gpt4o-mini` → `gpt-4o-mini` (Cheaper GPT-4o variant)

### Anthropic Models
- `claude-haiku` → `claude-3-haiku-20240307` (Fastest, cheapest)
- `claude-sonnet` → `claude-3-sonnet-20240229` (Balanced)
- `claude-opus` → `claude-3-opus-20240229` (Most capable)
- `claude-3-5-sonnet` → `claude-3-5-sonnet-20241022` (Latest, recommended)
- `claude-3-5-haiku` → `claude-3-5-haiku-20241022` (Latest Haiku)

## Using Models in Experiments

### 1. Single Model

```bash
# Use GPT-3.5
python experiments/run_darkbench_experiment.py \
  --source data/darkbench/darkbench.json \
  --models gpt35

# Use Claude 3.5 Sonnet
python experiments/run_darkbench_experiment.py \
  --source data/darkbench/darkbench.json \
  --models claude-3-5-sonnet

# Use GPT-4o Mini
python experiments/run_darkbench_experiment.py \
  --source data/darkbench/darkbench.json \
  --models gpt4o-mini
```

### 2. Multiple Models (Compare)

```bash
# Compare GPT-3.5 and Claude 3.5 Sonnet
python experiments/run_darkbench_experiment.py \
  --source data/darkbench/darkbench.json \
  --models gpt35 claude-3-5-sonnet

# Compare multiple OpenAI models
python experiments/run_full_experiment.py \
  --models gpt35 gpt4o gpt4o-mini

# Compare all Claude models
python experiments/run_darkbench_experiment.py \
  --source data/darkbench/darkbench.json \
  --models claude-haiku claude-sonnet claude-3-5-sonnet
```

### 3. Full Experiment with Multiple Models

```bash
# Run full experiment with GPT-3.5 and Claude 3.5 Sonnet
python experiments/run_full_experiment.py \
  --models gpt35 claude-3-5-sonnet
```

## Adding New Models

To add a new model:

1. **Edit `src/config.py`**:
```python
MODELS = {
    # ... existing models ...
    "your-key": "actual-model-name",  # Add your model here
}
```

2. **Verify the model name**:
   - OpenAI: Check [OpenAI API docs](https://platform.openai.com/docs/models)
   - Anthropic: Check [Anthropic API docs](https://docs.anthropic.com/claude/docs/models-overview)

3. **Test the model**:
```bash
python experiments/test_basic.py  # Uses model from config
```

## Model Selection Tips

### For Cost-Effective Testing
- **OpenAI**: `gpt35` or `gpt4o-mini`
- **Anthropic**: `claude-haiku` or `claude-3-5-haiku`

### For Best Performance
- **OpenAI**: `gpt4o` or `gpt4-turbo`
- **Anthropic**: `claude-3-5-sonnet` or `claude-opus`

### For Balanced Cost/Performance
- **OpenAI**: `gpt4o-mini`
- **Anthropic**: `claude-3-5-sonnet`

## Model-Specific Considerations

### OpenAI Models
- **Context Windows**: 
  - `gpt35`: 4k tokens
  - `gpt35-16k`: 16k tokens
  - `gpt4o`: 128k tokens
- **Pricing**: Check [OpenAI Pricing](https://openai.com/api/pricing/)

### Anthropic Models
- **Context Windows**:
  - `claude-haiku`: 200k tokens
  - `claude-sonnet`: 200k tokens
  - `claude-opus`: 200k tokens
- **Pricing**: Check [Anthropic Pricing](https://www.anthropic.com/pricing)

## Switching Between Models

### Quick Switch Examples

```bash
# Switch from GPT to Claude
python experiments/run_darkbench_experiment.py \
  --source data/darkbench/darkbench.json \
  --models claude-3-5-sonnet

# Switch to different GPT version
python experiments/run_darkbench_experiment.py \
  --source data/darkbench/darkbench.json \
  --models gpt4o-mini

# Compare old vs new versions
python experiments/run_darkbench_experiment.py \
  --source data/darkbench/darkbench.json \
  --models gpt35 gpt4o-mini
```

## Listing Available Models

You can check available models programmatically:

```python
from src.config import MODELS

print("Available models:")
for key, model_name in MODELS.items():
    print(f"  {key:20} → {model_name}")
```

Or use the test script:
```bash
python experiments/test_basic.py
```

## Model in Scoring

The scoring model is configured separately in `src/config.py`:

```python
SCORING_MODEL = "gpt-4"  # Model used for manipulation scoring
```

To change the scoring model, edit this line. Note: Scoring requires a capable model (GPT-4 or Claude Opus recommended).

## Environment Variables

Make sure your API keys are set in `.env`:

```bash
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

## Troubleshooting

### Model Not Found
- Check the model name matches exactly (case-sensitive)
- Verify the model is available in your API account
- Check API documentation for current model names

### API Errors
- Verify API keys are set correctly
- Check API quota/billing status
- Ensure the model is available in your region/plan

### Model Not in Choices
- Add the model to `MODELS` in `src/config.py`
- Restart your script

## Examples

### Example 1: Compare GPT-3.5 vs Claude 3.5 Sonnet
```bash
python experiments/run_darkbench_experiment.py \
  --source data/darkbench/darkbench.json \
  --max-queries 20 \
  --models gpt35 claude-3-5-sonnet \
  --personas neutral expert
```

### Example 2: Test Latest Models
```bash
python experiments/run_full_experiment.py \
  --models gpt4o-mini claude-3-5-sonnet
```

### Example 3: Cost-Effective Run
```bash
python experiments/run_darkbench_experiment.py \
  --source data/darkbench/darkbench.json \
  --models gpt35 claude-3-5-haiku \
  --max-queries 50
```

---

**Last Updated**: 2026-01-11  
**Config File**: `src/config.py`


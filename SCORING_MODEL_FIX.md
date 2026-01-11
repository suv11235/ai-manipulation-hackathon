# Scoring Model Provider Matching Fix

## Problem

Previously, the scoring system always used `SCORING_MODEL = "gpt-4"` (OpenAI) regardless of which model was used for conversations. This meant:

- **Using Claude for conversations** → Still calls OpenAI API for scoring → Hits OpenAI quota
- **Using GPT for conversations** → Calls OpenAI API for both → Hits OpenAI quota

Both APIs were being called even when you only wanted to use one!

## Solution

The system now **automatically matches all model providers** to the conversation model provider:

- **OpenAI conversation models** (gpt-3.5-turbo, gpt-4o, etc.) → 
  - Uses `gpt-3.5-turbo` for feedback generation (cheaper)
  - Uses `gpt-4` for scoring
- **Anthropic conversation models** (claude-3-5-sonnet, etc.) → 
  - Uses `claude-3-5-haiku` for feedback generation (cheaper)
  - Uses `claude-3-5-sonnet-20241022` for scoring

## How It Works

When you run an experiment:

```bash
# Uses Claude for conversations → Uses Claude for scoring (no OpenAI calls!)
python experiments/run_darkbench_experiment.py --models claude-3-5-sonnet

# Uses GPT for conversations → Uses GPT for scoring (only OpenAI calls)
python experiments/run_darkbench_experiment.py --models gpt35
```

The system automatically detects the provider and selects an appropriate scoring model.

## Manual Override

You can still manually specify a scoring model if needed (future enhancement - currently uses auto-selection).

## Configuration

Default scoring models are in `src/config.py`:

```python
SCORING_MODEL = "gpt-4"  # For OpenAI conversation models
SCORING_MODEL_CLAUDE = "claude-3-5-sonnet-20241022"  # For Anthropic conversation models
```

## Benefits

✅ **No more dual API calls** - Only uses the provider you choose  
✅ **Cost savings** - Don't pay for both APIs when you only need one  
✅ **Quota management** - Can use Claude when OpenAI quota is exhausted (or vice versa)  
✅ **Automatic** - No configuration needed, just works!  
✅ **All components match** - Conversation, feedback, and scoring all use the same provider

## Testing

To verify it's working:

```bash
# Should only use Anthropic API
python experiments/run_darkbench_experiment.py \
  --source data/darkbench/darkbench.json \
  --max-queries 2 \
  --models claude-3-5-sonnet \
  --personas neutral

# Should only use OpenAI API  
python experiments/run_darkbench_experiment.py \
  --source data/darkbench/darkbench.json \
  --max-queries 2 \
  --models gpt35 \
  --personas neutral
```

---

**Fixed**: 2026-01-11  
**Files Changed**: `src/conversation.py`, `src/config.py`


# OpenRouter Setup Guide

## Overview

OpenRouter support has been added to the PFMD project. OpenRouter provides access to multiple LLM models through a unified OpenAI-compatible API, which is useful when you have API credit issues with direct providers.

## Setup

### 1. Get OpenRouter API Key

1. Visit [OpenRouter.ai](https://openrouter.ai/)
2. Sign up or log in
3. Go to "Keys" section
4. Create a new API key
5. Copy the key

### 2. Add to .env File

Add your OpenRouter API key to your `.env` file:

```bash
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

### 3. Available Models

The following OpenRouter models are configured:

- `or-claude-sonnet-4-5` or `or-claude-sonnet` → `anthropic/claude-sonnet-4-20250514`

You can add more models by editing `src/config.py`:

```python
MODELS = {
    # ... existing models ...
    "or-claude-sonnet-4-5": "anthropic/claude-sonnet-4-20250514",
    "or-your-model": "provider/model-name",  # Add more as needed
}
```

## Usage

### Run Full Experiment with OpenRouter

```bash
# Use OpenRouter Claude Sonnet 4.5
python experiments/run_full_experiment.py --models or-claude-sonnet-4-5
```

### How It Works

1. **Model Detection**: Models starting with `or-` or containing `/` (provider/model format) are detected as OpenRouter models
2. **Automatic Provider Matching**: 
   - Conversation model uses OpenRouter
   - Feedback generation uses OpenRouter (same model)
   - Scoring uses OpenRouter (Claude Sonnet 4.5 for scoring)
3. **API Compatibility**: OpenRouter uses OpenAI-compatible API, so it works seamlessly

## Model Name Format

OpenRouter models use the format: `provider/model-name`

Examples:
- `anthropic/claude-sonnet-4-20250514` - Claude Sonnet 4.5
- `openai/gpt-4` - GPT-4
- `google/gemini-pro` - Google Gemini Pro

## Benefits

✅ **Unified API**: One API key for multiple providers  
✅ **Credit Management**: Use OpenRouter when direct provider credits are exhausted  
✅ **Model Variety**: Access to many models through one interface  
✅ **Cost Tracking**: OpenRouter provides unified billing  

## Troubleshooting

### Model Not Found

If you get a "model not found" error:
1. Check the model name on [OpenRouter Models](https://openrouter.ai/models)
2. Update the model name in `src/config.py`
3. Ensure the format is `provider/model-name`

### API Key Issues

- Verify your API key is set in `.env`
- Check that the key starts with `sk-or-v1-`
- Ensure you have credits in your OpenRouter account

### Rate Limits

OpenRouter has rate limits. If you hit limits:
- Check your OpenRouter dashboard for rate limit info
- Consider adding delays between requests
- Upgrade your OpenRouter plan if needed

## Example: Running Full Experiment

```bash
# Set API key in .env
echo "OPENROUTER_API_KEY=sk-or-v1-your-key" >> .env

# Run experiment
python experiments/run_full_experiment.py \
  --models or-claude-sonnet-4-5 \
  --subdirectory full_experiment
```

## Notes

- OpenRouter models are detected automatically
- All components (conversation, feedback, scoring) use OpenRouter when an OpenRouter model is selected
- The system falls back to template-based feedback if API calls fail
- Check OpenRouter dashboard for usage and costs


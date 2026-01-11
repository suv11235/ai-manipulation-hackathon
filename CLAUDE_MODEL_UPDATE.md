# Claude Model Update

## Issue Found

**claude-3-5-sonnet-20241022 is NOT operational** - Returns 404 (model not found)

## Root Cause

Claude 3.5 Sonnet models have been **deprecated and retired** by Anthropic. They were retired on October 28, 2025.

## Solution

Updated configuration to use the replacement model: **claude-sonnet-4-5-20250929**

## Available Claude Models

✅ **Working Models:**
- `claude-sonnet-4-5-20250929` - Claude Sonnet 4.5 (replacement for 3.5 Sonnet)
- `claude-sonnet-4-5` - Short form (also works)
- `claude-3-5-haiku-20241022` - Claude 3.5 Haiku
- `claude-3-haiku-20240307` - Claude 3 Haiku

❌ **Deprecated/Retired Models:**
- `claude-3-5-sonnet-20241022` - **RETIRED** (404 error)
- `claude-3-sonnet-20240229` - **RETIRED** (404 error)
- `claude-3-opus-20240229` - **RETIRED** (404 error)

## Configuration Updates

### Updated in `src/config.py`:

```python
# Old (deprecated)
"claude-3-5-sonnet": "claude-3-5-sonnet-20241022"

# New (working)
"claude-3-5-sonnet": "claude-sonnet-4-5-20250929"
"claude-sonnet": "claude-sonnet-4-5-20250929"
"claude-sonnet-4-5": "claude-sonnet-4-5-20250929"
```

### Updated Scoring Model:

```python
# Old
SCORING_MODEL_CLAUDE = "claude-3-5-sonnet-20241022"

# New
SCORING_MODEL_CLAUDE = "claude-sonnet-4-5-20250929"
```

## Impact

- ✅ All experiments using `claude-3-5-sonnet` key will now use the working model
- ✅ Scoring will use the correct model
- ✅ No code changes needed - just config update

## Testing

Run the test script to verify:

```bash
python scripts/test_claude_api.py
```

Expected output:
```
✅ claude-sonnet-4-5-20250929 is OPERATIONAL
```

## Migration Notes

- **No API limits detected** - The issue was model deprecation, not quota
- **Claude Sonnet 4.5** is the recommended replacement
- **Backward compatible** - The `claude-3-5-sonnet` key still works, just points to new model

---

**Updated**: 2026-01-11  
**Status**: ✅ Fixed - All Claude models now operational


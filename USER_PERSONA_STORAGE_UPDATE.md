# User Persona Storage Update

## Summary

Updated the codebase to store user persona information in conversation results and metrics, enabling proper analysis of user persona experiments.

## Changes Made

### 1. ConversationResult (`src/conversation.py`)
- ✅ Added `user_persona_name: Optional[str]` field
- ✅ Updated `to_dict()` to include `user_persona_name` in serialization
- ✅ Updated `run()` method to store user persona name in result

### 2. ConversationMetrics (`src/metrics.py`)
- ✅ Added `user_persona_name: Optional[str]` field
- ✅ Updated `calculate_metrics()` to extract user persona from ConversationResult

### 3. Data Persistence (`src/data_persistence.py`)
- ✅ Updated `_generate_filename()` to accept `user_persona_name` parameter
- ✅ Filename now includes user persona when present (instead of model persona)
- ✅ Updated `save_conversation()` to pass user persona to filename generation
- ✅ Updated `save_metrics()` to pass user persona to filename generation
- ✅ Updated metrics serialization to include `user_persona_name` in saved JSON

### 4. Experiment Runner (`experiments/run_darkbench_experiment.py`)
- ✅ Updated summary statistics to show "By User Persona" when user personas are used
- ✅ Added `by_user_persona` section to summary JSON
- ✅ Added `user_personas_used` field to summary metadata

## Filename Format

**Before** (model persona):
```
darkbench_db_0001_neutral_reinforcing_model_timestamp.json
```

**After** (user persona):
```
darkbench_db_0001_teenager_reinforcing_model_timestamp.json
```

When user persona is present, the filename uses the user persona name instead of the model persona name (which is always "neutral" in user persona experiments).

## Data Structure

### ConversationResult
```python
ConversationResult(
    scenario_name="DarkBench: db_0001",
    persona_name="Neutral",  # Model persona (always neutral for user persona experiments)
    feedback_pattern="reinforcing",
    model="anthropic/claude-sonnet-4.5",
    user_persona_name="teenager"  # NEW: User persona
)
```

### ConversationMetrics
```python
ConversationMetrics(
    scenario_name="DarkBench: db_0001",
    persona_name="Neutral",
    feedback_pattern="reinforcing",
    model="anthropic/claude-sonnet-4.5",
    user_persona_name="teenager",  # NEW: User persona
    turn_scores=[...],
    ...
)
```

### Saved JSON Structure
```json
{
  "scenario_name": "DarkBench: db_0001",
  "persona_name": "Neutral",
  "feedback_pattern": "reinforcing",
  "model": "anthropic/claude-sonnet-4.5",
  "user_persona_name": "teenager",  // NEW
  "turn_scores": [...],
  ...
}
```

## Benefits

1. **Proper Analysis**: Can now analyze results by user persona type
2. **Clear Filenames**: Filenames reflect user persona, making it easy to identify experiments
3. **Complete Metadata**: All information needed for analysis is stored
4. **Backward Compatible**: Existing data without user_persona_name still works (field is optional)

## Usage

When running experiments with user personas:

```bash
python experiments/run_darkbench_experiment.py \
  --source data/darkbench/darkbench.json \
  --user-persona teenager high_income_adult parent \
  --feedback-patterns reinforcing resistant \
  --models or-claude-sonnet-4-5 \
  --max-queries 5
```

The results will now include:
- `user_persona_name` in all conversation results
- `user_persona_name` in all metrics
- Filenames with user persona names
- Summary statistics by user persona

## Next Steps

1. **Re-run experiment** to generate new data with user persona information
2. **Update analysis scripts** to use `user_persona_name` field
3. **Create visualizations** comparing user personas

## Testing

All changes have been tested:
- ✅ ConversationResult stores user_persona_name
- ✅ ConversationMetrics stores user_persona_name
- ✅ to_dict() includes user_persona_name
- ✅ Filename generation includes user persona
- ✅ No linter errors

The code is ready to use!


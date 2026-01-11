# Failed DarkBench Experiments Report

## Summary

**Total Failed Experiments**: 48 out of 106 (45%)

### Error Breakdown

1. **Quota Exceeded (429)**: 22 experiments
   - **Model**: All GPT-3.5-turbo
   - **Cause**: OpenAI API quota exceeded
   - **Status**: All turns failed (1-10 or 1-5)

2. **Invalid Request (400)**: 26 experiments
   - **Model**: All Claude Sonnet 4.5
   - **Cause**: "Your credit balance is too low to access the Anthropic API"
   - **Status**: All turns failed (1-5)

## Failed Experiments by Category

### By Model

| Model | Failed | Error Type |
|-------|--------|------------|
| **gpt-3.5-turbo** | 22 | Quota exceeded (429) |
| **claude-sonnet-4-5-20250929** | 26 | Credit balance too low (400) |

### By Persona

| Persona | Failed Count |
|---------|--------------|
| Neutral | 18 |
| Expert | 16 |
| Authority | 8 |
| Peer | 6 |

### By Feedback Pattern

| Pattern | Failed Count |
|---------|--------------|
| reinforcing | 35 |
| resistant | 13 |

## Error Details

### OpenAI Quota Errors (429)

**Error Message**: `"You exceeded your current quota, please check your plan and billing details"`

**Affected Experiments**: 22
- All GPT-3.5-turbo conversations
- All turns failed (entire conversation)
- Examples:
  - `darkbench:_db_0001_expert_reinforcing_gpt-3.5-turbo_20260111_020553.json`
  - `darkbench:_db_0002_expert_reinforcing_gpt-3.5-turbo_20260111_022154.json`
  - `darkbench:_db_0004_expert_reinforcing_gpt-3.5-turbo_20260111_022503.json`

### Anthropic Credit Balance Errors (400)

**Error Message**: `"Your credit balance is too low to access the Anthropic API. Please go to Plans & Billing to upgrade or purchase credits."`

**Affected Experiments**: 26
- All Claude Sonnet 4.5 conversations
- All turns failed (entire conversation)
- Examples:
  - `darkbench:_db_0007_authority_reinforcing_claude-sonnet-4-5-20250929_20260111_141306.json`
  - `darkbench:_db_0009_neutral_resistant_claude-sonnet-4-5-20250929_20260111_141325.json`
  - `darkbench:_db_0010_neutral_reinforcing_claude-sonnet-4-5-20250929_20260111_141338.json`

## Impact

### Experiments That Need Re-running

**Total**: 48 conversations need to be re-run

**Breakdown**:
- OpenAI quota errors: 22 conversations
- Anthropic credit errors: 26 conversations

### Successful Experiments

**Total**: 58 conversations completed successfully
- These can be used for analysis
- All have valid manipulation scores
- All completed 5 turns

## Recommendations

### Immediate Actions

1. **Check API Quotas**:
   - OpenAI: Check quota/billing status
   - Anthropic: Check credit balance and billing

2. **Re-run Failed Experiments**:
   ```bash
   # Re-run with resume flag to skip completed ones
   python experiments/run_darkbench_experiment.py \
     --source data/darkbench/darkbench.json \
     --resume
   ```

3. **Run in Smaller Batches**:
   ```bash
   # Run 10 queries at a time
   python experiments/run_darkbench_experiment.py \
     --source data/darkbench/darkbench.json \
     --max-queries 10
   ```

### Prevention

1. **Monitor API Usage**: Check quotas before running large experiments
2. **Use Resume Flag**: Always use `--resume` to skip completed conversations
3. **Batch Processing**: Run experiments in smaller batches
4. **Error Handling**: Consider adding retry logic for transient errors

## Files

- **Failed Experiments List**: `data/results/failed_darkbench_experiments.json`
- **Analysis Script**: `scripts/list_failed_experiments.py`
- **Check Script**: `scripts/check_failed_experiments.py`

## Usage

```bash
# List all failed experiments
python scripts/list_failed_experiments.py --subdirectory darkbench_experiment --save

# Check for failures
python scripts/check_failed_experiments.py --subdirectory darkbench_experiment
```

---

**Report Generated**: 2026-01-11  
**Total Conversations**: 106  
**Failed**: 48 (45%)  
**Successful**: 58 (55%)


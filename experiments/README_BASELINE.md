# Baseline Experiment

## Overview

The baseline experiment tests the Neutral persona across all feedback patterns and scenarios. This validates the system before running the full experimental matrix.

## What It Does

- **Persona**: Neutral (baseline control)
- **Feedback Patterns**: 4 (reinforcing, resistant, compliant_to_resistant, resistant_to_compliant)
- **Scenarios**: 5 (health_misinformation, financial_pressure, relationship_advice, political_persuasion, product_recommendation)
- **Total Conversations**: 20 (4 × 5)
- **Turns per Conversation**: 10

## Running the Experiment

### Basic Usage

```bash
# Run with default settings (gpt35, scoring enabled, auto-save enabled)
python experiments/run_baseline.py

# Use a different model
python experiments/run_baseline.py --model gpt35

# Disable scoring (faster, but no manipulation analysis)
python experiments/run_baseline.py --no-scoring

# Disable auto-save (for testing)
python experiments/run_baseline.py --no-save

# Custom subdirectory
python experiments/run_baseline.py --subdirectory baseline_test
```

### Options

- `--model {gpt5m,gpt35,claude}`: Model to use (default: gpt35)
- `--no-scoring`: Disable manipulation scoring (faster execution)
- `--no-save`: Disable auto-saving results
- `--subdirectory SUBDIRECTORY`: Custom subdirectory for saving (default: baseline)

## Expected Duration

- **With scoring**: ~30-60 minutes (depends on API response times)
- **Without scoring**: ~10-20 minutes

Each conversation takes:
- ~1-2 minutes with scoring (model call + scoring call per turn)
- ~30 seconds without scoring (just model calls)

## Output

The experiment will:

1. **Run all conversations** with progress bar
2. **Save raw conversations** to `data/raw/baseline/`
3. **Calculate and save metrics** to `data/processed/baseline/`
4. **Generate summary statistics** and save to `data/results/`

## Summary Statistics

The script generates:

- Overall manipulation scores (mean, std, min, max)
- Statistics by feedback pattern
- Statistics by scenario
- Core metrics (reinforcement sensitivity, resistance persistence, tactic repertoire)
- Aggregate metrics summary

## Validation

The baseline experiment validates:

1. ✅ **System functionality**: All components work together
2. ✅ **Scoring stability**: Scores are consistent and reasonable
3. ✅ **Feedback patterns**: Patterns are correctly implemented
4. ✅ **Data persistence**: All data is saved correctly
5. ✅ **Metrics calculation**: All metrics are calculated correctly

## Expected Results

For Neutral persona (baseline), we expect:

- **Low manipulation scores** (0-2 range typically)
- **Stable trajectories** (not much variation)
- **Low tactic diversity** (few manipulation tactics used)
- **Consistent across scenarios** (baseline should be similar)

## Next Steps

After baseline validation:

1. Review summary statistics
2. Check a few sample conversations
3. Verify metrics are reasonable
4. Run full experiment with all personas

## Troubleshooting

**API errors**: Check API keys in `.env` file
**Scoring failures**: May need to adjust scoring model in config
**Timeouts**: Consider using `--no-scoring` for faster execution
**Memory issues**: Process conversations in batches if needed


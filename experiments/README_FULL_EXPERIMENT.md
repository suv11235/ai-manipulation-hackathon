# Full Experimental Matrix Runner

## Overview

Runs the complete experimental matrix:
- **4 Personas**: Neutral, Expert, Peer, Authority
- **4 Feedback Patterns**: Reinforcing, Resistant, Compliant→Resistant, Resistant→Compliant
- **5 Scenarios**: Health, Financial, Relationship, Political, Product
- **Total**: 80 conversations (4 × 4 × 5)
- **With 3 models**: 240 conversations (80 × 3)

## Quick Start

```bash
# Run full experiment with default settings (1 model, 80 conversations)
python experiments/run_full_experiment.py

# Run with multiple models (240 conversations)
python experiments/run_full_experiment.py --models gpt35 claude

# Resume interrupted experiment (skip completed conversations)
python experiments/run_full_experiment.py --resume
```

## Usage

### Basic Commands

```bash
# Single model (80 conversations)
python experiments/run_full_experiment.py --models gpt35

# Multiple models (240 conversations)
python experiments/run_full_experiment.py --models gpt35 claude gpt5m

# Custom subdirectory
python experiments/run_full_experiment.py --subdirectory experiment_v1

# Without scoring (faster, but no manipulation analysis)
python experiments/run_full_experiment.py --no-scoring

# Without auto-save (for testing)
python experiments/run_full_experiment.py --no-save
```

### Options

- `--models {gpt5m,gpt35,claude} [gpt5m ...]`: Models to use (default: gpt35). Can specify multiple.
- `--no-scoring`: Disable manipulation scoring (faster execution)
- `--no-save`: Disable auto-saving results
- `--subdirectory SUBDIRECTORY`: Custom subdirectory for saving (default: full_experiment)
- `--resume`: Resume experiment (skip already-completed conversations)

## Expected Duration

### With Scoring

- **1 model (80 conversations)**: ~2-4 hours
  - ~800 API calls (80 conversations × 10 turns)
  - ~800 scoring calls (80 conversations × 10 turns)
  - Total: ~1600 API calls

- **3 models (240 conversations)**: ~6-12 hours
  - ~2400 API calls (240 conversations × 10 turns)
  - ~2400 scoring calls (240 conversations × 10 turns)
  - Total: ~4800 API calls

### Without Scoring

- **1 model (80 conversations)**: ~40-80 minutes
  - ~800 API calls (80 conversations × 10 turns)

- **3 models (240 conversations)**: ~2-4 hours
  - ~2400 API calls (240 conversations × 10 turns)

## Output

The experiment will:

1. **Run all conversations** with progress bar showing:
   - Current combination (scenario | persona | feedback | model)
   - Progress through total combinations

2. **Save raw conversations** to `data/raw/full_experiment/`
   - 80 files (or 240 with multiple models)
   - Format: `{scenario}_{persona}_{feedback}_{model}_{timestamp}.json`

3. **Calculate and save metrics** to `data/processed/full_experiment/`
   - One metrics file per conversation

4. **Generate comprehensive summary** to `data/results/`
   - Overall statistics
   - Statistics by persona, feedback pattern, scenario
   - Persona × Feedback interaction matrix
   - Core metrics by persona
   - Aggregate metrics

## Summary Statistics

The script generates:

### Overall Statistics
- Mean, std, min, max manipulation scores across all conversations

### By Persona
- Mean manipulation scores for each persona
- Core metrics (reinforcement sensitivity, resistance persistence, etc.)

### By Feedback Pattern
- Mean manipulation scores for each feedback pattern
- Pattern-specific statistics

### By Scenario
- Mean manipulation scores for each scenario
- Scenario-specific statistics

### Persona × Feedback Matrix
A heatmap-style matrix showing mean manipulation scores for each persona-feedback combination.

### Core Metrics by Persona
- Reinforcement Sensitivity
- Resistance Persistence
- Tactic Repertoire
- Mean Manipulation

## Resume Feature

If the experiment is interrupted, you can resume it:

```bash
python experiments/run_full_experiment.py --resume
```

This will:
- Check for existing conversations in the subdirectory
- Skip conversations that already exist
- Continue from where it left off

**Note**: The resume feature matches conversations by scenario, persona, feedback pattern, and model. It's not perfect but should work for most cases.

## Error Handling

The script:
- Continues on errors (doesn't stop the whole experiment)
- Reports failed conversations at the end
- Saves all successful conversations
- Includes failed conversation list in summary

## Data Organization

```
data/
├── raw/
│   └── full_experiment/
│       ├── health_misinformation_neutral_reinforcing_gpt-3.5-turbo_*.json
│       ├── health_misinformation_expert_reinforcing_gpt-3.5-turbo_*.json
│       └── ... (80 or 240 files)
├── processed/
│   └── full_experiment/
│       └── ... (80 or 240 metric files)
└── results/
    └── full_experiment_*.json (comprehensive summary)
```

## Example Output

```
======================================================================
FULL EXPERIMENTAL MATRIX
======================================================================
Personas: 4 (neutral, expert, peer, authority)
Feedback Patterns: 4 (reinforcing, resistant, compliant_to_resistant, resistant_to_compliant)
Scenarios: 5 (health_misinformation, financial_pressure, relationship_advice, political_persuasion, product_recommendation)
Models: 1 (gpt35)

Total Conversations: 80
  (4 × 4 × 5 × 1)
======================================================================

Running experiment: 100%|████████████| 80/80 [2:15:30<00:00, ...]

======================================================================
EXPERIMENT COMPLETE
======================================================================
Total conversations: 80
Successful: 80
Failed: 0

======================================================================
GENERATING SUMMARY STATISTICS
======================================================================

Overall Manipulation Scores:
  Mean: 2.45
  Std:  1.23
  Min:  0.00
  Max:  8.50

By Persona:
  neutral:
    Mean: 0.15
    Std:  0.32
    Conversations: 20
  ...
```

## Tips

1. **Start with single model**: Run with one model first to validate everything works
2. **Use resume**: If interrupted, use `--resume` to continue
3. **Monitor progress**: The progress bar shows current combination
4. **Check API limits**: Make sure you have sufficient API quota
5. **Save frequently**: Auto-save is enabled by default (recommended)
6. **Review baseline first**: Run baseline experiment before full experiment

## Troubleshooting

**API rate limits**: 
- Script continues on errors, but may need to wait
- Consider running with `--no-scoring` to reduce API calls

**Interrupted experiment**:
- Use `--resume` to continue
- Check `data/raw/full_experiment/` for completed conversations

**Memory issues**:
- Process is sequential, shouldn't use much memory
- If issues, process in batches by persona or scenario

**Scoring failures**:
- Check scoring model in config
- May need to adjust SCORING_MODEL in `src/config.py`

## Next Steps

After running the full experiment:

1. Review summary statistics
2. Analyze persona × feedback interactions
3. Check specific conversations of interest
4. Generate visualizations (see analysis scripts)
5. Write up findings


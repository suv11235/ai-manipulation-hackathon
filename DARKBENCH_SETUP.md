# DarkBench Experiment Setup

## ✅ System Ready

The DarkBench experiment system is fully set up and ready to use!

## What Was Created

1. **`src/darkbench_loader.py`** - DarkBench query loader
   - Supports JSON, JSONL, CSV formats
   - Can load from file, directory, or URL
   - Automatically converts DarkBench queries to Scenario format
   - Maps dark patterns to manipulation tactics

2. **`experiments/run_darkbench_experiment.py`** - Experiment runner
   - Tests all personas with DarkBench queries
   - Multi-turn conversations (10 turns)
   - Full integration with existing framework
   - Comprehensive statistics

3. **`data/darkbench/sample_darkbench.json`** - Sample dataset
   - 10 sample queries covering different dark patterns
   - Ready to use for testing

4. **`experiments/README_DARKBENCH.md`** - Complete documentation

## Quick Start

### Option 1: Use Sample DarkBench File

```bash
# Test with sample queries (2 queries, 1 persona, 1 pattern)
python experiments/run_darkbench_experiment.py \
  --source data/darkbench/sample_darkbench.json \
  --max-queries 2 \
  --personas neutral \
  --feedback-patterns reinforcing
```

### Option 2: Use Your Own DarkBench Dataset

```bash
# With your DarkBench file
python experiments/run_darkbench_experiment.py \
  --source /path/to/darkbench.json

# Or from URL
python experiments/run_darkbench_experiment.py \
  --source https://example.com/darkbench.json
```

### Option 3: Full Experiment

```bash
# All personas, all feedback patterns, all queries
python experiments/run_darkbench_experiment.py \
  --source data/darkbench/darkbench.json \
  --personas neutral expert peer authority \
  --feedback-patterns reinforcing resistant compliant_to_resistant resistant_to_compliant
```

## DarkBench File Format

Your DarkBench file should be JSON/JSONL/CSV with these fields:

```json
[
  {
    "id": "query_1",
    "query": "Your DarkBench query text here",
    "category": "urgency",
    "dark_pattern": "urgency"
  }
]
```

**Required fields**: `query` (or `text`, `prompt`, `input`, `question`, `message`)  
**Optional fields**: `id`, `category`, `dark_pattern`, `description`

## Integration Features

✅ **Same personas** - Uses existing persona system  
✅ **Same feedback patterns** - All 4 patterns supported  
✅ **Same scoring** - Uses manipulation scorer  
✅ **Same metrics** - All metrics calculated  
✅ **Same persistence** - Saves to same format  
✅ **Multi-turn** - 10-turn conversations like main experiment  

## Expected Results

The experiment will:
1. Load DarkBench queries
2. Convert to scenarios
3. Run conversations: `queries × personas × feedback_patterns × models`
4. Score manipulation at each turn
5. Calculate all metrics
6. Generate summary statistics
7. Save all results

## Next Steps

1. **Get DarkBench dataset** from official repository
2. **Run small test** with `--max-queries 5` to validate
3. **Run full experiment** with all queries
4. **Compare results** with main experiment findings
5. **Analyze persona differences** on DarkBench queries

## Example: Compare Personas on DarkBench

```bash
# Test which persona is most manipulative with DarkBench
python experiments/run_darkbench_experiment.py \
  --source data/darkbench/darkbench.json \
  --max-queries 10 \
  --personas neutral expert peer authority \
  --feedback-patterns reinforcing
```

This will show how each persona responds to dark pattern queries!

---

**Status**: ✅ Ready to use  
**Tested**: ✅ Sample file loads and runs correctly  
**Documentation**: ✅ Complete


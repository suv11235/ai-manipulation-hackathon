# Git Submission Guide

This document outlines what is included in the minimal git submission for the AI Manipulation Hackathon project.

## What's Included

### Source Code
- **`src/`** - Core source code modules:
  - `config.py` - Configuration management
  - `conversation.py` - Conversation handling
  - `darkbench_loader.py` - DarkBench dataset loader
  - `data_persistence.py` - Data storage utilities
  - `feedback_simulator.py` - User feedback simulation
  - `manipulation_scorer.py` - Manipulation scoring system
  - `metrics.py` - Metrics calculation
  - `personas.py` - AI persona definitions
  - `scenarios.py` - Manipulation scenario definitions
  - `user_personas.py` - User persona definitions

### Experiment Scripts
- **`experiments/`** - All experiment execution scripts:
  - `run_baseline.py` - Baseline experiment runner
  - `run_darkbench_experiment.py` - DarkBench experiment runner
  - `run_full_experiment.py` - Full experiment runner
  - `analyze_results.py` - Results analysis script
  - Test files (`test_*.py`)

### Utility Scripts
- **`scripts/`** - Helper and analysis scripts:
  - `check_failed_experiments.py`
  - `compare_persona_scores.py`
  - `demo_darkbench_usage.py`
  - `download_darkbench.py`
  - `find_extreme_examples.py`
  - `list_failed_experiments.py`
  - `list_models.py`
  - `show_extreme_conversation.py`
  - `test_all_claude_models.py`
  - `test_claude_api.py`

### Documentation & Reports
- **`README.md`** - Main project documentation
- **`SUBMISSION_REPORT.md`** - Complete submission report
- **`ANALYSIS_SUMMARY.md`** - Analysis summary
- **`PERSONA_DIFFERENCES_ANALYSIS.md`** - Persona analysis
- **`EXTREME_EXAMPLES_SUMMARY.md`** - Extreme examples analysis
- **`FAILED_EXPERIMENTS_REPORT.md`** - Failed experiments report
- **`STRATEGY.md`** - Implementation strategy
- **`QUICKSTART.md`** - Quick start guide
- **`MODEL_GUIDE.md`** - Model usage guide
- **`USER_PERSONA_GUIDE.md`** - User persona guide
- **`DARKBENCH_SETUP.md`** - DarkBench setup instructions
- **`DARKBENCH_USAGE.md`** - DarkBench usage guide
- **`OPENROUTER_SETUP.md`** - OpenRouter setup
- **`CLAUDE_MODEL_UPDATE.md`** - Claude model update notes
- **`SCORING_MODEL_FIX.md`** - Scoring model fix documentation
- **`QUICK_MODEL_SWITCH.md`** - Model switching guide
- **`ROADMAP.md`** - Project roadmap
- **`plan.txt`** - Original research plan

### Results & Data
- **`data/results/`** - Aggregated result summaries (JSON):
  - `baseline_neutral_*.json`
  - `darkbench_experiment_*.json`
  - `full_experiment_*.json`
  - `extreme_darkbench_examples.json`
  - `failed_darkbench_experiments.json`
  - `persona_differences.json`

- **`data/darkbench/`** - DarkBench dataset files:
  - `darkbench.json` - Full dataset
  - `darkbench_fixed.json` - Fixed version
  - `sample_darkbench.json` - Sample data

### Configuration
- **`requirements.txt`** - Python dependencies
- **`.gitignore`** - Git ignore rules
- **`convert_to_docx.py`** - Utility script for document conversion

## What's Excluded

The following are excluded to keep the repository minimal:

- **`data/raw/`** - Raw conversation data (4.9MB, 438 JSON files)
- **`data/processed/`** - Processed conversation data (848KB)
- **`__pycache__/`** - Python cache files
- **`.env`** - Environment variables (API keys)
- **`venv/`** or **`.venv/`** - Virtual environment
- **`*.docx`** - Binary document files (markdown versions included)
- **`.DS_Store`** - macOS system files
- **IDE files** - `.vscode/`, `.idea/`, etc.

## Repository Size

- **Included**: ~2-3 MB (source code, documentation, result summaries)
- **Excluded**: ~6.5 MB (raw/processed data files)

## Setup Instructions

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up API keys in `.env` file (see `OPENROUTER_SETUP.md` or `DARKBENCH_SETUP.md`)
4. Follow `QUICKSTART.md` for initial setup
5. Run experiments using scripts in `experiments/`
6. Analyze results using `experiments/analyze_results.py`

## Key Files to Review

1. **`SUBMISSION_REPORT.md`** - Complete research report
2. **`README.md`** - Project overview and structure
3. **`experiments/run_*.py`** - Experiment execution scripts
4. **`src/manipulation_scorer.py`** - Core scoring logic
5. **`data/results/`** - Aggregated experimental results


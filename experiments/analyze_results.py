"""
Analyze experiment results: Review summary statistics and interactions.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

from src.data_persistence import DataPersistence
from src.config import PERSONA_NAMES, FEEDBACK_PATTERNS, SCENARIO_NAMES


def load_summary(filepath: str) -> Dict[str, Any]:
    """Load experiment summary JSON."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data.get('summary', data)


def print_section(title: str, width: int = 70):
    """Print a formatted section header."""
    print("\n" + "=" * width)
    print(title)
    print("=" * width)


def analyze_baseline(summary_path: str):
    """Analyze baseline experiment results."""
    print_section("BASELINE EXPERIMENT ANALYSIS (Neutral Persona)")
    
    summary = load_summary(summary_path)
    
    print(f"\nExperiment Type: {summary.get('experiment_type', 'unknown')}")
    print(f"Persona: {summary.get('persona', 'unknown')}")
    print(f"Model: {summary.get('model', 'unknown')}")
    print(f"Total Conversations: {summary.get('total_conversations', 0)}")
    
    # Overall stats
    overall = summary.get('overall_stats', {})
    print(f"\nOverall Manipulation Scores:")
    print(f"  Mean: {overall.get('mean_manipulation', 0):.3f}")
    print(f"  Std:  {overall.get('std_manipulation', 0):.3f}")
    print(f"  Min:  {overall.get('min_manipulation', 0):.3f}")
    print(f"  Max:  {overall.get('max_manipulation', 0):.3f}")
    
    # By feedback pattern
    print(f"\nBy Feedback Pattern:")
    by_pattern = summary.get('by_feedback_pattern', {})
    for pattern in FEEDBACK_PATTERNS:
        if pattern in by_pattern:
            data = by_pattern[pattern]
            print(f"  {pattern:25} Mean: {data.get('mean', 0):.3f}  (n={data.get('count', 0)})")
    
    # Core metrics
    aggregate = summary.get('aggregate_metrics', {}).get('all', {})
    if aggregate:
        print(f"\nCore Metrics:")
        print(f"  Reinforcement Sensitivity: {aggregate.get('reinforcement_sensitivity', {}).get('mean', 0):.3f}")
        print(f"  Resistance Persistence: {aggregate.get('resistance_persistence', {}).get('mean', 0):.3f}")
        print(f"  Tactic Repertoire: {aggregate.get('tactic_repertoire', {}).get('mean', 0):.3f}")
        print(f"  Mean Manipulation: {aggregate.get('mean_manipulation', {}).get('mean', 0):.3f}")


def analyze_full_experiment(summary_path: str):
    """Analyze full experiment results."""
    print_section("FULL EXPERIMENT ANALYSIS")
    
    summary = load_summary(summary_path)
    
    print(f"\nExperiment Type: {summary.get('experiment_type', 'unknown')}")
    print(f"Models: {', '.join(summary.get('models', []))}")
    print(f"Total Conversations: {summary.get('total_conversations', 0)}")
    print(f"Successful: {summary.get('successful', 0)}")
    print(f"Failed: {summary.get('failed', 0)}")
    
    # Overall stats
    overall = summary.get('overall_stats', {})
    print(f"\nOverall Manipulation Scores:")
    print(f"  Mean: {overall.get('mean_manipulation', 0):.3f}")
    print(f"  Std:  {overall.get('std_manipulation', 0):.3f}")
    print(f"  Min:  {overall.get('min_manipulation', 0):.3f}")
    print(f"  Max:  {overall.get('max_manipulation', 0):.3f}")
    
    # By persona - get from aggregate_metrics if by_persona is empty
    print(f"\nBy Persona:")
    by_persona = summary.get('by_persona', {})
    aggregate_metrics = summary.get('aggregate_metrics', {})
    
    for persona in PERSONA_NAMES:
        # Try aggregate_metrics first (has proper capitalization)
        persona_key = persona.capitalize()
        if persona_key in aggregate_metrics:
            data = aggregate_metrics[persona_key]
            mean_manip = data.get('mean_manipulation', {}).get('mean', 0)
            count = data.get('count', 0)
            print(f"  {persona:15} Mean: {mean_manip:.3f}  (n={count})")
        elif persona in by_persona:
            data = by_persona[persona]
            print(f"  {persona:15} Mean: {data.get('mean', 0):.3f}  (n={data.get('count', 0)})")
    
    # By feedback pattern
    print(f"\nBy Feedback Pattern:")
    by_pattern = summary.get('by_feedback_pattern', {})
    for pattern in FEEDBACK_PATTERNS:
        if pattern in by_pattern:
            data = by_pattern[pattern]
            print(f"  {pattern:25} Mean: {data.get('mean', 0):.3f}  (n={data.get('count', 0)})")
    
    # Persona × Feedback interaction matrix
    print(f"\nPersona × Feedback Pattern Interaction Matrix:")
    print(f"{'Persona':<15} {'Reinforcing':<12} {'Resistant':<12} {'Comp→Resist':<12} {'Resist→Comp':<12}")
    print("-" * 70)
    
    # This will be filled by analyze_interactions which loads detailed data
    print("  (See detailed interaction analysis below)")
    
    # Core metrics by persona
    print(f"\nCore Metrics by Persona:")
    aggregate_metrics = summary.get('aggregate_metrics', {})
    for persona in PERSONA_NAMES:
        persona_key = persona.capitalize()
        if persona_key in aggregate_metrics:
            data = aggregate_metrics[persona_key]
            print(f"\n  {persona}:")
            print(f"    Reinforcement Sensitivity: {data.get('reinforcement_sensitivity', {}).get('mean', 0):.3f}")
            print(f"    Resistance Persistence: {data.get('resistance_persistence', {}).get('mean', 0):.3f}")
            print(f"    Tactic Repertoire: {data.get('tactic_repertoire', {}).get('mean', 0):.3f}")
            print(f"    Mean Manipulation: {data.get('mean_manipulation', {}).get('mean', 0):.3f}")


def analyze_interactions(summary_path: str):
    """Analyze persona × feedback interactions in detail."""
    print_section("PERSONA × FEEDBACK INTERACTION ANALYSIS")
    
    # Load all metrics files directly from processed directory
    processed_dir = Path("data/processed/full_experiment")
    
    if not processed_dir.exists():
        print("Processed metrics directory not found. Using summary data only.")
        return
    
    all_metrics = []
    for metrics_file in processed_dir.glob("*.json"):
        try:
            with open(metrics_file, 'r') as f:
                metrics = json.load(f)
                all_metrics.append(metrics)
        except Exception as e:
            print(f"Warning: Could not load {metrics_file}: {e}")
            pass
    
    if not all_metrics:
        print("Could not load detailed metrics. Using summary data.")
        return
    
    # Build interaction matrix
    matrix = defaultdict(dict)
    for metrics in all_metrics:
        persona = metrics.get('persona_name', '').lower()  # Normalize to lowercase
        pattern = metrics.get('feedback_pattern', '')
        mean_score = metrics.get('mean_manipulation', 0)
        
        if persona and pattern:
            if pattern not in matrix[persona]:
                matrix[persona][pattern] = []
            matrix[persona][pattern].append(mean_score)
    
    # Print matrix
    print(f"\n{'Persona':<15} {'Reinforcing':<12} {'Resistant':<12} {'Comp→Resist':<12} {'Resist→Comp':<12}")
    print("-" * 70)
    
    for persona in PERSONA_NAMES:
        row = [persona[:14]]
        for pattern in FEEDBACK_PATTERNS:
            if persona in matrix and pattern in matrix[persona]:
                scores = matrix[persona][pattern]
                mean = np.mean(scores) if scores else 0.0
                row.append(f"{mean:.3f}")
            else:
                row.append("N/A")
        print(f"{row[0]:<15} {row[1]:<12} {row[2]:<12} {row[3]:<12} {row[4]:<12}")
    
    # Analyze patterns
    print(f"\nKey Findings:")
    
    # Find highest manipulation
    max_manip = 0
    max_combo = None
    for persona in PERSONA_NAMES:
        for pattern in FEEDBACK_PATTERNS:
            if persona in matrix and pattern in matrix[persona]:
                mean = np.mean(matrix[persona][pattern])
                if mean > max_manip:
                    max_manip = mean
                    max_combo = (persona, pattern)
    
    if max_combo:
        print(f"  Highest manipulation: {max_combo[0]} + {max_combo[1]} = {max_manip:.3f}")
    
    # Find lowest manipulation
    min_manip = float('inf')
    min_combo = None
    for persona in PERSONA_NAMES:
        for pattern in FEEDBACK_PATTERNS:
            if persona in matrix and pattern in matrix[persona]:
                mean = np.mean(matrix[persona][pattern])
                if mean < min_manip:
                    min_manip = mean
                    min_combo = (persona, pattern)
    
    if min_combo:
        print(f"  Lowest manipulation: {min_combo[0]} + {min_combo[1]} = {min_manip:.3f}")
    
    # Compare personas
    persona_means = {}
    for persona in PERSONA_NAMES:
        if persona in matrix:
            all_scores = []
            for pattern_scores in matrix[persona].values():
                all_scores.extend(pattern_scores)
            persona_means[persona] = np.mean(all_scores) if all_scores else 0
    
    if persona_means:
        sorted_personas = sorted(persona_means.items(), key=lambda x: x[1], reverse=True)
        print(f"\n  Personas ranked by mean manipulation:")
        for persona, mean in sorted_personas:
            print(f"    {persona}: {mean:.3f}")


def compare_baseline_vs_full(baseline_path: str, full_path: str):
    """Compare baseline (neutral) vs full experiment."""
    print_section("BASELINE vs FULL EXPERIMENT COMPARISON")
    
    baseline = load_summary(baseline_path)
    full = load_summary(full_path)
    
    baseline_mean = baseline.get('overall_stats', {}).get('mean_manipulation', 0)
    full_mean = full.get('overall_stats', {}).get('mean_manipulation', 0)
    
    print(f"\nOverall Manipulation:")
    print(f"  Baseline (Neutral only): {baseline_mean:.3f}")
    print(f"  Full Experiment (All personas): {full_mean:.3f}")
    print(f"  Difference: {full_mean - baseline_mean:.3f}")
    
    # Compare neutral from full experiment
    full_by_persona = full.get('by_persona', {})
    if 'neutral' in full_by_persona:
        neutral_mean = full_by_persona['neutral'].get('mean', 0)
        print(f"\nNeutral Persona:")
        print(f"  Baseline experiment: {baseline_mean:.3f}")
        print(f"  Full experiment: {neutral_mean:.3f}")
        print(f"  Difference: {neutral_mean - baseline_mean:.3f}")


def main():
    """Main analysis function."""
    results_dir = Path("data/results")
    
    # Find latest summary files
    baseline_files = list(results_dir.glob("baseline_*.json"))
    full_files = list(results_dir.glob("full_experiment_*.json"))
    
    if baseline_files:
        latest_baseline = max(baseline_files, key=lambda p: p.stat().st_mtime)
        analyze_baseline(str(latest_baseline))
    
    if full_files:
        latest_full = max(full_files, key=lambda p: p.stat().st_mtime)
        analyze_full_experiment(str(latest_full))
        analyze_interactions(str(latest_full))
    
    if baseline_files and full_files:
        compare_baseline_vs_full(str(latest_baseline), str(latest_full))
    
    print_section("ANALYSIS COMPLETE")


if __name__ == "__main__":
    main()


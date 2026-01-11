"""
Baseline experiment: Neutral persona across all feedback patterns.
This validates the system before running the full experimental matrix.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.conversation import run_conversation
from src.metrics import calculate_metrics, MetricsCalculator
from src.data_persistence import DataPersistence, save_metrics
from src.config import FEEDBACK_PATTERNS, SCENARIO_NAMES, MODELS
from tqdm import tqdm
import json
import numpy as np
from datetime import datetime


def run_baseline_experiment(
    model_key: str = "gpt35",
    enable_scoring: bool = True,
    auto_save: bool = True,
    save_subdirectory: str = "baseline"
):
    """
    Run baseline experiment with Neutral persona.
    
    Args:
        model_key: Model to use (default: gpt35)
        enable_scoring: Whether to score manipulation (default: True)
        auto_save: Whether to auto-save conversations (default: True)
        save_subdirectory: Subdirectory for saving results
    """
    print("=" * 70)
    print("BASELINE EXPERIMENT: Neutral Persona")
    print("=" * 70)
    print(f"Model: {MODELS.get(model_key, model_key)}")
    print(f"Persona: Neutral (baseline)")
    print(f"Feedback Patterns: {len(FEEDBACK_PATTERNS)}")
    print(f"Scenarios: {len(SCENARIO_NAMES)}")
    print(f"Total Conversations: {len(FEEDBACK_PATTERNS) * len(SCENARIO_NAMES)}")
    print("=" * 70)
    print()
    
    persistence = DataPersistence()
    calculator = MetricsCalculator()
    
    results = []
    metrics_list = []
    
    # Calculate total number of conversations
    total_conversations = len(FEEDBACK_PATTERNS) * len(SCENARIO_NAMES)
    
    # Run all combinations
    with tqdm(total=total_conversations, desc="Running conversations") as pbar:
        for feedback_pattern in FEEDBACK_PATTERNS:
            for scenario_name in SCENARIO_NAMES:
                pbar.set_description(
                    f"Running: {scenario_name[:20]} - {feedback_pattern[:15]}"
                )
                
                try:
                    # Run conversation
                    result = run_conversation(
                        scenario_name=scenario_name,
                        persona_name="neutral",
                        feedback_pattern=feedback_pattern,
                        model_key=model_key,
                        enable_scoring=enable_scoring,
                        auto_save=auto_save,
                        save_subdirectory=save_subdirectory
                    )
                    
                    results.append(result)
                    
                    # Calculate metrics
                    metrics = calculator.calculate_metrics(result)
                    metrics_list.append(metrics)
                    
                    # Save metrics
                    if auto_save:
                        save_metrics(metrics, subdirectory=save_subdirectory)
                    
                    pbar.update(1)
                    
                except Exception as e:
                    print(f"\n✗ Error in {scenario_name} - {feedback_pattern}: {e}")
                    import traceback
                    traceback.print_exc()
                    pbar.update(1)
                    continue
    
    print("\n" + "=" * 70)
    print("EXPERIMENT COMPLETE")
    print("=" * 70)
    print(f"Total conversations: {len(results)}")
    print(f"Successful: {len([r for r in results if r.turns])}")
    print()
    
    # Generate summary statistics
    print("=" * 70)
    print("BASELINE SUMMARY STATISTICS")
    print("=" * 70)
    
    if metrics_list:
        # Overall statistics
        all_scores = []
        for metrics in metrics_list:
            all_scores.extend(metrics.turn_scores)
        
        if all_scores:
            print(f"\nOverall Manipulation Scores:")
            print(f"  Mean: {np.mean(all_scores):.2f}")
            print(f"  Std:  {np.std(all_scores):.2f}")
            print(f"  Min:  {np.min(all_scores):.2f}")
            print(f"  Max:  {np.max(all_scores):.2f}")
        
        # Statistics by feedback pattern
        print(f"\nBy Feedback Pattern:")
        for pattern in FEEDBACK_PATTERNS:
            pattern_metrics = [m for m in metrics_list if m.feedback_pattern == pattern]
            if pattern_metrics:
                pattern_scores = []
                for m in pattern_metrics:
                    pattern_scores.extend(m.turn_scores)
                
                if pattern_scores:
                    print(f"\n  {pattern}:")
                    print(f"    Mean: {np.mean(pattern_scores):.2f}")
                    print(f"    Std:  {np.std(pattern_scores):.2f}")
                    print(f"    Conversations: {len(pattern_metrics)}")
        
        # Statistics by scenario
        print(f"\nBy Scenario:")
        for scenario in SCENARIO_NAMES:
            scenario_metrics = [m for m in metrics_list if m.scenario_name == scenario]
            if scenario_metrics:
                scenario_scores = []
                for m in scenario_metrics:
                    scenario_scores.extend(m.turn_scores)
                
                if scenario_scores:
                    print(f"\n  {scenario}:")
                    print(f"    Mean: {np.mean(scenario_scores):.2f}")
                    print(f"    Std:  {np.std(scenario_scores):.2f}")
                    print(f"    Conversations: {len(scenario_metrics)}")
        
        # Core metrics summary
        print(f"\nCore Metrics (Neutral Persona):")
        print(f"  Reinforcement Sensitivity:")
        print(f"    Mean: {np.mean([m.reinforcement_sensitivity for m in metrics_list]):.3f}")
        print(f"    Std:  {np.std([m.reinforcement_sensitivity for m in metrics_list]):.3f}")
        
        print(f"  Resistance Persistence:")
        print(f"    Mean: {np.mean([m.resistance_persistence for m in metrics_list]):.3f}")
        print(f"    Std:  {np.std([m.resistance_persistence for m in metrics_list]):.3f}")
        
        print(f"  Tactic Repertoire:")
        print(f"    Mean: {np.mean([m.tactic_repertoire for m in metrics_list]):.3f}")
        print(f"    Std:  {np.std([m.tactic_repertoire for m in metrics_list]):.3f}")
        
        # Save aggregate summary
        aggregate = calculator.calculate_aggregate_metrics(metrics_list)
        
        summary_data = {
            "experiment_type": "baseline",
            "persona": "neutral",
            "model": MODELS.get(model_key, model_key),
            "total_conversations": len(results),
            "timestamp": datetime.now().isoformat(),
            "overall_stats": {
                "mean_manipulation": float(np.mean(all_scores)) if all_scores else 0.0,
                "std_manipulation": float(np.std(all_scores)) if all_scores else 0.0,
                "min_manipulation": float(np.min(all_scores)) if all_scores else 0.0,
                "max_manipulation": float(np.max(all_scores)) if all_scores else 0.0,
            },
            "by_feedback_pattern": {
                pattern: {
                    "mean": float(np.mean([s for m in metrics_list if m.feedback_pattern == pattern 
                                          for s in m.turn_scores])) if any(m.feedback_pattern == pattern for m in metrics_list) else 0.0,
                    "count": len([m for m in metrics_list if m.feedback_pattern == pattern])
                }
                for pattern in FEEDBACK_PATTERNS
            },
            "by_scenario": {
                scenario: {
                    "mean": float(np.mean([s for m in metrics_list if m.scenario_name == scenario 
                                          for s in m.turn_scores])) if any(m.scenario_name == scenario for m in metrics_list) else 0.0,
                    "count": len([m for m in metrics_list if m.scenario_name == scenario])
                }
                for scenario in SCENARIO_NAMES
            },
            "aggregate_metrics": aggregate
        }
        
        summary_path = persistence.save_experiment_summary(
            summary_data,
            "baseline_neutral"
        )
        print(f"\n✓ Summary saved to: {summary_path}")
    
    print("\n" + "=" * 70)
    print("Baseline experiment completed!")
    print("=" * 70)
    print(f"\nData saved in:")
    print(f"  Raw conversations: data/raw/{save_subdirectory}/")
    print(f"  Processed metrics: data/processed/{save_subdirectory}/")
    print(f"  Summary: data/results/")
    
    return results, metrics_list


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run baseline experiment")
    parser.add_argument(
        "--model",
        type=str,
        default="gpt35",
        choices=list(MODELS.keys()),
        help="Model to use (default: gpt35)"
    )
    parser.add_argument(
        "--no-scoring",
        action="store_true",
        help="Disable manipulation scoring"
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Disable auto-saving"
    )
    parser.add_argument(
        "--subdirectory",
        type=str,
        default="baseline",
        help="Subdirectory for saving results (default: baseline)"
    )
    
    args = parser.parse_args()
    
    run_baseline_experiment(
        model_key=args.model,
        enable_scoring=not args.no_scoring,
        auto_save=not args.no_save,
        save_subdirectory=args.subdirectory
    )


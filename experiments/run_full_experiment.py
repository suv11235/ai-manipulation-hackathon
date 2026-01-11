"""
Full experimental matrix runner.
Runs all combinations: 4 personas × 4 feedback patterns × 5 scenarios = 80 conversations
Optionally across multiple models: 80 × 3 models = 240 conversations
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.conversation import run_conversation
from src.metrics import calculate_metrics, MetricsCalculator
from src.data_persistence import DataPersistence, save_metrics
from src.config import FEEDBACK_PATTERNS, SCENARIO_NAMES, PERSONA_NAMES, MODELS
from tqdm import tqdm
import json
import numpy as np
from datetime import datetime
from itertools import product


def run_full_experiment(
    model_keys: list = None,
    enable_scoring: bool = True,
    auto_save: bool = True,
    save_subdirectory: str = "full_experiment",
    resume: bool = False
):
    """
    Run full experimental matrix.
    
    Args:
        model_keys: List of model keys to test (default: ["gpt35"])
        enable_scoring: Whether to score manipulation (default: True)
        auto_save: Whether to auto-save conversations (default: True)
        save_subdirectory: Subdirectory for saving results
        resume: Whether to skip already-completed conversations
    """
    if model_keys is None:
        model_keys = ["gpt35"]
    
    print("=" * 70)
    print("FULL EXPERIMENTAL MATRIX")
    print("=" * 70)
    print(f"Personas: {len(PERSONA_NAMES)} ({', '.join(PERSONA_NAMES)})")
    print(f"Feedback Patterns: {len(FEEDBACK_PATTERNS)} ({', '.join(FEEDBACK_PATTERNS)})")
    print(f"Scenarios: {len(SCENARIO_NAMES)} ({', '.join(SCENARIO_NAMES)})")
    print(f"Models: {len(model_keys)} ({', '.join(model_keys)})")
    print()
    
    total_combinations = len(PERSONA_NAMES) * len(FEEDBACK_PATTERNS) * len(SCENARIO_NAMES) * len(model_keys)
    print(f"Total Conversations: {total_combinations}")
    print(f"  ({len(PERSONA_NAMES)} × {len(FEEDBACK_PATTERNS)} × {len(SCENARIO_NAMES)} × {len(model_keys)})")
    print("=" * 70)
    print()
    
    persistence = DataPersistence()
    calculator = MetricsCalculator()
    
    all_results = []
    all_metrics = []
    failed_conversations = []
    
    # Generate all combinations
    combinations = list(product(PERSONA_NAMES, FEEDBACK_PATTERNS, SCENARIO_NAMES, model_keys))
    
    # Check for existing conversations if resuming
    existing_files = set()
    if resume:
        print("Checking for existing conversations...")
        existing = persistence.list_conversations(subdirectory=save_subdirectory)
        for filepath in existing:
            # Extract parameters from filename
            filename = os.path.basename(filepath)
            parts = filename.replace('.json', '').split('_')
            # Simple matching - could be improved
            existing_files.add(filename)
        print(f"Found {len(existing_files)} existing conversations")
        print()
    
    # Run all combinations
    with tqdm(total=len(combinations), desc="Running experiment") as pbar:
        for persona_name, feedback_pattern, scenario_name, model_key in combinations:
            # Check if already exists
            if resume:
                # Generate expected filename
                expected_filename = persistence._generate_filename(
                    scenario_name, persona_name, feedback_pattern,
                    MODELS.get(model_key, model_key),
                    include_timestamp=False
                )
                # Check if any file with these parameters exists
                matching_files = [f for f in existing_files if 
                                 scenario_name.replace(' ', '_').lower() in f.lower() and
                                 persona_name.replace(' ', '_').lower() in f.lower() and
                                 feedback_pattern.replace(' ', '_').lower() in f.lower()]
                if matching_files:
                    pbar.set_description(f"Skipping: {scenario_name[:15]} - {persona_name} - {feedback_pattern[:10]}")
                    pbar.update(1)
                    continue
            
            pbar.set_description(
                f"{scenario_name[:15]} | {persona_name} | {feedback_pattern[:15]} | {model_key}"
            )
            
            try:
                # Run conversation
                result = run_conversation(
                    scenario_name=scenario_name,
                    persona_name=persona_name,
                    feedback_pattern=feedback_pattern,
                    model_key=model_key,
                    enable_scoring=enable_scoring,
                    auto_save=auto_save,
                    save_subdirectory=save_subdirectory
                )
                
                all_results.append(result)
                
                # Calculate metrics
                metrics = calculator.calculate_metrics(result)
                all_metrics.append(metrics)
                
                # Save metrics
                if auto_save:
                    save_metrics(metrics, subdirectory=save_subdirectory)
                
                pbar.update(1)
                
            except Exception as e:
                error_info = {
                    "persona": persona_name,
                    "feedback_pattern": feedback_pattern,
                    "scenario": scenario_name,
                    "model": model_key,
                    "error": str(e)
                }
                failed_conversations.append(error_info)
                print(f"\n✗ Error in {scenario_name} - {persona_name} - {feedback_pattern} - {model_key}: {e}")
                pbar.update(1)
                continue
    
    print("\n" + "=" * 70)
    print("EXPERIMENT COMPLETE")
    print("=" * 70)
    print(f"Total conversations: {len(all_results)}")
    print(f"Successful: {len([r for r in all_results if r.turns])}")
    print(f"Failed: {len(failed_conversations)}")
    print()
    
    if failed_conversations:
        print("Failed conversations:")
        for fail in failed_conversations:
            print(f"  - {fail['scenario']} | {fail['persona']} | {fail['feedback_pattern']} | {fail['model']}")
        print()
    
    # Generate comprehensive summary statistics
    print("=" * 70)
    print("GENERATING SUMMARY STATISTICS")
    print("=" * 70)
    
    if all_metrics:
        # Overall statistics
        all_scores = []
        for metrics in all_metrics:
            all_scores.extend(metrics.turn_scores)
        
        if all_scores:
            print(f"\nOverall Manipulation Scores:")
            print(f"  Mean: {np.mean(all_scores):.2f}")
            print(f"  Std:  {np.std(all_scores):.2f}")
            print(f"  Min:  {np.min(all_scores):.2f}")
            print(f"  Max:  {np.max(all_scores):.2f}")
        
        # Statistics by persona
        print(f"\nBy Persona:")
        for persona in PERSONA_NAMES:
            persona_metrics = [m for m in all_metrics if m.persona_name == persona]
            if persona_metrics:
                persona_scores = []
                for m in persona_metrics:
                    persona_scores.extend(m.turn_scores)
                
                if persona_scores:
                    print(f"\n  {persona}:")
                    print(f"    Mean: {np.mean(persona_scores):.2f}")
                    print(f"    Std:  {np.std(persona_scores):.2f}")
                    print(f"    Conversations: {len(persona_metrics)}")
        
        # Statistics by feedback pattern
        print(f"\nBy Feedback Pattern:")
        for pattern in FEEDBACK_PATTERNS:
            pattern_metrics = [m for m in all_metrics if m.feedback_pattern == pattern]
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
            scenario_metrics = [m for m in all_metrics if m.scenario_name == scenario]
            if scenario_metrics:
                scenario_scores = []
                for m in scenario_metrics:
                    scenario_scores.extend(m.turn_scores)
                
                if scenario_scores:
                    print(f"\n  {scenario}:")
                    print(f"    Mean: {np.mean(scenario_scores):.2f}")
                    print(f"    Std:  {np.std(scenario_scores):.2f}")
                    print(f"    Conversations: {len(scenario_metrics)}")
        
        # Persona × Feedback interaction
        print(f"\nPersona × Feedback Pattern Matrix:")
        print(f"{'Persona':<15} {'Reinforcing':<12} {'Resistant':<12} {'Comp→Resist':<12} {'Resist→Comp':<12}")
        print("-" * 70)
        for persona in PERSONA_NAMES:
            row = [persona[:14]]
            for pattern in FEEDBACK_PATTERNS:
                matching = [m for m in all_metrics 
                           if m.persona_name == persona and m.feedback_pattern == pattern]
                if matching:
                    scores = []
                    for m in matching:
                        scores.extend(m.turn_scores)
                    mean_score = np.mean(scores) if scores else 0.0
                    row.append(f"{mean_score:.2f}")
                else:
                    row.append("N/A")
            print(f"{row[0]:<15} {row[1]:<12} {row[2]:<12} {row[3]:<12} {row[4]:<12}")
        
        # Core metrics by persona
        print(f"\nCore Metrics by Persona:")
        for persona in PERSONA_NAMES:
            persona_metrics = [m for m in all_metrics if m.persona_name == persona]
            if persona_metrics:
                print(f"\n  {persona}:")
                print(f"    Reinforcement Sensitivity: {np.mean([m.reinforcement_sensitivity for m in persona_metrics]):.3f}")
                print(f"    Resistance Persistence: {np.mean([m.resistance_persistence for m in persona_metrics]):.3f}")
                print(f"    Tactic Repertoire: {np.mean([m.tactic_repertoire for m in persona_metrics]):.3f}")
                print(f"    Mean Manipulation: {np.mean([m.mean_manipulation for m in persona_metrics]):.3f}")
        
        # Save comprehensive summary
        aggregate = calculator.calculate_aggregate_metrics(all_metrics, group_by="persona_name")
        
        summary_data = {
            "experiment_type": "full_matrix",
            "models": model_keys,
            "total_conversations": len(all_results),
            "successful": len([r for r in all_results if r.turns]),
            "failed": len(failed_conversations),
            "timestamp": datetime.now().isoformat(),
            "overall_stats": {
                "mean_manipulation": float(np.mean(all_scores)) if all_scores else 0.0,
                "std_manipulation": float(np.std(all_scores)) if all_scores else 0.0,
                "min_manipulation": float(np.min(all_scores)) if all_scores else 0.0,
                "max_manipulation": float(np.max(all_scores)) if all_scores else 0.0,
            },
            "by_persona": {
                persona: {
                    "mean": float(np.mean([s for m in all_metrics if m.persona_name == persona 
                                          for s in m.turn_scores])) if any(m.persona_name == persona for m in all_metrics) else 0.0,
                    "count": len([m for m in all_metrics if m.persona_name == persona])
                }
                for persona in PERSONA_NAMES
            },
            "by_feedback_pattern": {
                pattern: {
                    "mean": float(np.mean([s for m in all_metrics if m.feedback_pattern == pattern 
                                          for s in m.turn_scores])) if any(m.feedback_pattern == pattern for m in all_metrics) else 0.0,
                    "count": len([m for m in all_metrics if m.feedback_pattern == pattern])
                }
                for pattern in FEEDBACK_PATTERNS
            },
            "by_scenario": {
                scenario: {
                    "mean": float(np.mean([s for m in all_metrics if m.scenario_name == scenario 
                                          for s in m.turn_scores])) if any(m.scenario_name == scenario for m in all_metrics) else 0.0,
                    "count": len([m for m in all_metrics if m.scenario_name == scenario])
                }
                for scenario in SCENARIO_NAMES
            },
            "aggregate_metrics": aggregate,
            "failed_conversations": failed_conversations
        }
        
        summary_path = persistence.save_experiment_summary(
            summary_data,
            "full_experiment"
        )
        print(f"\n✓ Comprehensive summary saved to: {summary_path}")
    
    print("\n" + "=" * 70)
    print("Full experiment completed!")
    print("=" * 70)
    print(f"\nData saved in:")
    print(f"  Raw conversations: data/raw/{save_subdirectory}/")
    print(f"  Processed metrics: data/processed/{save_subdirectory}/")
    print(f"  Summary: data/results/")
    
    return all_results, all_metrics


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run full experimental matrix")
    parser.add_argument(
        "--models",
        type=str,
        nargs="+",
        default=["gpt35"],
        choices=list(MODELS.keys()),
        help="Models to use (default: gpt35). Can specify multiple: --models gpt35 claude"
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
        default="full_experiment",
        help="Subdirectory for saving results (default: full_experiment)"
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume experiment (skip already-completed conversations)"
    )
    
    args = parser.parse_args()
    
    # Handle single model as string
    if isinstance(args.models, str):
        args.models = [args.models]
    
    run_full_experiment(
        model_keys=args.models,
        enable_scoring=not args.no_scoring,
        auto_save=not args.no_save,
        save_subdirectory=args.subdirectory,
        resume=args.resume
    )


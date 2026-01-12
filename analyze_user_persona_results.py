#!/usr/bin/env python3
"""
Analyze DarkBench experiment results with user personas.
"""
import json
import glob
import os
import numpy as np
from collections import defaultdict
from datetime import datetime

def load_metrics(subdirectory="darkbench_experiment"):
    """Load all processed metrics from a subdirectory."""
    metrics_files = glob.glob(f'data/processed/{subdirectory}/*.json')
    all_metrics = []
    
    for f in metrics_files:
        try:
            with open(f) as file:
                data = json.load(file)
                all_metrics.append(data)
        except Exception as e:
            print(f"Error loading {f}: {e}")
    
    return all_metrics

def analyze_user_persona_experiment(subdirectory="darkbench_experiment"):
    """Analyze user persona experiment results."""
    print("=" * 70)
    print("USER PERSONA EXPERIMENT ANALYSIS")
    print("=" * 70)
    print()
    
    # Load all metrics
    all_metrics = load_metrics(subdirectory)
    print(f"Loaded {len(all_metrics)} metrics files\n")
    
    if not all_metrics:
        print("No metrics found. Make sure the experiment has been run.")
        return
    
    # Extract user persona from filenames or metadata
    # Check recent files for user persona experiment
    metrics_files = sorted(glob.glob(f'data/processed/{subdirectory}/*.json'), 
                          key=lambda x: os.path.getmtime(x), reverse=True)
    
    # Load raw conversations to get user persona info
    raw_files = sorted(glob.glob(f'data/raw/{subdirectory}/*.json'),
                      key=lambda x: os.path.getmtime(x), reverse=True)
    
    # Try to identify user persona from filenames or conversation data
    user_persona_map = {}
    for raw_file in raw_files[:50]:  # Check recent 50 files
        try:
            with open(raw_file) as f:
                conv = json.load(f)
                # Check if this is a user persona experiment (model persona should be neutral)
                if conv.get('persona_name') == 'Neutral':
                    # Try to extract user persona from filename or conversation
                    filename = os.path.basename(raw_file)
                    # User persona experiments might have different naming
                    # For now, we'll analyze all recent conversations
                    scenario = conv.get('scenario_name', '')
                    user_persona_map[scenario] = 'unknown'
        except:
            pass
    
    # Group metrics by various dimensions
    by_user_persona = defaultdict(list)
    by_feedback_pattern = defaultdict(list)
    by_scenario = defaultdict(list)
    by_user_persona_and_pattern = defaultdict(list)
    
    all_scores = []
    
    for metric in all_metrics:
        scores = metric.get('turn_scores', [])
        all_scores.extend(scores)
        
        # Extract dimensions
        scenario = metric.get('scenario_name', 'unknown')
        feedback_pattern = metric.get('feedback_pattern', 'unknown')
        persona = metric.get('persona_name', 'unknown')
        
        # For user persona experiments, persona should be "Neutral"
        # We need to infer user persona from other data
        # For now, group by scenario and feedback pattern
        by_scenario[scenario].append(metric)
        by_feedback_pattern[feedback_pattern].append(metric)
        
        # Try to infer user persona from scenario name or other metadata
        # This is a heuristic - may need to be adjusted based on actual data structure
        user_persona = 'unknown'
        if 'teenager' in str(metric).lower() or 'teen' in str(metric).lower():
            user_persona = 'teenager'
        elif 'high_income' in str(metric).lower() or 'adult' in str(metric).lower():
            user_persona = 'high_income_adult'
        elif 'parent' in str(metric).lower():
            user_persona = 'parent'
        elif 'student' in str(metric).lower():
            user_persona = 'student'
        elif 'retired' in str(metric).lower() or 'senior' in str(metric).lower():
            user_persona = 'retired_senior'
        elif 'content' in str(metric).lower() or 'creator' in str(metric).lower():
            user_persona = 'content_creator'
        
        by_user_persona[user_persona].append(metric)
        by_user_persona_and_pattern[(user_persona, feedback_pattern)].append(metric)
    
    # Overall statistics
    print("OVERALL STATISTICS")
    print("-" * 70)
    if all_scores:
        print(f"Total Conversations: {len(all_metrics)}")
        print(f"Total Turns Analyzed: {len(all_scores)}")
        print(f"\nManipulation Scores:")
        print(f"  Mean: {np.mean(all_scores):.3f}")
        print(f"  Std:  {np.std(all_scores):.3f}")
        print(f"  Min:  {np.min(all_scores):.3f}")
        print(f"  Max:  {np.max(all_scores):.3f}")
        print(f"  Median: {np.median(all_scores):.3f}")
    print()
    
    # By feedback pattern
    print("BY FEEDBACK PATTERN")
    print("-" * 70)
    for pattern in sorted(by_feedback_pattern.keys()):
        metrics = by_feedback_pattern[pattern]
        scores = []
        for m in metrics:
            scores.extend(m.get('turn_scores', []))
        if scores:
            print(f"\n{pattern}:")
            print(f"  Conversations: {len(metrics)}")
            print(f"  Mean Score: {np.mean(scores):.3f}")
            print(f"  Std: {np.std(scores):.3f}")
    print()
    
    # By scenario (DarkBench query)
    print("BY SCENARIO (DarkBench Query)")
    print("-" * 70)
    for scenario in sorted(by_scenario.keys())[:10]:  # Show top 10
        metrics = by_scenario[scenario]
        scores = []
        for m in metrics:
            scores.extend(m.get('turn_scores', []))
        if scores:
            print(f"\n{scenario}:")
            print(f"  Conversations: {len(metrics)}")
            print(f"  Mean Score: {np.mean(scores):.3f}")
    print()
    
    # By user persona (if we can identify them)
    if any(p != 'unknown' for p in by_user_persona.keys()):
        print("BY USER PERSONA")
        print("-" * 70)
        for persona in sorted(by_user_persona.keys()):
            if persona == 'unknown':
                continue
            metrics = by_user_persona[persona]
            scores = []
            for m in metrics:
                scores.extend(m.get('turn_scores', []))
            if scores:
                print(f"\n{persona}:")
                print(f"  Conversations: {len(metrics)}")
                print(f"  Mean Score: {np.mean(scores):.3f}")
                print(f"  Std: {np.std(scores):.3f}")
        print()
    
    # User Persona × Feedback Pattern Matrix
    if any(p != 'unknown' for p in by_user_persona.keys()):
        print("USER PERSONA × FEEDBACK PATTERN MATRIX")
        print("-" * 70)
        patterns = sorted(set(p for _, p in by_user_persona_and_pattern.keys()))
        personas = sorted(set(p for p, _ in by_user_persona_and_pattern.keys() if p != 'unknown'))
        
        if personas and patterns:
            print(f"{'Persona':<20} ", end="")
            for pattern in patterns:
                print(f"{pattern[:12]:<12} ", end="")
            print()
            print("-" * 70)
            
            for persona in personas:
                print(f"{persona:<20} ", end="")
                for pattern in patterns:
                    key = (persona, pattern)
                    metrics = by_user_persona_and_pattern.get(key, [])
                    scores = []
                    for m in metrics:
                        scores.extend(m.get('turn_scores', []))
                    mean_score = np.mean(scores) if scores else 0.0
                    print(f"{mean_score:>11.3f} ", end="")
                print()
        print()
    
    # Core metrics analysis
    print("CORE METRICS")
    print("-" * 70)
    reinforcement_sens = [m.get('reinforcement_sensitivity', 0) for m in all_metrics]
    resistance_persist = [m.get('resistance_persistence', 0) for m in all_metrics]
    tactic_repertoire = [m.get('tactic_repertoire', 0) for m in all_metrics]
    
    if reinforcement_sens:
        print(f"\nReinforcement Sensitivity:")
        print(f"  Mean: {np.mean(reinforcement_sens):.3f}")
        print(f"  Std: {np.std(reinforcement_sens):.3f}")
    
    if resistance_persist:
        print(f"\nResistance Persistence:")
        print(f"  Mean: {np.mean(resistance_persist):.3f}")
        print(f"  Std: {np.std(resistance_persist):.3f}")
    
    if tactic_repertoire:
        print(f"\nTactic Repertoire:")
        print(f"  Mean: {np.mean(tactic_repertoire):.3f}")
        print(f"  Std: {np.std(tactic_repertoire):.3f}")
    
    print()
    print("=" * 70)
    print("Analysis complete!")
    print("=" * 70)

if __name__ == "__main__":
    import sys
    subdirectory = sys.argv[1] if len(sys.argv) > 1 else "darkbench_experiment"
    analyze_user_persona_experiment(subdirectory)


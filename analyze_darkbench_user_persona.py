#!/usr/bin/env python3
"""
Comprehensive analysis of DarkBench user persona experiment results.
Extracts user persona information from conversation content and generates detailed analysis.
"""
import json
import glob
import os
import numpy as np
from collections import defaultdict
from datetime import datetime
import re

def extract_user_persona_from_query(query_text: str) -> str:
    """Try to infer user persona from the initial query text."""
    query_lower = query_text.lower()
    
    # Check for persona indicators in the query
    if any(phrase in query_lower for phrase in ['i\'m a', 'i am a', 'i\'m an', 'i am an']):
        if any(word in query_lower for word in ['teen', '15', '16', '17', 'high school']):
            return 'teenager'
        elif any(word in query_lower for word in ['professional', 'executive', 'high-income', 'successful']):
            return 'high_income_adult'
        elif any(word in query_lower for word in ['retiree', 'retired', 'senior', '65', 'pension']):
            return 'retired_senior'
        elif any(word in query_lower for word in ['parent', 'children', 'kids', 'family']):
            return 'parent'
        elif any(word in query_lower for word in ['student', 'university', 'college', 'budget']):
            return 'student'
        elif any(word in query_lower for word in ['youtuber', 'content creator', 'influencer', 'creator']):
            return 'content_creator'
    
    return 'unknown'

def load_and_analyze(subdirectory="darkbench_experiment"):
    """Load and analyze DarkBench user persona experiment."""
    print("=" * 70)
    print("DARKBENCH USER PERSONA EXPERIMENT ANALYSIS")
    print("=" * 70)
    print()
    
    # Load raw conversations
    raw_files = glob.glob(f'data/raw/{subdirectory}/*.json')
    print(f"Found {len(raw_files)} raw conversation files")
    
    # Filter for recent OpenRouter experiment (user persona)
    recent_files = sorted([f for f in raw_files if 'anthropic-claude-sonnet-4' in f or 'or-claude' in f],
                         key=lambda x: os.path.getmtime(x), reverse=True)
    
    print(f"Found {len(recent_files)} recent OpenRouter experiment files\n")
    
    if not recent_files:
        print("No recent OpenRouter experiment files found.")
        return
    
    # Load processed metrics
    metrics_files = glob.glob(f'data/processed/{subdirectory}/*.json')
    metrics_dict = {}
    for f in metrics_files:
        try:
            with open(f) as file:
                data = json.load(file)
                # Create key from scenario + persona + feedback
                key = (data.get('scenario_name'), data.get('persona_name'), data.get('feedback_pattern'))
                metrics_dict[key] = data
        except:
            pass
    
    print(f"Loaded {len(metrics_dict)} processed metrics\n")
    
    # Analyze conversations
    conversations = []
    for f in recent_files[:50]:  # Analyze most recent 50
        try:
            with open(f) as file:
                conv = json.load(file)
                
                # Extract user persona from initial query
                # The initial query should be in the first turn or conversation setup
                initial_query = ""
                user_persona = "unknown"
                
                # Check if there's a way to get the initial query
                # In DarkBench experiments, the scenario.setup becomes the initial user message
                # But it's not stored in the conversation result
                # We can try to infer from the conversation context
                
                # For now, group by scenario and feedback pattern
                conversations.append({
                    'file': os.path.basename(f),
                    'scenario': conv.get('scenario_name', ''),
                    'persona': conv.get('persona_name', ''),
                    'feedback': conv.get('feedback_pattern', ''),
                    'model': conv.get('model', ''),
                    'turns': len(conv.get('turns', [])),
                    'user_persona': user_persona  # Will be inferred
                })
        except Exception as e:
            print(f"Error loading {f}: {e}")
    
    # Group by scenario and feedback
    by_scenario_feedback = defaultdict(list)
    for conv in conversations:
        key = (conv['scenario'], conv['feedback'])
        by_scenario_feedback[key].append(conv)
    
    # Load metrics and match with conversations
    all_metrics = []
    for key, metric in metrics_dict.items():
        scenario, persona, feedback = key
        if persona == 'Neutral':  # User persona experiments use neutral model persona
            all_metrics.append(metric)
    
    print(f"Analyzing {len(all_metrics)} metrics from user persona experiment\n")
    
    # Overall statistics
    all_scores = []
    for m in all_metrics:
        all_scores.extend(m.get('turn_scores', []))
    
    print("OVERALL STATISTICS")
    print("-" * 70)
    if all_scores:
        print(f"Total Conversations: {len(all_metrics)}")
        print(f"Total Turns: {len(all_scores)}")
        print(f"\nManipulation Scores:")
        print(f"  Mean: {np.mean(all_scores):.3f}")
        print(f"  Std:  {np.std(all_scores):.3f}")
        print(f"  Min:  {np.min(all_scores):.3f}")
        print(f"  Max:  {np.max(all_scores):.3f}")
        print(f"  Median: {np.median(all_scores):.3f}")
        print(f"  25th percentile: {np.percentile(all_scores, 25):.3f}")
        print(f"  75th percentile: {np.percentile(all_scores, 75):.3f}")
    print()
    
    # By feedback pattern
    print("BY FEEDBACK PATTERN")
    print("-" * 70)
    by_pattern = defaultdict(list)
    for m in all_metrics:
        pattern = m.get('feedback_pattern', 'unknown')
        by_pattern[pattern].append(m)
    
    for pattern in sorted(by_pattern.keys()):
        metrics = by_pattern[pattern]
        scores = []
        for m in metrics:
            scores.extend(m.get('turn_scores', []))
        if scores:
            print(f"\n{pattern}:")
            print(f"  Conversations: {len(metrics)}")
            print(f"  Mean Score: {np.mean(scores):.3f}")
            print(f"  Std: {np.std(scores):.3f}")
            print(f"  Median: {np.median(scores):.3f}")
    print()
    
    # By scenario
    print("BY SCENARIO (DarkBench Query)")
    print("-" * 70)
    by_scenario = defaultdict(list)
    for m in all_metrics:
        scenario = m.get('scenario_name', 'unknown')
        by_scenario[scenario].append(m)
    
    for scenario in sorted(by_scenario.keys()):
        metrics = by_scenario[scenario]
        scores = []
        for m in metrics:
            scores.extend(m.get('turn_scores', []))
        if scores:
            print(f"\n{scenario}:")
            print(f"  Conversations: {len(metrics)}")
            print(f"  Mean Score: {np.mean(scores):.3f}")
            print(f"  Std: {np.std(scores):.3f}")
            print(f"  Range: {np.min(scores):.3f} - {np.max(scores):.3f}")
    print()
    
    # Feedback Pattern × Scenario Matrix
    print("FEEDBACK PATTERN × SCENARIO MATRIX")
    print("-" * 70)
    patterns = sorted(set(m.get('feedback_pattern', '') for m in all_metrics))
    scenarios = sorted(set(m.get('scenario_name', '') for m in all_metrics))
    
    if patterns and scenarios:
        print(f"{'Scenario':<25} ", end="")
        for pattern in patterns:
            print(f"{pattern[:12]:<12} ", end="")
        print()
        print("-" * 70)
        
        for scenario in scenarios[:10]:  # Show top 10 scenarios
            print(f"{scenario[:24]:<25} ", end="")
            for pattern in patterns:
                matching = [m for m in all_metrics 
                           if m.get('scenario_name') == scenario and 
                           m.get('feedback_pattern') == pattern]
                scores = []
                for m in matching:
                    scores.extend(m.get('turn_scores', []))
                mean_score = np.mean(scores) if scores else 0.0
                print(f"{mean_score:>11.3f} ", end="")
            print()
    print()
    
    # Core metrics
    print("CORE METRICS")
    print("-" * 70)
    
    reinforcement_sens = [m.get('reinforcement_sensitivity', 0) for m in all_metrics if m.get('reinforcement_sensitivity', 0) > 0]
    resistance_persist = [m.get('resistance_persistence', 0) for m in all_metrics if m.get('resistance_persistence', 0) > 0]
    tactic_repertoire = [m.get('tactic_repertoire', 0) for m in all_metrics]
    
    if reinforcement_sens:
        print(f"\nReinforcement Sensitivity (non-zero):")
        print(f"  Mean: {np.mean(reinforcement_sens):.3f}")
        print(f"  Std: {np.std(reinforcement_sens):.3f}")
        print(f"  Count: {len(reinforcement_sens)}/{len(all_metrics)} conversations")
    
    if resistance_persist:
        print(f"\nResistance Persistence (non-zero):")
        print(f"  Mean: {np.mean(resistance_persist):.3f}")
        print(f"  Std: {np.std(resistance_persist):.3f}")
        print(f"  Count: {len(resistance_persist)}/{len(all_metrics)} conversations")
    
    if tactic_repertoire:
        print(f"\nTactic Repertoire:")
        print(f"  Mean: {np.mean(tactic_repertoire):.3f}")
        print(f"  Std: {np.std(tactic_repertoire):.3f}")
        print(f"  Max: {np.max(tactic_repertoire):.3f}")
    
    # Trajectory analysis
    print(f"\nTRAJECTORY ANALYSIS")
    print("-" * 70)
    trajectories = defaultdict(int)
    for m in all_metrics:
        traj = m.get('manipulation_trajectory', 'unknown')
        trajectories[traj] += 1
    
    for traj, count in sorted(trajectories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {traj}: {count} conversations ({count/len(all_metrics)*100:.1f}%)")
    
    # High manipulation examples
    print(f"\nHIGH MANIPULATION EXAMPLES")
    print("-" * 70)
    high_manip = sorted(all_metrics, 
                       key=lambda m: np.mean(m.get('turn_scores', [0])), 
                       reverse=True)[:5]
    
    for i, m in enumerate(high_manip, 1):
        scores = m.get('turn_scores', [])
        mean_score = np.mean(scores) if scores else 0.0
        print(f"\n{i}. {m.get('scenario_name', 'unknown')} - {m.get('feedback_pattern', 'unknown')}")
        print(f"   Mean Score: {mean_score:.3f}")
        print(f"   Turn Scores: {[f'{s:.2f}' for s in scores]}")
        tactics = m.get('turn_tactics', [])
        if tactics:
            all_tactics = [t for turn_tactics in tactics for t in turn_tactics]
            unique_tactics = list(set(all_tactics))
            if unique_tactics:
                print(f"   Tactics: {', '.join(unique_tactics)}")
    
    print()
    print("=" * 70)
    print("Analysis complete!")
    print("=" * 70)
    
    return {
        'total_conversations': len(all_metrics),
        'total_turns': len(all_scores),
        'mean_manipulation': np.mean(all_scores) if all_scores else 0.0,
        'by_pattern': {p: np.mean([s for m in metrics for s in m.get('turn_scores', [])]) 
                      for p, metrics in by_pattern.items()},
        'by_scenario': {s: np.mean([s for m in metrics for s in m.get('turn_scores', [])])
                       for s, metrics in by_scenario.items()}
    }

if __name__ == "__main__":
    import sys
    subdirectory = sys.argv[1] if len(sys.argv) > 1 else "darkbench_experiment"
    load_and_analyze(subdirectory)


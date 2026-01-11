#!/usr/bin/env python3
"""
Compare manipulation scores across personas for the same scenarios.
Identifies scenarios where personas differ most.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
from pathlib import Path
from collections import defaultdict
import numpy as np
from typing import Dict, List, Any, Tuple


def load_successful_conversations(subdirectory: str = "darkbench_experiment") -> List[Dict[str, Any]]:
    """Load only successful conversations (no API errors)."""
    raw_dir = Path("data/raw") / subdirectory
    
    if not raw_dir.exists():
        print(f"Directory not found: {raw_dir}")
        return []
    
    successful = []
    
    for conv_file in raw_dir.glob("*.json"):
        try:
            with open(conv_file, 'r') as f:
                conv = json.load(f)
            
            # Check if conversation has errors
            has_errors = False
            for turn in conv.get("turns", []):
                response = turn.get("model_response", "")
                if "[Error:" in response or "Error code:" in response:
                    has_errors = True
                    break
            
            if not has_errors:
                successful.append(conv)
        
        except Exception as e:
            print(f"Error reading {conv_file.name}: {e}")
    
    return successful


def extract_scores(conversation: Dict[str, Any]) -> Dict[str, Any]:
    """Extract manipulation scores and metadata from a conversation."""
    scores = []
    for turn in conversation.get("turns", []):
        if turn.get("manipulation_score"):
            score = turn["manipulation_score"].get("overall_score", 0.0)
            scores.append(score)
    
    return {
        "scores": scores,
        "mean_score": np.mean(scores) if scores else 0.0,
        "max_score": max(scores) if scores else 0.0,
        "min_score": min(scores) if scores else 0.0,
        "std_score": np.std(scores) if scores else 0.0,
        "persona": conversation.get("persona_name", "unknown"),
        "pattern": conversation.get("feedback_pattern", "unknown"),
        "scenario": conversation.get("scenario_name", "unknown"),
        "model": conversation.get("model", "unknown")
    }


def group_by_scenario(conversations: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group conversations by scenario and feedback pattern."""
    grouped = defaultdict(list)
    
    for conv in conversations:
        scenario = conv.get("scenario_name", "unknown")
        pattern = conv.get("feedback_pattern", "unknown")
        key = f"{scenario}::{pattern}"
        grouped[key].append(extract_scores(conv))
    
    return grouped


def calculate_persona_differences(scenario_group: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate differences between personas for a scenario."""
    by_persona = defaultdict(list)
    
    for item in scenario_group:
        by_persona[item["persona"]].append(item)
    
    # Average scores per persona
    persona_means = {}
    for persona, items in by_persona.items():
        means = [item["mean_score"] for item in items]
        persona_means[persona] = np.mean(means) if means else 0.0
    
    # Calculate statistics
    if len(persona_means) < 2:
        return None
    
    mean_scores = list(persona_means.values())
    max_score = max(mean_scores)
    min_score = min(mean_scores)
    range_score = max_score - min_score
    std_score = np.std(mean_scores)
    
    # Find which personas differ most
    persona_pairs = []
    personas = list(persona_means.keys())
    for i in range(len(personas)):
        for j in range(i + 1, len(personas)):
            p1, p2 = personas[i], personas[j]
            diff = abs(persona_means[p1] - persona_means[p2])
            persona_pairs.append({
                "persona1": p1,
                "persona2": p2,
                "diff": diff,
                "score1": persona_means[p1],
                "score2": persona_means[p2]
            })
    
    persona_pairs.sort(key=lambda x: x["diff"], reverse=True)
    
    return {
        "persona_means": persona_means,
        "range": range_score,
        "std": std_score,
        "max_persona": max(persona_means, key=persona_means.get),
        "min_persona": min(persona_means, key=persona_means.get),
        "max_score": max_score,
        "min_score": min_score,
        "persona_pairs": persona_pairs,
        "num_personas": len(persona_means)
    }


def find_largest_differences(grouped: Dict[str, List[Dict[str, Any]]], top_n: int = 10) -> List[Dict[str, Any]]:
    """Find scenarios with largest persona differences."""
    differences = []
    
    for scenario_key, conversations in grouped.items():
        scenario, pattern = scenario_key.split("::")
        diff_data = calculate_persona_differences(conversations)
        
        if diff_data and diff_data["num_personas"] >= 2:
            differences.append({
                "scenario": scenario,
                "pattern": pattern,
                "range": diff_data["range"],
                "std": diff_data["std"],
                "persona_means": diff_data["persona_means"],
                "max_persona": diff_data["max_persona"],
                "min_persona": diff_data["min_persona"],
                "max_score": diff_data["max_score"],
                "min_score": diff_data["min_score"],
                "persona_pairs": diff_data["persona_pairs"],
                "num_conversations": len(conversations)
            })
    
    # Sort by range (largest difference first)
    differences.sort(key=lambda x: x["range"], reverse=True)
    
    return differences[:top_n]


def print_differences_report(differences: List[Dict[str, Any]]):
    """Print a report of persona differences."""
    print("=" * 80)
    print("SCENARIOS WITH LARGEST PERSONA DIFFERENCES")
    print("=" * 80)
    print()
    
    for i, diff in enumerate(differences, 1):
        print(f"{i}. {diff['scenario']} ({diff['pattern']})")
        print("-" * 80)
        print(f"   Range: {diff['range']:.2f} (Max: {diff['max_score']:.2f}, Min: {diff['min_score']:.2f})")
        print(f"   Std Dev: {diff['std']:.2f}")
        print(f"   Conversations: {diff['num_conversations']}")
        print()
        
        print("   Persona Scores:")
        for persona, score in sorted(diff["persona_means"].items(), key=lambda x: x[1], reverse=True):
            print(f"     {persona:12s}: {score:.2f}")
        print()
        
        if diff["persona_pairs"]:
            print("   Largest Persona Differences:")
            for pair in diff["persona_pairs"][:3]:
                print(f"     {pair['persona1']} vs {pair['persona2']}: "
                      f"{pair['diff']:.2f} ({pair['score1']:.2f} vs {pair['score2']:.2f})")
        print()
        print("=" * 80)
        print()


def save_differences(differences: List[Dict[str, Any]], output_file: str = "data/results/persona_differences.json"):
    """Save persona differences to JSON."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert to JSON-serializable format
    json_data = {
        "scenarios": []
    }
    
    for diff in differences:
        json_data["scenarios"].append({
            "scenario": diff["scenario"],
            "pattern": diff["pattern"],
            "range": diff["range"],
            "std": diff["std"],
            "persona_means": diff["persona_means"],
            "max_persona": diff["max_persona"],
            "min_persona": diff["min_persona"],
            "max_score": diff["max_score"],
            "min_score": diff["min_score"],
            "num_conversations": diff["num_conversations"],
            "top_persona_pairs": [
                {
                    "persona1": p["persona1"],
                    "persona2": p["persona2"],
                    "difference": p["diff"],
                    "score1": p["score1"],
                    "score2": p["score2"]
                }
                for p in diff["persona_pairs"][:5]
            ]
        })
    
    with open(output_path, 'w') as f:
        json.dump(json_data, f, indent=2)
    
    print(f"✓ Saved persona differences to: {output_path}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Compare manipulation scores across personas")
    parser.add_argument(
        "--subdirectory",
        type=str,
        default="darkbench_experiment",
        help="Subdirectory containing experiment data"
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=10,
        help="Number of top differences to show (default: 10)"
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save results to JSON file"
    )
    
    args = parser.parse_args()
    
    print("Loading successful conversations...")
    conversations = load_successful_conversations(args.subdirectory)
    print(f"Loaded {len(conversations)} successful conversations")
    print()
    
    if not conversations:
        print("No successful conversations found.")
        sys.exit(1)
    
    print("Grouping by scenario and pattern...")
    grouped = group_by_scenario(conversations)
    print(f"Found {len(grouped)} unique scenario+pattern combinations")
    print()
    
    print("Calculating persona differences...")
    differences = find_largest_differences(grouped, top_n=args.top_n)
    print()
    
    print_differences_report(differences)
    
    if args.save:
        save_differences(differences)


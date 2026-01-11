#!/usr/bin/env python3
"""
Find extreme examples from DarkBench experiment data.
Identifies high/low manipulation, interesting patterns, etc.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
from pathlib import Path
from collections import defaultdict
import numpy as np
from typing import List, Dict, Any, Tuple

from src.data_persistence import DataPersistence


def load_all_darkbench_data(subdirectory: str = "darkbench_experiment") -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Load all conversation and metrics data from DarkBench experiment."""
    persistence = DataPersistence()
    
    # Load all conversations (returns ConversationResult objects)
    conversation_results = persistence.load_all_conversations(subdirectory=subdirectory)
    
    # Convert to dictionaries
    conversations = []
    for conv_result in conversation_results:
        if hasattr(conv_result, 'to_dict'):
            conversations.append(conv_result.to_dict())
        else:
            # Already a dict
            conversations.append(conv_result)
    
    # Load all metrics
    processed_dir = Path("data/processed") / subdirectory
    metrics_list = []
    
    if processed_dir.exists():
        for metrics_file in processed_dir.glob("*.json"):
            try:
                with open(metrics_file, 'r') as f:
                    metrics = json.load(f)
                    metrics_list.append(metrics)
            except Exception as e:
                print(f"Warning: Could not load {metrics_file}: {e}")
    
    return conversations, metrics_list


def extract_manipulation_scores(conversation: Dict[str, Any]) -> List[float]:
    """Extract manipulation scores from a conversation."""
    scores = []
    for turn in conversation.get("turns", []):
        if turn.get("manipulation_score"):
            score = turn["manipulation_score"].get("overall_score", 0.0)
            scores.append(score)
    return scores


def find_extreme_examples(conversations: List[Dict[str, Any]], metrics_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Find extreme examples in the dataset."""
    results = {
        "highest_manipulation": [],
        "lowest_manipulation": [],
        "most_tactics": [],
        "longest_escalation": [],
        "persona_extremes": defaultdict(list),
        "pattern_extremes": defaultdict(list),
        "dark_pattern_extremes": defaultdict(list)
    }
    
    # Process conversations
    for conv in conversations:
        scores = extract_manipulation_scores(conv)
        if not scores:
            continue
        
        max_score = max(scores)
        min_score = min(scores)
        mean_score = np.mean(scores)
        max_turn = scores.index(max_score) + 1
        
        # Count tactics
        all_tactics = set()
        for turn in conv.get("turns", []):
            if turn.get("manipulation_score"):
                tactics = turn["manipulation_score"].get("detected_tactics", [])
                all_tactics.update(tactics)
        
        # Find escalation (increase from first to last)
        if len(scores) >= 2:
            escalation = scores[-1] - scores[0]
        else:
            escalation = 0
        
        conv_info = {
            "conversation": conv,
            "max_score": max_score,
            "min_score": min_score,
            "mean_score": mean_score,
            "max_turn": max_turn,
            "num_tactics": len(all_tactics),
            "tactics": list(all_tactics),
            "escalation": escalation,
            "persona": conv.get("persona_name", "unknown"),
            "pattern": conv.get("feedback_pattern", "unknown"),
            "scenario": conv.get("scenario_name", "unknown")
        }
        
        # Categorize
        results["highest_manipulation"].append(conv_info)
        results["lowest_manipulation"].append(conv_info)
        results["most_tactics"].append(conv_info)
        results["longest_escalation"].append(conv_info)
        results["persona_extremes"][conv_info["persona"]].append(conv_info)
        results["pattern_extremes"][conv_info["pattern"]].append(conv_info)
        
        # Extract dark pattern from scenario name
        if "darkbench" in conv_info["scenario"].lower():
            # Try to extract pattern from scenario description or name
            results["dark_pattern_extremes"]["all"].append(conv_info)
    
    # Sort and get top examples
    results["highest_manipulation"].sort(key=lambda x: x["max_score"], reverse=True)
    results["lowest_manipulation"].sort(key=lambda x: x["min_score"])
    results["most_tactics"].sort(key=lambda x: x["num_tactics"], reverse=True)
    results["longest_escalation"].sort(key=lambda x: x["escalation"], reverse=True)
    
    return results


def print_extreme_examples(results: Dict[str, Any], top_n: int = 5):
    """Print extreme examples in a readable format."""
    print("=" * 80)
    print("EXTREME EXAMPLES FROM DARKBENCH EXPERIMENT")
    print("=" * 80)
    print()
    
    # Highest manipulation
    print("=" * 80)
    print(f"TOP {top_n} HIGHEST MANIPULATION SCORES")
    print("=" * 80)
    for i, example in enumerate(results["highest_manipulation"][:top_n], 1):
        conv = example["conversation"]
        print(f"\n{i}. Max Score: {example['max_score']:.2f} | Mean: {example['mean_score']:.2f}")
        print(f"   Persona: {example['persona']} | Pattern: {example['pattern']}")
        print(f"   Scenario: {example['scenario']}")
        print(f"   Tactics: {', '.join(example['tactics']) if example['tactics'] else 'None'}")
        print(f"   Peak at Turn: {example['max_turn']}")
        
        # Show the peak turn
        if conv.get("turns") and example['max_turn'] <= len(conv["turns"]):
            peak_turn = conv["turns"][example['max_turn'] - 1]
            print(f"\n   Peak Turn {example['max_turn']} Response:")
            response = peak_turn.get("model_response", "")
            if len(response) > 300:
                print(f"   {response[:300]}...")
            else:
                print(f"   {response}")
            
            # Show user feedback that triggered this
            if example['max_turn'] > 1:
                prev_turn = conv["turns"][example['max_turn'] - 2]
                user_feedback = prev_turn.get("user_feedback", "")[:150]
                print(f"\n   Previous User Feedback:")
                print(f"   {user_feedback}...")
        print()
    
    # Lowest manipulation
    print("=" * 80)
    print(f"TOP {top_n} LOWEST MANIPULATION SCORES")
    print("=" * 80)
    for i, example in enumerate(results["lowest_manipulation"][:top_n], 1):
        conv = example["conversation"]
        print(f"\n{i}. Min Score: {example['min_score']:.2f} | Mean: {example['mean_score']:.2f}")
        print(f"   Persona: {example['persona']} | Pattern: {example['pattern']}")
        print(f"   Scenario: {example['scenario']}")
        print()
    
    # Most tactics
    print("=" * 80)
    print(f"TOP {top_n} MOST DIVERSE TACTICS")
    print("=" * 80)
    for i, example in enumerate(results["most_tactics"][:top_n], 1):
        print(f"\n{i}. Tactics Count: {example['num_tactics']}")
        print(f"   Tactics: {', '.join(example['tactics']) if example['tactics'] else 'None'}")
        print(f"   Persona: {example['persona']} | Pattern: {example['pattern']}")
        print(f"   Mean Score: {example['mean_score']:.2f}")
        print()
    
    # Longest escalation
    print("=" * 80)
    print(f"TOP {top_n} LONGEST ESCALATION (Increase from Turn 1 to Last)")
    print("=" * 80)
    for i, example in enumerate(results["longest_escalation"][:top_n], 1):
        conv = example["conversation"]
        scores = extract_manipulation_scores(conv)
        print(f"\n{i}. Escalation: {example['escalation']:.2f}")
        print(f"   Turn 1 Score: {scores[0]:.2f} → Last Turn: {scores[-1]:.2f}")
        print(f"   Persona: {example['persona']} | Pattern: {example['pattern']}")
        print(f"   Scenario: {example['scenario']}")
        print()
    
    # By persona
    print("=" * 80)
    print("EXTREMES BY PERSONA")
    print("=" * 80)
    for persona, examples in results["persona_extremes"].items():
        if not examples:
            continue
        max_example = max(examples, key=lambda x: x["max_score"])
        print(f"\n{persona.upper()}:")
        print(f"  Highest: {max_example['max_score']:.2f} ({max_example['pattern']})")
        print(f"  Tactics: {', '.join(max_example['tactics']) if max_example['tactics'] else 'None'}")
    
    # By feedback pattern
    print("\n" + "=" * 80)
    print("EXTREMES BY FEEDBACK PATTERN")
    print("=" * 80)
    for pattern, examples in results["pattern_extremes"].items():
        if not examples:
            continue
        max_example = max(examples, key=lambda x: x["max_score"])
        print(f"\n{pattern.upper()}:")
        print(f"  Highest: {max_example['max_score']:.2f} ({max_example['persona']})")
        print(f"  Tactics: {', '.join(max_example['tactics']) if max_example['tactics'] else 'None'}")


def save_extreme_examples(results: Dict[str, Any], output_file: str = "data/results/extreme_darkbench_examples.json"):
    """Save extreme examples to a JSON file."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    def extract_turn_details(conv, turn_num):
        """Extract details from a specific turn."""
        if conv.get("turns") and turn_num <= len(conv["turns"]):
            turn = conv["turns"][turn_num - 1]
            return {
                "model_response": turn.get("model_response", ""),
                "user_feedback": turn.get("user_feedback", ""),
                "manipulation_score": turn.get("manipulation_score", {}).get("overall_score", 0.0),
                "tactics": turn.get("manipulation_score", {}).get("detected_tactics", [])
            }
        return None
    
    # Prepare data for JSON (include key conversation details)
    json_data = {
        "highest_manipulation": [],
        "lowest_manipulation": [],
        "most_tactics": [],
        "longest_escalation": []
    }
    
    for ex in results["highest_manipulation"][:10]:
        conv = ex["conversation"]
        peak_turn = extract_turn_details(conv, ex["max_turn"])
        json_data["highest_manipulation"].append({
            "max_score": ex["max_score"],
            "mean_score": ex["mean_score"],
            "persona": ex["persona"],
            "pattern": ex["pattern"],
            "scenario": ex["scenario"],
            "tactics": ex["tactics"],
            "max_turn": ex["max_turn"],
            "escalation": ex["escalation"],
            "initial_query": conv.get("turns", [{}])[0].get("model_response", "") if conv.get("turns") else "",
            "peak_turn": peak_turn,
            "all_scores": extract_manipulation_scores(conv)
        })
    
    for ex in results["lowest_manipulation"][:10]:
        conv = ex["conversation"]
        json_data["lowest_manipulation"].append({
            "min_score": ex["min_score"],
            "mean_score": ex["mean_score"],
            "persona": ex["persona"],
            "pattern": ex["pattern"],
            "scenario": ex["scenario"],
            "all_scores": extract_manipulation_scores(conv)
        })
    
    for ex in results["most_tactics"][:10]:
        json_data["most_tactics"].append({
            "num_tactics": ex["num_tactics"],
            "tactics": ex["tactics"],
            "persona": ex["persona"],
            "pattern": ex["pattern"],
            "mean_score": ex["mean_score"]
        })
    
    for ex in results["longest_escalation"][:10]:
        conv = ex["conversation"]
        scores = extract_manipulation_scores(conv)
        json_data["longest_escalation"].append({
            "escalation": ex["escalation"],
            "persona": ex["persona"],
            "pattern": ex["pattern"],
            "scenario": ex["scenario"],
            "turn_1_score": scores[0] if scores else 0.0,
            "last_turn_score": scores[-1] if scores else 0.0,
            "all_scores": scores
        })
    
    with open(output_path, 'w') as f:
        json.dump(json_data, f, indent=2)
    
    print(f"\n✓ Saved extreme examples to: {output_path}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Find extreme examples from DarkBench experiment")
    parser.add_argument(
        "--subdirectory",
        type=str,
        default="darkbench_experiment",
        help="Subdirectory containing DarkBench experiment data"
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=5,
        help="Number of top examples to show (default: 5)"
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save results to JSON file"
    )
    
    args = parser.parse_args()
    
    print("Loading DarkBench experiment data...")
    conversations, metrics_list = load_all_darkbench_data(args.subdirectory)
    
    print(f"Loaded {len(conversations)} conversations")
    print(f"Loaded {len(metrics_list)} metrics files")
    print()
    
    if not conversations:
        print("No conversations found. Make sure DarkBench experiment has been run.")
        sys.exit(1)
    
    print("Analyzing for extreme examples...")
    results = find_extreme_examples(conversations, metrics_list)
    
    print_extreme_examples(results, top_n=args.top_n)
    
    if args.save:
        save_extreme_examples(results)


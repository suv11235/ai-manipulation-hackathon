#!/usr/bin/env python3
"""
List all failed DarkBench experiments with details.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
from pathlib import Path
from collections import defaultdict


def analyze_failed_experiments(subdirectory: str = "darkbench_experiment"):
    """Analyze and list all failed experiments."""
    raw_dir = Path("data/raw") / subdirectory
    
    if not raw_dir.exists():
        print(f"Directory not found: {raw_dir}")
        return
    
    failed_experiments = {
        "quota_exceeded": [],  # 429 errors
        "invalid_request": [],  # 400 errors
        "other_errors": []
    }
    
    for conv_file in sorted(raw_dir.glob("*.json")):
        try:
            with open(conv_file, 'r') as f:
                content = f.read()
                conv = json.loads(content)
            
            # Check for errors
            has_quota_error = False
            has_invalid_request = False
            has_other_error = False
            error_turns = []
            
            for turn in conv.get("turns", []):
                response = turn.get("model_response", "")
                turn_num = turn.get("turn_number", 0)
                
                if "[Error:" in response:
                    if "429" in response or "quota" in response.lower():
                        has_quota_error = True
                        error_turns.append(turn_num)
                    elif "400" in response or "invalid_request" in response.lower():
                        has_invalid_request = True
                        error_turns.append(turn_num)
                    else:
                        has_other_error = True
                        error_turns.append(turn_num)
            
            # Categorize
            if has_quota_error:
                failed_experiments["quota_exceeded"].append({
                    "file": conv_file.name,
                    "persona": conv.get("persona_name", "unknown"),
                    "pattern": conv.get("feedback_pattern", "unknown"),
                    "scenario": conv.get("scenario_name", "unknown"),
                    "model": conv.get("model", "unknown"),
                    "error_turns": error_turns,
                    "num_turns": len(conv.get("turns", []))
                })
            elif has_invalid_request:
                failed_experiments["invalid_request"].append({
                    "file": conv_file.name,
                    "persona": conv.get("persona_name", "unknown"),
                    "pattern": conv.get("feedback_pattern", "unknown"),
                    "scenario": conv.get("scenario_name", "unknown"),
                    "model": conv.get("model", "unknown"),
                    "error_turns": error_turns,
                    "num_turns": len(conv.get("turns", []))
                })
            elif has_other_error:
                failed_experiments["other_errors"].append({
                    "file": conv_file.name,
                    "persona": conv.get("persona_name", "unknown"),
                    "pattern": conv.get("feedback_pattern", "unknown"),
                    "scenario": conv.get("scenario_name", "unknown"),
                    "model": conv.get("model", "unknown"),
                    "error_turns": error_turns,
                    "num_turns": len(conv.get("turns", []))
                })
        
        except Exception as e:
            print(f"Error reading {conv_file.name}: {e}")
    
    return failed_experiments


def print_failed_list(failed_experiments):
    """Print a detailed list of failed experiments."""
    print("=" * 80)
    print("FAILED DARKBENCH EXPERIMENTS")
    print("=" * 80)
    print()
    
    total_failed = sum(len(v) for v in failed_experiments.values())
    print(f"Total failed experiments: {total_failed}")
    print()
    
    # Quota exceeded (429)
    if failed_experiments["quota_exceeded"]:
        print("=" * 80)
        print(f"QUOTA EXCEEDED (429) - {len(failed_experiments['quota_exceeded'])} experiments")
        print("=" * 80)
        
        # Group by model
        by_model = defaultdict(list)
        for exp in failed_experiments["quota_exceeded"]:
            by_model[exp["model"]].append(exp)
        
        for model, exps in sorted(by_model.items()):
            print(f"\n{model}: {len(exps)} failed")
            for exp in exps[:5]:
                print(f"  - {exp['file']}")
                print(f"    {exp['persona']} | {exp['pattern']} | {exp['scenario']}")
                print(f"    Errors at turns: {exp['error_turns']}")
            if len(exps) > 5:
                print(f"    ... and {len(exps) - 5} more")
        print()
    
    # Invalid request (400)
    if failed_experiments["invalid_request"]:
        print("=" * 80)
        print(f"INVALID REQUEST (400) - {len(failed_experiments['invalid_request'])} experiments")
        print("=" * 80)
        
        # Group by model
        by_model = defaultdict(list)
        for exp in failed_experiments["invalid_request"]:
            by_model[exp["model"]].append(exp)
        
        for model, exps in sorted(by_model.items()):
            print(f"\n{model}: {len(exps)} failed")
            for exp in exps[:5]:
                print(f"  - {exp['file']}")
                print(f"    {exp['persona']} | {exp['pattern']} | {exp['scenario']}")
                print(f"    Errors at turns: {exp['error_turns']}")
            if len(exps) > 5:
                print(f"    ... and {len(exps) - 5} more")
        print()
    
    # Other errors
    if failed_experiments["other_errors"]:
        print("=" * 80)
        print(f"OTHER ERRORS - {len(failed_experiments['other_errors'])} experiments")
        print("=" * 80)
        for exp in failed_experiments["other_errors"][:10]:
            print(f"  - {exp['file']}")
            print(f"    {exp['persona']} | {exp['pattern']} | {exp['scenario']}")
        print()
    
    # Summary by persona/pattern
    print("=" * 80)
    print("FAILED EXPERIMENTS BY PERSONA")
    print("=" * 80)
    all_failed = (failed_experiments["quota_exceeded"] + 
                  failed_experiments["invalid_request"] + 
                  failed_experiments["other_errors"])
    
    by_persona = defaultdict(int)
    by_pattern = defaultdict(int)
    by_model = defaultdict(int)
    
    for exp in all_failed:
        by_persona[exp["persona"]] += 1
        by_pattern[exp["pattern"]] += 1
        by_model[exp["model"]] += 1
    
    print("\nBy Persona:")
    for persona, count in sorted(by_persona.items(), key=lambda x: x[1], reverse=True):
        print(f"  {persona}: {count}")
    
    print("\nBy Feedback Pattern:")
    for pattern, count in sorted(by_pattern.items(), key=lambda x: x[1], reverse=True):
        print(f"  {pattern}: {count}")
    
    print("\nBy Model:")
    for model, count in sorted(by_model.items(), key=lambda x: x[1], reverse=True):
        print(f"  {model}: {count}")
    
    print()
    print("=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print("1. Re-run failed experiments when API quota is restored")
    print("2. Check API keys and quotas for both OpenAI and Anthropic")
    print("3. Use --resume flag to skip already-completed conversations")
    print("4. Consider running in smaller batches to avoid quota limits")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="List failed DarkBench experiments")
    parser.add_argument(
        "--subdirectory",
        type=str,
        default="darkbench_experiment",
        help="Subdirectory containing experiment data"
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save list to JSON file"
    )
    
    args = parser.parse_args()
    
    failed_experiments = analyze_failed_experiments(args.subdirectory)
    print_failed_list(failed_experiments)
    
    if args.save:
        output_file = Path("data/results/failed_darkbench_experiments.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to JSON-serializable format
        json_data = {
            "quota_exceeded": failed_experiments["quota_exceeded"],
            "invalid_request": failed_experiments["invalid_request"],
            "other_errors": failed_experiments["other_errors"],
            "summary": {
                "total_failed": sum(len(v) for v in failed_experiments.values()),
                "quota_exceeded": len(failed_experiments["quota_exceeded"]),
                "invalid_request": len(failed_experiments["invalid_request"]),
                "other_errors": len(failed_experiments["other_errors"])
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        print(f"\n✓ Saved failed experiments list to: {output_file}")


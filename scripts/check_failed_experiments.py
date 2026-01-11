#!/usr/bin/env python3
"""
Check which DarkBench experiments failed or are incomplete.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
from pathlib import Path
from collections import defaultdict


def check_failed_experiments(subdirectory: str = "darkbench_experiment"):
    """Check for failed or incomplete experiments."""
    raw_dir = Path("data/raw") / subdirectory
    
    if not raw_dir.exists():
        print(f"Directory not found: {raw_dir}")
        return
    
    failed = []
    incomplete = []
    error_files = []
    
    for conv_file in raw_dir.glob("*.json"):
        try:
            with open(conv_file, 'r') as f:
                conv = json.load(f)
            
            turns = conv.get("turns", [])
            num_turns = len(turns)
            
            # Check for errors in responses
            has_errors = False
            error_details = []
            
            for turn in turns:
                response = turn.get("model_response", "")
                if "[Error:" in response or "Error code:" in response or "429" in response:
                    has_errors = True
                    error_details.append({
                        "turn": turn.get("turn_number"),
                        "error": response[:200] if len(response) < 200 else response[:200]
                    })
            
            # Check manipulation scores for errors
            for turn in turns:
                score = turn.get("manipulation_score", {})
                if score and "error" in str(score).lower():
                    has_errors = True
                    if not error_details:
                        error_details.append({
                            "turn": turn.get("turn_number"),
                            "error": "Scoring error"
                        })
            
            # Check if incomplete (should have 5 turns for DarkBench)
            if num_turns < 5:
                incomplete.append({
                    "file": conv_file.name,
                    "turns": num_turns,
                    "persona": conv.get("persona_name", "unknown"),
                    "pattern": conv.get("feedback_pattern", "unknown"),
                    "scenario": conv.get("scenario_name", "unknown"),
                    "has_errors": has_errors,
                    "error_details": error_details
                })
            
            # Check if has errors
            if has_errors:
                error_files.append({
                    "file": conv_file.name,
                    "turns": num_turns,
                    "persona": conv.get("persona_name", "unknown"),
                    "pattern": conv.get("feedback_pattern", "unknown"),
                    "scenario": conv.get("scenario_name", "unknown"),
                    "error_details": error_details
                })
        
        except Exception as e:
            failed.append({
                "file": conv_file.name,
                "error": str(e)
            })
    
    return failed, incomplete, error_files


def print_failed_report(failed, incomplete, error_files):
    """Print a report of failed experiments."""
    print("=" * 80)
    print("DARKBENCH EXPERIMENT FAILURE ANALYSIS")
    print("=" * 80)
    print()
    
    # Failed to load
    if failed:
        print(f"❌ FAILED TO LOAD: {len(failed)} files")
        print("-" * 80)
        for item in failed[:10]:
            print(f"  {item['file']}: {item['error']}")
        if len(failed) > 10:
            print(f"  ... and {len(failed) - 10} more")
        print()
    
    # Incomplete conversations
    if incomplete:
        print(f"⚠ INCOMPLETE CONVERSATIONS (< 5 turns): {len(incomplete)}")
        print("-" * 80)
        
        # Group by persona
        by_persona = defaultdict(list)
        by_pattern = defaultdict(list)
        
        for item in incomplete:
            by_persona[item["persona"]].append(item)
            by_pattern[item["pattern"]].append(item)
        
        print("\nBy Persona:")
        for persona, items in sorted(by_persona.items()):
            print(f"  {persona}: {len(items)} incomplete")
        
        print("\nBy Feedback Pattern:")
        for pattern, items in sorted(by_pattern.items()):
            print(f"  {pattern}: {len(items)} incomplete")
        
        print("\nSample Incomplete Conversations:")
        for item in incomplete[:10]:
            print(f"  {item['file']}")
            print(f"    Turns: {item['turns']}/5 | Persona: {item['persona']} | Pattern: {item['pattern']}")
            if item['has_errors']:
                print(f"    Has API errors: Yes")
            print()
        
        if len(incomplete) > 10:
            print(f"  ... and {len(incomplete) - 10} more incomplete conversations")
        print()
    
    # Files with errors
    if error_files:
        print(f"⚠ CONVERSATIONS WITH API ERRORS: {len(error_files)}")
        print("-" * 80)
        
        # Group by error type
        error_types = defaultdict(int)
        for item in error_files:
            for err in item.get("error_details", []):
                err_msg = str(err.get("error", "")).lower()
                if "429" in err_msg or "quota" in err_msg:
                    error_types["quota_exceeded"] += 1
                elif "error" in err_msg:
                    error_types["api_error"] += 1
                else:
                    error_types["other"] += 1
        
        print("\nError Types:")
        for err_type, count in sorted(error_types.items()):
            print(f"  {err_type}: {count}")
        
        print("\nSample Error Conversations:")
        for item in error_files[:10]:
            print(f"  {item['file']}")
            print(f"    Persona: {item['persona']} | Pattern: {item['pattern']}")
            for err in item.get("error_details", [])[:2]:
                print(f"    Turn {err.get('turn')}: {err.get('error', '')[:100]}")
            print()
        
        if len(error_files) > 10:
            print(f"  ... and {len(error_files) - 10} more conversations with errors")
        print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total issues found:")
    print(f"  Failed to load: {len(failed)}")
    print(f"  Incomplete (< 5 turns): {len(incomplete)}")
    print(f"  With API errors: {len(error_files)}")
    print()
    
    # Recommendations
    if incomplete or error_files:
        print("RECOMMENDATIONS:")
        if incomplete:
            print(f"  - {len(incomplete)} conversations need to be re-run")
        if error_files:
            print(f"  - Check API quota/keys for {len(error_files)} conversations with errors")
        print("  - Consider using --resume flag to skip completed conversations")
    else:
        print("✅ All conversations appear complete!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Check for failed DarkBench experiments")
    parser.add_argument(
        "--subdirectory",
        type=str,
        default="darkbench_experiment",
        help="Subdirectory containing experiment data"
    )
    
    args = parser.parse_args()
    
    failed, incomplete, error_files = check_failed_experiments(args.subdirectory)
    print_failed_report(failed, incomplete, error_files)


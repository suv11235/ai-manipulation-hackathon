#!/usr/bin/env python3
"""
Show full conversation for an extreme example.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
from pathlib import Path
from src.data_persistence import DataPersistence


def show_conversation(conversation_file: str):
    """Display a full conversation in readable format."""
    with open(conversation_file, 'r') as f:
        conv = json.load(f)
    
    print("=" * 80)
    print("CONVERSATION DETAILS")
    print("=" * 80)
    print(f"Scenario: {conv.get('scenario_name', 'Unknown')}")
    print(f"Persona: {conv.get('persona_name', 'Unknown')}")
    print(f"Feedback Pattern: {conv.get('feedback_pattern', 'Unknown')}")
    print(f"Model: {conv.get('model', 'Unknown')}")
    print()
    
    # Show initial setup
    if conv.get('turns'):
        first_turn = conv['turns'][0]
        print("=" * 80)
        print("INITIAL QUERY (DarkBench)")
        print("=" * 80)
        # The initial query is in the scenario setup, but we can infer from first response context
        print("(Initial query would be in scenario setup)")
        print()
    
    # Show all turns
    print("=" * 80)
    print("CONVERSATION TURNS")
    print("=" * 80)
    print()
    
    for turn in conv.get('turns', []):
        turn_num = turn.get('turn_number', 0)
        score = turn.get('manipulation_score', {}).get('overall_score', 0.0) if turn.get('manipulation_score') else 0.0
        tactics = turn.get('manipulation_score', {}).get('detected_tactics', []) if turn.get('manipulation_score') else []
        
        print(f"TURN {turn_num} (Manipulation Score: {score:.2f})")
        if tactics:
            print(f"Tactics: {', '.join(tactics)}")
        print("-" * 80)
        
        print("ASSISTANT:")
        response = turn.get('model_response', '')
        # Wrap long responses
        if len(response) > 500:
            print(response[:500] + "...")
            print(f"[... {len(response) - 500} more characters ...]")
        else:
            print(response)
        print()
        
        print("USER FEEDBACK:")
        feedback = turn.get('user_feedback', '')
        if len(feedback) > 300:
            print(feedback[:300] + "...")
        else:
            print(feedback)
        print()
        print("=" * 80)
        print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Show full conversation for an extreme example")
    parser.add_argument(
        "file",
        type=str,
        help="Path to conversation JSON file"
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}")
        sys.exit(1)
    
    show_conversation(args.file)


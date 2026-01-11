#!/usr/bin/env python3
"""
Demonstrate how DarkBench queries are converted and used.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.darkbench_loader import load_darkbench_scenarios

def demo_darkbench_usage():
    """Show how DarkBench queries are converted to scenarios."""
    print("=" * 70)
    print("DARKBENCH QUERY → SCENARIO CONVERSION")
    print("=" * 70)
    print()
    
    # Load 2 example queries
    scenarios = load_darkbench_scenarios(
        'data/darkbench/darkbench.json',
        max_queries=2
    )
    
    print(f"Loaded {len(scenarios)} DarkBench queries as scenarios\n")
    
    for name, scenario in scenarios.items():
        print(f"Query ID: {name}")
        print(f"DarkBench Query: {scenario.setup}")
        print(f"Manipulation Opportunities: {scenario.manipulation_opportunities}")
        print(f"Description: {scenario.description}")
        print()
        print("How it's used in conversation:")
        print(f"  System: [Persona system prompt]")
        print(f"  User:   {scenario.setup[:60]}...")
        print(f"  → This becomes Turn 1, then continues for 10 turns")
        print()
        print("-" * 70)
        print()

if __name__ == "__main__":
    demo_darkbench_usage()


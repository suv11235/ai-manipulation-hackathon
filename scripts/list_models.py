#!/usr/bin/env python3
"""
List all available models configured in the system.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import MODELS


def list_models():
    """List all configured models."""
    print("=" * 70)
    print("AVAILABLE MODELS")
    print("=" * 70)
    print()
    
    # Group by provider
    openai_models = {}
    anthropic_models = {}
    other_models = {}
    
    for key, model_name in MODELS.items():
        if 'gpt' in key.lower() or 'openai' in key.lower():
            openai_models[key] = model_name
        elif 'claude' in key.lower() or 'anthropic' in key.lower():
            anthropic_models[key] = model_name
        else:
            other_models[key] = model_name
    
    if openai_models:
        print("OpenAI Models:")
        print("-" * 70)
        for key, model_name in sorted(openai_models.items()):
            print(f"  {key:20} → {model_name}")
        print()
    
    if anthropic_models:
        print("Anthropic Models:")
        print("-" * 70)
        for key, model_name in sorted(anthropic_models.items()):
            print(f"  {key:20} → {model_name}")
        print()
    
    if other_models:
        print("Other Models:")
        print("-" * 70)
        for key, model_name in sorted(other_models.items()):
            print(f"  {key:20} → {model_name}")
        print()
    
    print("=" * 70)
    print(f"Total: {len(MODELS)} models configured")
    print("=" * 70)
    print()
    print("Usage examples:")
    print("  # Single model:")
    print("  python experiments/run_darkbench_experiment.py --models gpt35")
    print()
    print("  # Multiple models:")
    print("  python experiments/run_darkbench_experiment.py --models gpt35 claude-3-5-sonnet")
    print()
    print("  # All OpenAI models:")
    print(f"  python experiments/run_darkbench_experiment.py --models {' '.join(openai_models.keys())}")


if __name__ == "__main__":
    list_models()


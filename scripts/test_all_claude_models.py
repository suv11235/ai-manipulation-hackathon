#!/usr/bin/env python3
"""
Test all possible Claude model names to find what's available.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from anthropic import Anthropic
from src.config import ANTHROPIC_API_KEY

# List of possible model names to test
MODELS_TO_TEST = [
    # Claude 3.5 Sonnet variants
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-20240620",
    "claude-3-5-sonnet",
    # Claude Sonnet 4.5 (newer)
    "claude-sonnet-4-5-20250929",
    "claude-sonnet-4-5",
    "claude-4-5-sonnet",
    # Claude 3 models
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307",
    # Claude 3.5 Haiku
    "claude-3-5-haiku-20241022",
    "claude-3-5-haiku",
]

def test_model(model_name):
    """Test if a model is available."""
    try:
        client = Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=model_name,
            max_tokens=10,
            messages=[{"role": "user", "content": "hi"}]
        )
        return True, None
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    print("=" * 70)
    print("TESTING ALL CLAUDE MODELS")
    print("=" * 70)
    print()
    
    available = []
    unavailable = []
    
    for model in MODELS_TO_TEST:
        print(f"Testing {model:40}... ", end="", flush=True)
        success, error = test_model(model)
        if success:
            print("✓ AVAILABLE")
            available.append(model)
        else:
            print(f"✗ {error[:50]}")
            unavailable.append((model, error))
        import time
        time.sleep(0.3)  # Rate limit protection
    
    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print()
    print("AVAILABLE MODELS:")
    for model in available:
        print(f"  ✓ {model}")
    
    print()
    print("UNAVAILABLE MODELS:")
    for model, error in unavailable:
        print(f"  ✗ {model}")
        if "not_found" in error.lower():
            print(f"     → Model not found")
        elif "rate_limit" in error.lower() or "429" in error:
            print(f"     → Rate limit")
        else:
            print(f"     → {error[:60]}")
    
    print()
    if available:
        print(f"✅ Found {len(available)} working model(s)")
        print(f"\nRecommended: {available[0]}")
    else:
        print("❌ No working models found")


#!/usr/bin/env python3
"""
Quick test script to check Claude API status and limits.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from anthropic import Anthropic
from src.config import ANTHROPIC_API_KEY
import time


def test_claude_api():
    """Test Claude API with a simple request."""
    print("=" * 70)
    print("CLAUDE API TEST")
    print("=" * 70)
    print()
    
    if not ANTHROPIC_API_KEY:
        print("❌ ANTHROPIC_API_KEY not set in .env file")
        return False
    
    print(f"✓ API Key found: {ANTHROPIC_API_KEY[:10]}...")
    print()
    
    # Test different Claude models
    models_to_test = [
        "claude-sonnet-4-5-20250929",  # New Sonnet 4.5 (replaces deprecated 3.5 Sonnet)
        "claude-sonnet-4-5",  # Short form
        "claude-3-5-haiku-20241022",  # Claude 3.5 Haiku
        "claude-3-haiku-20240307",  # Claude 3 Haiku
    ]
    
    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    
    results = {}
    
    for model in models_to_test:
        print(f"Testing {model}...")
        try:
            start_time = time.time()
            response = client.messages.create(
                model=model,
                max_tokens=100,
                messages=[
                    {"role": "user", "content": "Say 'Hello, API test successful!' in exactly those words."}
                ]
            )
            elapsed = time.time() - start_time
            
            response_text = response.content[0].text
            success = "Hello, API test successful!" in response_text or "successful" in response_text.lower()
            
            if success:
                print(f"  ✓ SUCCESS ({elapsed:.2f}s)")
                results[model] = {"status": "success", "time": elapsed, "response": response_text[:50]}
            else:
                print(f"  ⚠ PARTIAL ({elapsed:.2f}s) - Unexpected response")
                results[model] = {"status": "partial", "time": elapsed, "response": response_text[:50]}
            
        except Exception as e:
            error_msg = str(e)
            print(f"  ❌ FAILED: {error_msg[:100]}")
            results[model] = {"status": "failed", "error": error_msg}
            
            # Check for specific error types
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                print(f"     → Rate limit / Quota issue detected")
            elif "401" in error_msg or "unauthorized" in error_msg.lower():
                print(f"     → Authentication issue")
            elif "invalid" in error_msg.lower() and "model" in error_msg.lower():
                print(f"     → Model not available")
        
        print()
        time.sleep(0.5)  # Small delay between requests
    
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    
    for model, result in results.items():
        status = result.get("status", "unknown")
        if status == "success":
            print(f"✓ {model:35} - Working ({result.get('time', 0):.2f}s)")
        elif status == "partial":
            print(f"⚠ {model:35} - Partial ({result.get('time', 0):.2f}s)")
        else:
            error = result.get("error", "Unknown error")
            print(f"❌ {model:35} - Failed: {error[:60]}")
    
    print()
    
    # Check specifically for claude-sonnet-4-5 (replacement for deprecated 3.5 Sonnet)
    sonnet_result = results.get("claude-sonnet-4-5-20250929", {})
    if sonnet_result.get("status") == "success":
        print("✅ claude-sonnet-4-5-20250929 is OPERATIONAL")
        print("   (This replaces the deprecated claude-3-5-sonnet-20241022)")
        return True
    else:
        # Try short form
        sonnet_result_short = results.get("claude-sonnet-4-5", {})
        if sonnet_result_short.get("status") == "success":
            print("✅ claude-sonnet-4-5 is OPERATIONAL")
            return True
        else:
            print("❌ claude-sonnet-4-5 is NOT OPERATIONAL")
            print(f"   Error: {sonnet_result.get('error', sonnet_result_short.get('error', 'Unknown'))}")
            print("   Note: claude-3-5-sonnet-20241022 has been deprecated and retired")
            return False


if __name__ == "__main__":
    success = test_claude_api()
    sys.exit(0 if success else 1)


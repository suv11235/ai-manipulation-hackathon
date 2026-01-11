"""
Basic test script to verify the PFMD system is working.
Tests a single conversation with minimal setup.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.conversation import run_conversation
from src.config import MODELS

def test_basic_conversation():
    """Test a single conversation with neutral persona and reinforcing feedback."""
    print("Testing basic conversation...")
    print(f"Available models: {list(MODELS.keys())}")

    model_key = "gpt35"
    print(f"Using model: {model_key} ({MODELS[model_key]})")
    
    try:
        result = run_conversation(
            scenario_name="health_misinformation",
            persona_name="neutral",
            feedback_pattern="reinforcing",
            model_key=model_key
        )
        
        print(f"\n✓ Conversation completed successfully!")
        print(f"  Scenario: {result.scenario_name}")
        print(f"  Persona: {result.persona_name}")
        print(f"  Feedback Pattern: {result.feedback_pattern}")
        print(f"  Model: {result.model}")
        print(f"  Number of turns: {len(result.turns)}")
        print(f"\nFirst turn preview:")
        if result.turns:
            first_turn = result.turns[0]
            print(f"  Model: {first_turn.model_response[:200]}...")
            print(f"  User: {first_turn.user_feedback}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error running conversation: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_basic_conversation()
    sys.exit(0 if success else 1)


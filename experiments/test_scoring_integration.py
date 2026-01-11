"""
Test script to verify scoring integration in conversation flow.
Tests that manipulation scores are automatically calculated during conversations.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.conversation import run_conversation
from src.config import MODELS
from src.metrics import calculate_metrics


def test_scoring_integration():
    """Test that scoring is automatically integrated into conversations."""
    print("Testing scoring integration in conversation flow...\n")
    
    # Test with scoring enabled (default)
    print("=" * 60)
    print("Test 1: Conversation with automatic scoring enabled")
    print("=" * 60)
    
    try:
        result = run_conversation(
            scenario_name="health_misinformation",
            persona_name="neutral",
            feedback_pattern="reinforcing",
            model_key="gpt35",
            enable_scoring=True
        )
        
        print(f"✓ Conversation completed: {len(result.turns)} turns")
        print(f"  Scenario: {result.scenario_name}")
        print(f"  Persona: {result.persona_name}")
        print(f"  Feedback Pattern: {result.feedback_pattern}")
        print(f"  Model: {result.model}\n")
        
        # Check scoring results
        scored_turns = [t for t in result.turns if t.manipulation_score is not None]
        print(f"Turns with scores: {len(scored_turns)} / {len(result.turns)}")
        
        if scored_turns:
            print("\nSample scores:")
            for i, turn in enumerate(scored_turns[:3], 1):
                score = turn.manipulation_score.get("overall_score", 0.0)
                tactics = turn.manipulation_score.get("detected_tactics", [])
                confidence = turn.manipulation_score.get("confidence", 0.0)
                print(f"  Turn {turn.turn_number}:")
                print(f"    Overall Score: {score:.2f}")
                print(f"    Confidence: {confidence:.2f}")
                print(f"    Detected Tactics: {', '.join(tactics) if tactics else 'None'}")
            
            # Calculate metrics
            print("\n" + "-" * 60)
            print("Calculating metrics from scored conversation...")
            metrics = calculate_metrics(result)
            
            print(f"  Mean Manipulation: {metrics.mean_manipulation:.2f}")
            print(f"  Reinforcement Sensitivity: {metrics.reinforcement_sensitivity:.2f}")
            print(f"  Trajectory: {metrics.manipulation_trajectory}")
            print(f"  Peak Manipulation: {metrics.peak_manipulation:.2f} at turn {metrics.peak_turn}")
            
            # Show turn-by-turn scores
            print("\nTurn-by-turn manipulation scores:")
            for turn in result.turns:
                if turn.manipulation_score:
                    score = turn.manipulation_score.get("overall_score", 0.0)
                    print(f"  Turn {turn.turn_number}: {score:.2f}")
                else:
                    print(f"  Turn {turn.turn_number}: [not scored]")
        else:
            print("⚠ No turns were scored. Check if scoring model is available.")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test with scoring disabled
    print("\n" + "=" * 60)
    print("Test 2: Conversation with scoring disabled")
    print("=" * 60)
    
    try:
        result_no_scoring = run_conversation(
            scenario_name="health_misinformation",
            persona_name="neutral",
            feedback_pattern="reinforcing",
            model_key="gpt35",
            enable_scoring=False
        )
        
        print(f"✓ Conversation completed: {len(result_no_scoring.turns)} turns")
        scored_turns = [t for t in result_no_scoring.turns if t.manipulation_score is not None]
        print(f"Turns with scores: {len(scored_turns)} / {len(result_no_scoring.turns)}")
        
        if len(scored_turns) == 0:
            print("✓ Correctly disabled scoring")
        else:
            print("⚠ Warning: Some turns were scored even though scoring was disabled")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test with different persona (should show different manipulation patterns)
    print("\n" + "=" * 60)
    print("Test 3: Expert persona (expected higher manipulation)")
    print("=" * 60)
    
    try:
        result_expert = run_conversation(
            scenario_name="health_misinformation",
            persona_name="expert",
            feedback_pattern="reinforcing",
            model_key="gpt35",
            enable_scoring=True
        )
        
        scored_turns = [t for t in result_expert.turns if t.manipulation_score is not None]
        if scored_turns:
            scores = [t.manipulation_score.get("overall_score", 0.0) for t in scored_turns]
            mean_score = sum(scores) / len(scores) if scores else 0.0
            print(f"✓ Expert persona conversation completed")
            print(f"  Mean manipulation score: {mean_score:.2f}")
            print(f"  Score range: {min(scores):.2f} - {max(scores):.2f}")
            
            # Compare with neutral
            if 'result' in locals() and result.turns:
                neutral_scores = [t.manipulation_score.get("overall_score", 0.0) 
                                 for t in result.turns if t.manipulation_score]
                if neutral_scores:
                    neutral_mean = sum(neutral_scores) / len(neutral_scores)
                    print(f"  Neutral persona mean: {neutral_mean:.2f}")
                    print(f"  Difference: {mean_score - neutral_mean:.2f}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Scoring integration test completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_scoring_integration()


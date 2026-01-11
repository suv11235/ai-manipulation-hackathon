"""
Test script for data persistence.
Tests saving and loading conversation results.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.conversation import run_conversation
from src.data_persistence import DataPersistence, save_conversation, load_conversation, save_metrics
from src.metrics import calculate_metrics
from src.config import MODELS


def test_persistence():
    """Test data persistence functionality."""
    print("Testing data persistence...\n")
    
    persistence = DataPersistence()
    
    # Test 1: Save and load a conversation
    print("=" * 60)
    print("Test 1: Save and Load Conversation")
    print("=" * 60)
    
    try:
        # Run a conversation
        result = run_conversation(
            scenario_name="health_misinformation",
            persona_name="neutral",
            feedback_pattern="reinforcing",
            model_key="gpt35",
            enable_scoring=True,
            auto_save=False  # Manual save for testing
        )
        
        print(f"✓ Conversation completed: {len(result.turns)} turns")
        
        # Save conversation
        saved_path = persistence.save_conversation(result, subdirectory="test")
        print(f"✓ Conversation saved to: {saved_path}")
        
        # Load conversation
        loaded_result = persistence.load_conversation(saved_path)
        print(f"✓ Conversation loaded from: {saved_path}")
        
        # Verify data integrity
        assert loaded_result.scenario_name == result.scenario_name
        assert loaded_result.persona_name == result.persona_name
        assert loaded_result.feedback_pattern == result.feedback_pattern
        assert len(loaded_result.turns) == len(result.turns)
        assert loaded_result.conversation_id == result.conversation_id
        
        # Verify turn data
        for orig_turn, loaded_turn in zip(result.turns, loaded_result.turns):
            assert orig_turn.turn_number == loaded_turn.turn_number
            assert orig_turn.model_response == loaded_turn.model_response
            assert orig_turn.user_feedback == loaded_turn.user_feedback
            if orig_turn.manipulation_score:
                assert loaded_turn.manipulation_score is not None
                assert orig_turn.manipulation_score.get("overall_score") == \
                       loaded_turn.manipulation_score.get("overall_score")
        
        print("✓ Data integrity verified")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Auto-save during conversation
    print("\n" + "=" * 60)
    print("Test 2: Auto-save During Conversation")
    print("=" * 60)
    
    try:
        result_auto = run_conversation(
            scenario_name="financial_pressure",
            persona_name="expert",
            feedback_pattern="resistant",
            model_key="gpt35",
            enable_scoring=True,
            auto_save=True,
            save_subdirectory="test"
        )
        
        print(f"✓ Conversation with auto-save completed: {len(result_auto.turns)} turns")
        print(f"✓ Conversation ID: {result_auto.conversation_id}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Save and load metrics
    print("\n" + "=" * 60)
    print("Test 3: Save and Load Metrics")
    print("=" * 60)
    
    try:
        # Calculate metrics
        metrics = calculate_metrics(result)
        
        # Save metrics
        metrics_path = persistence.save_metrics(metrics, subdirectory="test")
        print(f"✓ Metrics saved to: {metrics_path}")
        
        # Verify file exists and is readable
        import json
        with open(metrics_path, 'r') as f:
            metrics_data = json.load(f)
        
        assert metrics_data["scenario_name"] == metrics.scenario_name
        assert metrics_data["persona_name"] == metrics.persona_name
        assert metrics_data["mean_manipulation"] == metrics.mean_manipulation
        assert len(metrics_data["turn_scores"]) == len(metrics.turn_scores)
        
        print("✓ Metrics file verified")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: List and filter conversations
    print("\n" + "=" * 60)
    print("Test 4: List and Filter Conversations")
    print("=" * 60)
    
    try:
        # List all conversations
        all_files = persistence.list_conversations(subdirectory="test")
        print(f"✓ Found {len(all_files)} conversation files")
        
        # Filter by persona
        neutral_files = persistence.list_conversations(
            persona_name="neutral",
            subdirectory="test"
        )
        print(f"✓ Found {len(neutral_files)} conversations with neutral persona")
        
        # Filter by scenario
        health_files = persistence.list_conversations(
            scenario_name="health",
            subdirectory="test"
        )
        print(f"✓ Found {len(health_files)} conversations with health scenario")
        
        # Load all matching conversations
        loaded_conversations = persistence.load_all_conversations(
            persona_name="neutral",
            subdirectory="test"
        )
        print(f"✓ Loaded {len(loaded_conversations)} conversations")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 5: Convenience functions
    print("\n" + "=" * 60)
    print("Test 5: Convenience Functions")
    print("=" * 60)
    
    try:
        # Test convenience save
        from src.data_persistence import save_conversation, save_metrics
        
        saved_path = save_conversation(result, subdirectory="test")
        print(f"✓ Convenience save_conversation() worked: {saved_path}")
        
        metrics_path = save_metrics(metrics, subdirectory="test")
        print(f"✓ Convenience save_metrics() worked: {metrics_path}")
        
        loaded = load_conversation(saved_path)
        print(f"✓ Convenience load_conversation() worked: {len(loaded.turns)} turns")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Persistence test completed!")
    print("=" * 60)
    print(f"\nData saved in:")
    print(f"  Raw conversations: {persistence.raw_dir}")
    print(f"  Processed metrics: {persistence.processed_dir}")
    print(f"  Results: {persistence.results_dir}")


if __name__ == "__main__":
    test_persistence()


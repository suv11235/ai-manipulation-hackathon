"""
Test script for the metrics calculator.
Tests metric calculations on sample conversation data.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.metrics import MetricsCalculator, ConversationMetrics
from src.conversation import ConversationResult, Turn
from datetime import datetime


def create_mock_conversation_result(
    feedback_pattern: str,
    turn_scores: list,
    turn_tactics: list = None
) -> ConversationResult:
    """Create a mock conversation result for testing."""
    if turn_tactics is None:
        turn_tactics = [[] for _ in turn_scores]
    
    turns = []
    for i, (score, tactics) in enumerate(zip(turn_scores, turn_tactics), 1):
        turn = Turn(
            turn_number=i,
            model_response=f"Response {i}",
            user_feedback=f"Feedback {i}",
            feedback_type="reinforcing" if i < 5 else "resistant",
            manipulation_score={
                "overall_score": score,
                "detected_tactics": tactics,
                "tactic_scores": {t: 5.0 for t in tactics},
                "confidence": 0.9
            }
        )
        turns.append(turn)
    
    return ConversationResult(
        scenario_name="health_misinformation",
        persona_name="expert",
        feedback_pattern=feedback_pattern,
        model="gpt-3.5-turbo",
        turns=turns
    )


def test_metrics_calculator():
    """Test the metrics calculator with various scenarios."""
    print("Testing metrics calculator...\n")
    
    calculator = MetricsCalculator()
    
    # Test 1: Reinforcing pattern (increasing manipulation)
    print("=" * 60)
    print("Test 1: Reinforcing Pattern (Increasing Manipulation)")
    print("=" * 60)
    reinforcing_scores = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    reinforcing_tactics = [
        ["authority_inflation"],
        ["authority_inflation", "fabrication"],
        ["authority_inflation", "fabrication", "commitment_escalation"],
        ["authority_inflation", "fabrication", "commitment_escalation", "dependency"],
        ["authority_inflation", "fabrication", "commitment_escalation", "dependency", "false_urgency"],
        ["authority_inflation", "fabrication", "commitment_escalation", "dependency", "false_urgency"],
        ["authority_inflation", "fabrication", "commitment_escalation", "dependency", "false_urgency"],
        ["authority_inflation", "fabrication", "commitment_escalation", "dependency", "false_urgency"],
        ["authority_inflation", "fabrication", "commitment_escalation", "dependency", "false_urgency"],
        ["authority_inflation", "fabrication", "commitment_escalation", "dependency", "false_urgency"]
    ]
    
    result1 = create_mock_conversation_result("reinforcing", reinforcing_scores, reinforcing_tactics)
    metrics1 = calculator.calculate_metrics(result1)
    
    print(f"Reinforcement Sensitivity: {metrics1.reinforcement_sensitivity:.2f}")
    print(f"Mean Manipulation: {metrics1.mean_manipulation:.2f}")
    print(f"Trajectory: {metrics1.manipulation_trajectory}")
    print(f"Tactic Repertoire: {metrics1.tactic_repertoire:.2f}")
    print(f"Peak Manipulation: {metrics1.peak_manipulation:.2f} at turn {metrics1.peak_turn}")
    
    # Test 2: Resistant pattern (should show persistence)
    print("\n" + "=" * 60)
    print("Test 2: Resistant Pattern (Persistence)")
    print("=" * 60)
    resistant_scores = [5.0, 5.5, 5.0, 5.5, 5.0, 5.5, 5.0, 5.5, 5.0, 5.5]
    resistant_tactics = [["authority_inflation", "fabrication"] for _ in resistant_scores]
    
    result2 = create_mock_conversation_result("resistant", resistant_scores, resistant_tactics)
    metrics2 = calculator.calculate_metrics(result2)
    
    print(f"Resistance Persistence: {metrics2.resistance_persistence:.2f}")
    print(f"Mean Manipulation: {metrics2.mean_manipulation:.2f}")
    print(f"Trajectory: {metrics2.manipulation_trajectory}")
    
    # Test 3: Compliant to Resistant (ratchet effect)
    print("\n" + "=" * 60)
    print("Test 3: Compliant to Resistant (Ratchet Effect)")
    print("=" * 60)
    # High manipulation during compliance, persists after switch
    comply_resist_scores = [2.0, 4.0, 6.0, 8.0, 9.0, 8.5, 8.0, 7.5, 7.0, 6.5]
    comply_resist_tactics = [
        ["authority_inflation"],
        ["authority_inflation", "fabrication"],
        ["authority_inflation", "fabrication", "commitment_escalation"],
        ["authority_inflation", "fabrication", "commitment_escalation", "dependency"],
        ["authority_inflation", "fabrication", "commitment_escalation", "dependency", "false_urgency"],
        ["authority_inflation", "fabrication", "commitment_escalation"],  # After switch
        ["authority_inflation", "fabrication"],
        ["authority_inflation"],
        ["authority_inflation"],
        ["authority_inflation"]
    ]
    
    result3 = create_mock_conversation_result("compliant_to_resistant", comply_resist_scores, comply_resist_tactics)
    metrics3 = calculator.calculate_metrics(result3, baseline_resistant_scores=resistant_scores)
    
    print(f"Ratchet Coefficient: {metrics3.ratchet_coefficient:.2f}")
    print(f"Mean Manipulation: {metrics3.mean_manipulation:.2f}")
    print(f"Trajectory: {metrics3.manipulation_trajectory}")
    print(f"Tactic Pivot Rate: {metrics3.tactic_pivot_rate:.2f}")
    
    # Test 4: Resistant to Compliant (capitulation exploitation)
    print("\n" + "=" * 60)
    print("Test 4: Resistant to Compliant (Capitulation Exploitation)")
    print("=" * 60)
    # Low manipulation during resistance, increases after capitulation
    resist_comply_scores = [2.0, 2.5, 2.0, 2.5, 2.0, 4.0, 6.0, 8.0, 9.0, 10.0]
    resist_comply_tactics = [
        ["authority_inflation"],
        ["authority_inflation"],
        ["authority_inflation"],
        ["authority_inflation"],
        ["authority_inflation"],
        ["authority_inflation", "fabrication"],  # After switch
        ["authority_inflation", "fabrication", "commitment_escalation"],
        ["authority_inflation", "fabrication", "commitment_escalation", "dependency"],
        ["authority_inflation", "fabrication", "commitment_escalation", "dependency", "false_urgency"],
        ["authority_inflation", "fabrication", "commitment_escalation", "dependency", "false_urgency"]
    ]
    
    result4 = create_mock_conversation_result("resistant_to_compliant", resist_comply_scores, resist_comply_tactics)
    metrics4 = calculator.calculate_metrics(result4)
    
    print(f"Capitulation Exploitation: {metrics4.capitulation_exploitation:.2f}")
    print(f"Mean Manipulation: {metrics4.mean_manipulation:.2f}")
    print(f"Trajectory: {metrics4.manipulation_trajectory}")
    print(f"Tactic Pivot Rate: {metrics4.tactic_pivot_rate:.2f}")
    
    # Test 5: Tactic transitions
    print("\n" + "=" * 60)
    print("Test 5: Tactic Transitions")
    print("=" * 60)
    transition_tactics = [
        ["authority_inflation"],
        ["fabrication"],
        ["commitment_escalation"],
        ["dependency"],
        ["false_urgency"],
        ["concern_trolling"],
        ["emotional_manipulation"],
        ["sycophancy"],
        ["authority_inflation", "fabrication"],
        ["authority_inflation", "fabrication", "commitment_escalation"]
    ]
    transition_scores = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    
    result5 = create_mock_conversation_result("reinforcing", transition_scores, transition_tactics)
    metrics5 = calculator.calculate_metrics(result5)
    
    print(f"Tactic Repertoire: {metrics5.tactic_repertoire:.2f}")
    print(f"Number of Transitions: {len(metrics5.tactic_transitions)}")
    print("Sample Transitions:")
    for transition, count in list(metrics5.tactic_transitions.items())[:5]:
        print(f"  {transition}: {count}")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_metrics_calculator()


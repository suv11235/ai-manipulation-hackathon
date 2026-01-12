"""
Data persistence for PFMD experiments.
Saves and loads conversation results and metrics to/from disk.
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from datetime import datetime
import uuid

from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, RESULTS_DIR

if TYPE_CHECKING:
    from src.conversation import ConversationResult, Turn
    from src.metrics import ConversationMetrics


class DataPersistence:
    """Handles saving and loading conversation data."""
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize data persistence.
        
        Args:
            base_dir: Base directory for data (default: from config)
        """
        if base_dir:
            self.raw_dir = os.path.join(base_dir, "raw")
            self.processed_dir = os.path.join(base_dir, "processed")
            self.results_dir = os.path.join(base_dir, "results")
        else:
            self.raw_dir = RAW_DATA_DIR
            self.processed_dir = PROCESSED_DATA_DIR
            self.results_dir = RESULTS_DIR
        
        # Ensure directories exist
        for directory in [self.raw_dir, self.processed_dir, self.results_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def _generate_filename(
        self,
        scenario_name: str,
        persona_name: str,
        feedback_pattern: str,
        model: str,
        suffix: str = "json",
        include_timestamp: bool = True,
        user_persona_name: Optional[str] = None
    ) -> str:
        """
        Generate a standardized filename for a conversation.
        
        Args:
            scenario_name: Name of scenario
            persona_name: Name of persona (model persona)
            feedback_pattern: Feedback pattern
            model: Model name
            suffix: File extension
            include_timestamp: Whether to include timestamp in filename
            user_persona_name: Optional user persona name (if used)
        
        Returns:
            Filename string
        """
        # Sanitize names for filesystem
        safe_scenario = scenario_name.replace(" ", "_").lower()
        safe_persona = persona_name.replace(" ", "_").lower()
        safe_feedback = feedback_pattern.replace(" ", "_").lower()
        safe_model = model.replace(" ", "_").replace("/", "-").lower()
        
        # If user persona is present, use it instead of model persona in filename
        # Format: scenario_userpersona_feedback_model_timestamp.json
        if user_persona_name:
            safe_user_persona = user_persona_name.replace(" ", "_").lower()
            parts = [safe_scenario, safe_user_persona, safe_feedback, safe_model]
        else:
            parts = [safe_scenario, safe_persona, safe_feedback, safe_model]
        
        if include_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            parts.append(timestamp)
        
        filename = "_".join(parts) + f".{suffix}"
        return filename
    
    def _generate_conversation_id(self) -> str:
        """Generate a unique conversation ID."""
        return str(uuid.uuid4())
    
    def save_conversation(
        self,
        conversation_result: "ConversationResult",
        subdirectory: Optional[str] = None,
        auto_id: bool = True
    ) -> str:
        """
        Save a conversation result to disk.
        
        Args:
            conversation_result: ConversationResult to save
            subdirectory: Optional subdirectory within raw_data_dir
            auto_id: Whether to auto-generate conversation_id if missing
        
        Returns:
            Path to saved file
        """
        # Generate conversation ID if missing
        if auto_id and not conversation_result.conversation_id:
            conversation_result.conversation_id = self._generate_conversation_id()
        
        # Determine save directory
        save_dir = self.raw_dir
        if subdirectory:
            save_dir = os.path.join(save_dir, subdirectory)
            os.makedirs(save_dir, exist_ok=True)
        
        # Generate filename
        filename = self._generate_filename(
            conversation_result.scenario_name,
            conversation_result.persona_name,
            conversation_result.feedback_pattern,
            conversation_result.model,
            user_persona_name=getattr(conversation_result, 'user_persona_name', None)
        )
        
        filepath = os.path.join(save_dir, filename)
        
        # Convert to dict and save
        data = conversation_result.to_dict()
        
        # Add metadata
        data["_metadata"] = {
            "saved_at": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        # Save to JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def load_conversation(self, filepath: str) -> "ConversationResult":
        """
        Load a conversation result from disk.
        
        Args:
            filepath: Path to JSON file
        
        Returns:
            ConversationResult object
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Import here to avoid circular import
        from src.conversation import Turn, ConversationResult
        
        # Reconstruct Turn objects
        turns = []
        for turn_data in data.get("turns", []):
            turn = Turn(
                turn_number=turn_data["turn_number"],
                model_response=turn_data["model_response"],
                user_feedback=turn_data["user_feedback"],
                feedback_type=turn_data["feedback_type"],
                timestamp=datetime.fromisoformat(turn_data["timestamp"]),
                manipulation_score=turn_data.get("manipulation_score")
            )
            turns.append(turn)
        
        # Reconstruct ConversationResult
        result = ConversationResult(
            scenario_name=data["scenario_name"],
            persona_name=data["persona_name"],
            feedback_pattern=data["feedback_pattern"],
            model=data["model"],
            turns=turns,
            conversation_id=data.get("conversation_id"),
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None
        )
        
        return result
    
    def save_metrics(
        self,
        metrics: "ConversationMetrics",
        subdirectory: Optional[str] = None
    ) -> str:
        """
        Save conversation metrics to disk.
        
        Args:
            metrics: ConversationMetrics to save
            subdirectory: Optional subdirectory within processed_data_dir
        
        Returns:
            Path to saved file
        """
        # Determine save directory
        save_dir = self.processed_dir
        if subdirectory:
            save_dir = os.path.join(save_dir, subdirectory)
            os.makedirs(save_dir, exist_ok=True)
        
        # Generate filename
        filename = self._generate_filename(
            metrics.scenario_name,
            metrics.persona_name,
            metrics.feedback_pattern,
            metrics.model,
            suffix="json",
            user_persona_name=getattr(metrics, 'user_persona_name', None)
        )
        
        filepath = os.path.join(save_dir, filename)
        
        # Convert metrics to dict
        data = {
            "scenario_name": metrics.scenario_name,
            "persona_name": metrics.persona_name,
            "feedback_pattern": metrics.feedback_pattern,
            "model": metrics.model,
            "user_persona_name": getattr(metrics, 'user_persona_name', None),
            "turn_scores": metrics.turn_scores,
            "turn_tactics": metrics.turn_tactics,
            "reinforcement_sensitivity": metrics.reinforcement_sensitivity,
            "resistance_persistence": metrics.resistance_persistence,
            "ratchet_coefficient": metrics.ratchet_coefficient,
            "capitulation_exploitation": metrics.capitulation_exploitation,
            "tactic_pivot_rate": metrics.tactic_pivot_rate,
            "tactic_repertoire": metrics.tactic_repertoire,
            "tactic_transitions": metrics.tactic_transitions,
            "manipulation_trajectory": metrics.manipulation_trajectory,
            "peak_manipulation": metrics.peak_manipulation,
            "peak_turn": metrics.peak_turn,
            "mean_manipulation": metrics.mean_manipulation,
            "std_manipulation": metrics.std_manipulation,
            "manipulation_range": list(metrics.manipulation_range),
            "_metadata": {
                "saved_at": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
        
        # Save to JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def list_conversations(
        self,
        scenario_name: Optional[str] = None,
        persona_name: Optional[str] = None,
        feedback_pattern: Optional[str] = None,
        model: Optional[str] = None,
        subdirectory: Optional[str] = None
    ) -> List[str]:
        """
        List all conversation files matching criteria.
        
        Args:
            scenario_name: Filter by scenario
            persona_name: Filter by persona
            feedback_pattern: Filter by feedback pattern
            model: Filter by model
            subdirectory: Search in subdirectory
        
        Returns:
            List of file paths
        """
        search_dir = self.raw_dir
        if subdirectory:
            search_dir = os.path.join(search_dir, subdirectory)
        
        if not os.path.exists(search_dir):
            return []
        
        files = []
        for filename in os.listdir(search_dir):
            if not filename.endswith('.json'):
                continue
            
            filepath = os.path.join(search_dir, filename)
            
            # Parse filename to check filters
            parts = filename.replace('.json', '').split('_')
            
            # Simple matching (could be improved)
            if scenario_name and scenario_name.lower().replace(' ', '_') not in filename.lower():
                continue
            if persona_name and persona_name.lower().replace(' ', '_') not in filename.lower():
                continue
            if feedback_pattern and feedback_pattern.lower().replace(' ', '_') not in filename.lower():
                continue
            if model and model.lower().replace(' ', '_').replace('/', '-') not in filename.lower():
                continue
            
            files.append(filepath)
        
        return sorted(files)
    
    def load_all_conversations(
        self,
        scenario_name: Optional[str] = None,
        persona_name: Optional[str] = None,
        feedback_pattern: Optional[str] = None,
        model: Optional[str] = None,
        subdirectory: Optional[str] = None
    ) -> List["ConversationResult"]:
        """
        Load all conversations matching criteria.
        
        Args:
            scenario_name: Filter by scenario
            persona_name: Filter by persona
            feedback_pattern: Filter by feedback pattern
            model: Filter by model
            subdirectory: Search in subdirectory
        
        Returns:
            List of ConversationResult objects
        """
        filepaths = self.list_conversations(
            scenario_name=scenario_name,
            persona_name=persona_name,
            feedback_pattern=feedback_pattern,
            model=model,
            subdirectory=subdirectory
        )
        
        results = []
        for filepath in filepaths:
            try:
                result = self.load_conversation(filepath)
                results.append(result)
            except Exception as e:
                print(f"Warning: Failed to load {filepath}: {e}")
        
        return results
    
    def save_experiment_summary(
        self,
        summary_data: Dict[str, Any],
        experiment_name: str
    ) -> str:
        """
        Save experiment summary/aggregate results.
        
        Args:
            summary_data: Dictionary with summary statistics
            experiment_name: Name of experiment
        
        Returns:
            Path to saved file
        """
        filename = f"{experiment_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.results_dir, filename)
        
        data = {
            "experiment_name": experiment_name,
            "summary": summary_data,
            "_metadata": {
                "saved_at": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filepath


# Convenience functions
def save_conversation(
    conversation_result: "ConversationResult",
    subdirectory: Optional[str] = None
) -> str:
    """Convenience function to save a conversation."""
    persistence = DataPersistence()
    return persistence.save_conversation(conversation_result, subdirectory)


def load_conversation(filepath: str) -> "ConversationResult":
    """Convenience function to load a conversation."""
    persistence = DataPersistence()
    return persistence.load_conversation(filepath)


def save_metrics(metrics: "ConversationMetrics", subdirectory: Optional[str] = None) -> str:
    """Convenience function to save metrics."""
    persistence = DataPersistence()
    return persistence.save_metrics(metrics, subdirectory)


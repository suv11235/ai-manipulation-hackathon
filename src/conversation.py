"""
Conversation management for PFMD experiments.
Handles multi-turn conversations with personas, scenarios, and feedback patterns.
"""
import openai
from anthropic import Anthropic
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

from src.config import OPENAI_API_KEY, ANTHROPIC_API_KEY, OPENROUTER_API_KEY, NUM_TURNS, MODELS
from src.scenarios import Scenario, get_scenario
from src.personas import Persona, get_persona
from src.user_personas import UserPersona, frame_query_for_persona
from src.feedback_simulator import FeedbackSimulator
from src.manipulation_scorer import ManipulationScorer
from src.data_persistence import DataPersistence


@dataclass
class Turn:
    """Represents a single turn in a conversation."""
    turn_number: int
    model_response: str
    user_feedback: str
    feedback_type: str
    timestamp: datetime = field(default_factory=datetime.now)
    manipulation_score: Optional[Dict[str, Any]] = None  # Scoring result from ManipulationScorer


@dataclass
class ConversationResult:
    """Results from a complete conversation."""
    scenario_name: str
    persona_name: str
    feedback_pattern: str
    model: str
    turns: List[Turn] = field(default_factory=list)
    conversation_id: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    user_persona_name: Optional[str] = None  # User persona if used (model persona is neutral)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "scenario_name": self.scenario_name,
            "persona_name": self.persona_name,
            "feedback_pattern": self.feedback_pattern,
            "model": self.model,
            "conversation_id": self.conversation_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "user_persona_name": self.user_persona_name,
            "turns": [
                {
                    "turn_number": t.turn_number,
                    "model_response": t.model_response,
                    "user_feedback": t.user_feedback,
                    "feedback_type": t.feedback_type,
                    "timestamp": t.timestamp.isoformat(),
                    "manipulation_score": t.manipulation_score
                }
                for t in self.turns
            ]
        }


class Conversation:
    """Manages a multi-turn conversation with a model."""
    
    def __init__(
        self,
        scenario: Scenario,
        persona: Persona,
        feedback_pattern: str,
        model: str,
        model_key: Optional[str] = None,
        enable_scoring: bool = True,
        scoring_model: Optional[str] = None,
        auto_save: bool = False,
        save_subdirectory: Optional[str] = None,
        num_turns: Optional[int] = None,
        max_tokens: Optional[int] = None,
        user_persona: Optional[UserPersona] = None
    ):
        """
        Initialize a conversation.
        
        Args:
            scenario: The scenario to use
            persona: The persona to apply
            feedback_pattern: Feedback pattern ("reinforcing", "resistant", etc.)
            model: Model identifier (e.g., "gpt-3.5-turbo", "claude-haiku-4-5")
            model_key: Key in MODELS dict (e.g., "gpt35", "claude")
            enable_scoring: Whether to automatically score manipulation (default: True)
            scoring_model: Model to use for scoring (default: from config)
            auto_save: Whether to auto-save conversations (default: False)
            save_subdirectory: Subdirectory for saving results
            num_turns: Number of conversation turns (default: from config NUM_TURNS)
            max_tokens: Maximum tokens per response (default: 1000 for Anthropic, unlimited for OpenAI)
            user_persona: Optional user persona to frame queries and feedback
        """
        self.scenario = scenario
        self.persona = persona
        self.feedback_pattern = feedback_pattern
        self.model = model
        self.model_key = model_key or model
        self.enable_scoring = enable_scoring
        self.auto_save = auto_save
        self.save_subdirectory = save_subdirectory
        self.user_persona = user_persona
        
        # Frame scenario setup with user persona if provided
        if user_persona:
            self.framed_setup = frame_query_for_persona(
                scenario.setup,
                user_persona,
                context=scenario.description
            )
        else:
            self.framed_setup = scenario.setup
        
        # Set num_turns and max_tokens
        from src.config import NUM_TURNS
        self.num_turns = num_turns if num_turns is not None else NUM_TURNS
        self.max_tokens = max_tokens if max_tokens is not None else None  # None means use API defaults
        
        # Initialize data persistence if auto-save enabled
        if self.auto_save:
            self.persistence = DataPersistence()
        else:
            self.persistence = None
        
        # Initialize API clients
        if OPENAI_API_KEY:
            self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        else:
            self.openai_client = None
            
        if ANTHROPIC_API_KEY:
            self.anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
        else:
            self.anthropic_client = None
        
        # Initialize OpenRouter client (uses OpenAI-compatible API)
        if OPENROUTER_API_KEY:
            self.openrouter_client = openai.OpenAI(
                api_key=OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": "https://github.com/ai-manipulation-hackathon",
                    "X-Title": "PFMD Research"
                }
            )
        else:
            self.openrouter_client = None
        
        # Initialize feedback simulator
        # Use same provider as conversation model to avoid dual API calls
        feedback_model = self.model  # Use same model as conversation by default
        # For cost savings, could use cheaper variant of same provider
        
        # Check if this is an OpenRouter model first (has "/" but not direct provider format)
        is_openrouter = (self.model.startswith("or-") or 
                        ("/" in self.model and not self.model.startswith("gpt") and 
                         not self.model.startswith("claude") and not self.model.startswith("o1")))
        
        if is_openrouter:
            # OpenRouter model - use OpenRouter for feedback too
            # Use a cheaper OpenRouter model if available, otherwise same model
            feedback_model = self.model  # Could use anthropic/claude-3.5-haiku via OpenRouter if cheaper
        elif self.model.startswith("gpt") or self.model.startswith("o1"):
            # Use cheaper GPT model for feedback if available
            feedback_model = MODELS.get("gpt35", "gpt-3.5-turbo")
        elif self.model.startswith("claude"):
            # Direct Anthropic API - use cheaper Claude model for feedback
            feedback_model = MODELS.get("claude-3-5-haiku", "claude-3-5-haiku-20241022")
        
        self.feedback_simulator = FeedbackSimulator(
            pattern=feedback_pattern,
            scenario_context=scenario.description or scenario.setup,
            model=feedback_model,
            user_persona=user_persona
        )
        
        # Initialize manipulation scorer if enabled
        # If no scoring_model specified, auto-select based on conversation model provider
        if self.enable_scoring:
            if scoring_model is None:
                # Auto-select scoring model from same provider as conversation model
                # Check if this is an OpenRouter model first
                is_openrouter = (self.model.startswith("or-") or 
                                ("/" in self.model and not self.model.startswith("gpt") and 
                                 not self.model.startswith("claude") and not self.model.startswith("o1")))
                
                if is_openrouter:
                    # OpenRouter model - use OpenRouter scoring model
                    from src.config import SCORING_MODEL_OPENROUTER
                    scoring_model = SCORING_MODEL_OPENROUTER
                elif self.model.startswith("gpt") or self.model.startswith("o1"):
                    # Use GPT-4 for OpenAI models (or gpt-4o-mini if available)
                    from src.config import SCORING_MODEL
                    scoring_model = SCORING_MODEL  # Default to gpt-4
                elif self.model.startswith("claude"):
                    # Direct Anthropic API - use Claude Sonnet 4.5 for scoring
                    from src.config import SCORING_MODEL_CLAUDE
                    scoring_model = SCORING_MODEL_CLAUDE
                else:
                    # Fallback to default
                    from src.config import SCORING_MODEL
                    scoring_model = SCORING_MODEL
            self.scorer = ManipulationScorer(model=scoring_model)
        else:
            self.scorer = None
        
        # Conversation state
        self.messages: List[Dict[str, str]] = []
        self.turns: List[Turn] = []
    
    def _call_model(self, messages: List[Dict[str, str]]) -> str:
        """Call the model API with the given messages."""
        # Check if this is an OpenRouter model (starts with "or-" or contains "/" for provider/model format)
        is_openrouter = self.model.startswith("or-") or "/" in self.model
        
        if is_openrouter:
            # OpenRouter uses OpenAI-compatible API
            if not self.openrouter_client:
                raise ValueError("OpenRouter API key not set")
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7
            }
            # Add max_tokens if specified
            if self.max_tokens is not None:
                kwargs["max_tokens"] = self.max_tokens
            response = self.openrouter_client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        
        elif self.model.startswith("gpt") or self.model.startswith("o1"):
            if not self.openai_client:
                raise ValueError("OpenAI API key not set")
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7
            }
            # Add max_tokens for OpenAI if specified
            if self.max_tokens is not None:
                kwargs["max_tokens"] = self.max_tokens
            response = self.openai_client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        
        elif self.model.startswith("claude"):
            if not self.anthropic_client:
                raise ValueError("Anthropic API key not set")
            # Anthropic API format is slightly different
            anthropic_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    # Anthropic doesn't have system role, prepend to first user message
                    if anthropic_messages and anthropic_messages[-1]["role"] == "user":
                        anthropic_messages[-1]["content"] = f"{msg['content']}\n\n{anthropic_messages[-1]['content']}"
                    else:
                        anthropic_messages.append({"role": "user", "content": msg["content"]})
                else:
                    anthropic_messages.append(msg)
            
            response = self.anthropic_client.messages.create(
                model=self.model,
                messages=anthropic_messages,
                max_tokens=self.max_tokens if self.max_tokens is not None else 1000,
                temperature=0.7
            )
            return response.content[0].text
        
        else:
            raise ValueError(f"Unknown model type: {self.model}")
    
    def run(self) -> ConversationResult:
        """
        Run the full conversation (num_turns turns).
        
        Returns:
            ConversationResult with all turns and metadata
        """
        result = ConversationResult(
            scenario_name=self.scenario.name,
            persona_name=self.persona.name,
            feedback_pattern=self.feedback_pattern,
            model=self.model,
            user_persona_name=self.user_persona.name if self.user_persona else None
        )
        
        # Initialize conversation with persona and scenario
        # Use framed setup if user persona is provided
        initial_user_message = self.framed_setup if hasattr(self, 'framed_setup') else self.scenario.setup
        self.messages = [
            {"role": "system", "content": self.persona.system_prompt},
            {"role": "user", "content": initial_user_message}
        ]
        
        # Run conversation turns
        for turn_num in range(1, self.num_turns + 1):
            # Get model response
            try:
                model_response = self._call_model(self.messages)
            except Exception as e:
                print(f"Error calling model at turn {turn_num}: {e}")
                model_response = f"[Error: {str(e)}]"
            
            # Add model response to messages
            self.messages.append({"role": "assistant", "content": model_response})
            
            # Generate user feedback
            feedback_type = self.feedback_simulator._get_feedback_type(turn_num)
            user_feedback = self.feedback_simulator.generate_feedback(
                turn=turn_num,
                model_response=model_response,
                conversation_history=self.messages
            )
            
            # Score manipulation in model response (before adding user feedback to context)
            manipulation_score = None
            if self.enable_scoring and self.scorer:
                try:
                    # Build context for scoring
                    scoring_context = {
                        "scenario": self.scenario.name,
                        "persona": self.persona.name,
                        "turn_number": turn_num,
                        "conversation_history": self.messages[:-1],  # Exclude current assistant response
                        "user_feedback": user_feedback
                    }
                    manipulation_score = self.scorer.score_turn(model_response, scoring_context)
                except Exception as e:
                    print(f"Warning: Scoring failed at turn {turn_num}: {e}")
                    manipulation_score = None
            
            # Add user feedback to messages
            self.messages.append({"role": "user", "content": user_feedback})
            
            # Store turn with score
            turn = Turn(
                turn_number=turn_num,
                model_response=model_response,
                user_feedback=user_feedback,
                feedback_type=feedback_type,
                manipulation_score=manipulation_score
            )
            self.turns.append(turn)
            result.turns.append(turn)
        
        result.end_time = datetime.now()
        
        # Auto-save if enabled
        if self.auto_save and self.persistence:
            try:
                saved_path = self.persistence.save_conversation(
                    result,
                    subdirectory=self.save_subdirectory
                )
                print(f"Conversation saved to: {saved_path}")
            except Exception as e:
                print(f"Warning: Failed to auto-save conversation: {e}")
        
        return result


def run_conversation(
    scenario_name: str,
    persona_name: str,
    feedback_pattern: str,
    model_key: str,
    enable_scoring: bool = True,
    scoring_model: Optional[str] = None,
    auto_save: bool = False,
    save_subdirectory: Optional[str] = None,
    num_turns: Optional[int] = None,
    max_tokens: Optional[int] = None
) -> ConversationResult:
    """
    Convenience function to run a conversation.
    
    Args:
        scenario_name: Name of scenario
        persona_name: Name of persona
        feedback_pattern: Feedback pattern
        model_key: Key in MODELS dict
        enable_scoring: Whether to automatically score manipulation (default: True)
        scoring_model: Model to use for scoring (default: from config)
        auto_save: Whether to automatically save conversation to disk (default: False)
        save_subdirectory: Optional subdirectory for saving
        num_turns: Number of conversation turns (default: from config)
        max_tokens: Maximum tokens per response (default: None)
        
    Returns:
        ConversationResult
    """
    scenario = get_scenario(scenario_name)
    persona = get_persona(persona_name)
    model = MODELS.get(model_key, model_key)
    
    conversation = Conversation(
        scenario=scenario,
        persona=persona,
        feedback_pattern=feedback_pattern,
        model=model,
        model_key=model_key,
        enable_scoring=enable_scoring,
        scoring_model=scoring_model,
        auto_save=auto_save,
        save_subdirectory=save_subdirectory,
        num_turns=num_turns,
        max_tokens=max_tokens
    )
    
    return conversation.run()


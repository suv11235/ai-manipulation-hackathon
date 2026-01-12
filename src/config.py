"""
Configuration file for PFMD project.
Set API keys in .env file (see .env.example)
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Model Configuration
# Add model keys here to use in experiments
# Format: "key": "actual-model-name"
MODELS = {
    # OpenAI Models
    "gpt5m": "gpt-5-mini",  # Cheapest OpenAI model for testing (if available)
    "gpt35": "gpt-3.5-turbo",  # Standard OpenAI model
    "gpt35-16k": "gpt-3.5-turbo-16k",  # GPT-3.5 with 16k context
    "gpt4": "gpt-4",  # GPT-4 standard
    "gpt4-turbo": "gpt-4-turbo-preview",  # GPT-4 Turbo
    "gpt4o": "gpt-4o",  # GPT-4 Optimized
    "gpt4o-mini": "gpt-4o-mini",  # GPT-4o Mini (cheaper)
    
    # Anthropic Models
    "claude": "claude-3-5-haiku-20241022",  # Cheapest Anthropic model
    "claude-haiku": "claude-3-haiku-20240307",  # Claude 3 Haiku
    "claude-3-5-haiku": "claude-3-5-haiku-20241022",  # Claude 3.5 Haiku (latest)
    "claude-sonnet": "claude-sonnet-4-5-20250929",  # Claude Sonnet 4.5 (replaces 3.5 Sonnet)
    "claude-3-5-sonnet": "claude-sonnet-4-5-20250929",  # Updated: Claude Sonnet 4.5 (was 3.5 Sonnet, deprecated)
    "claude-sonnet-4-5": "claude-sonnet-4-5-20250929",  # Claude Sonnet 4.5 (explicit)
    # Note: claude-3-opus and claude-3-sonnet are deprecated/retired
    
    # OpenRouter Models (uses OpenAI-compatible API)
    "or-claude-sonnet-4-5": "anthropic/claude-sonnet-4.5",  # Claude Sonnet 4.5 via OpenRouter
    "or-claude-sonnet": "anthropic/claude-sonnet-4.5",  # Alias for Claude Sonnet 4.5 via OpenRouter
}

# Experiment Configuration
NUM_TURNS = 10
FEEDBACK_SWITCH_TURN = 5  # Turn where feedback pattern switches (for switching conditions)

# Personas
PERSONA_NAMES = ["neutral", "expert", "peer", "authority"]

# Feedback Patterns
FEEDBACK_PATTERNS = [
    "reinforcing",
    "resistant", 
    "compliant_to_resistant",
    "resistant_to_compliant"
]

# Scenarios
SCENARIO_NAMES = [
    "health_misinformation",
    "financial_pressure",
    "relationship_advice",
    "political_persuasion",
    "product_recommendation"
]

# Data Paths
DATA_DIR = "data"
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
RESULTS_DIR = os.path.join(DATA_DIR, "results")

# Scoring Configuration
SCORING_MODEL = "gpt-4"  # Default model used for manipulation scoring (OpenAI)
SCORING_MODEL_CLAUDE = "claude-sonnet-4-5-20250929"  # Default scoring model for Anthropic (updated from deprecated 3.5 Sonnet)
SCORING_MODEL_OPENROUTER = "anthropic/claude-sonnet-4.5"  # Default scoring model for OpenRouter Claude models
SCORING_TEMPERATURE = 0.0  # Deterministic scoring

# Logging
LOG_LEVEL = "INFO"


# Utils package for Dinneroo analysis scripts
# All agents should import from here for consistent definitions

from .definitions import (
    CORE_7,
    REQUIRED_FOR_MVP,
    SUB_TO_CORE,
    DISH_TO_SUB,
    DISH_TO_CORE,
    MVP_STATUS_TIERS,
    get_core_7,
    get_sub_cuisine,
    get_mvp_status,
    normalize_cuisine,
)

# Gemini client for LLM-based extraction (optional import)
try:
    from .gemini_client import GeminiClient, DishMention, ExtractionResult
except ImportError:
    # google-generativeai not installed
    GeminiClient = None
    DishMention = None
    ExtractionResult = None



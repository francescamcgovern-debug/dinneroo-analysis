"""
Gemini Client Utility
=====================
Provides a wrapper around Google's Gemini API for structured extraction tasks.

Features:
- Rate limiting to avoid API throttling
- Structured JSON output parsing
- Error handling with retries
- Batch processing support

Usage:
    from scripts.utils.gemini_client import GeminiClient
    
    client = GeminiClient()
    results = client.extract_dish_mentions(text_batch)
"""

import os
import json
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import google.generativeai
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-generativeai not installed. Run: pip install google-generativeai")


@dataclass
class DishMention:
    """A single dish mention extracted from text."""
    dish_type: str
    signal_type: str  # "want" | "complaint" | "praise"
    verbatim_quote: str
    confidence: float
    source_id: Optional[str] = None


@dataclass
class ExtractionResult:
    """Result of extracting mentions from a batch of text."""
    mentions: List[DishMention]
    source_count: int
    api_calls: int
    tokens_used: int
    errors: List[str]


# Standard dish types for normalization
STANDARD_DISH_TYPES = [
    # Italian
    "Pizza", "Pasta", "Lasagne", "Risotto", "Gnocchi", "Filled Pasta", "Baked Pasta",
    # Asian - Japanese
    "Katsu", "Sushi", "Ramen", "Teriyaki", "Gyoza", "Tempura", "Udon",
    # Asian - Chinese
    "Fried Rice", "Noodles", "Stir Fry", "Sweet & Sour", "Spring Rolls", "Dim Sum", "Peking Duck",
    # Asian - Thai
    "Pad Thai", "Thai Curry", "Tom Yum", "Satay",
    # Asian - Vietnamese
    "Pho", "Banh Mi",
    # Asian - Korean
    "Korean Fried Chicken", "Bibimbap", "Bulgogi",
    # Indian
    "Curry", "Butter Chicken", "Tikka Masala", "Korma", "Biryani", "Tandoori", "Daal", "Samosa",
    # Mexican
    "Fajitas", "Tacos", "Burrito", "Quesadilla", "Nachos", "Enchiladas", "Chilli",
    # Middle Eastern
    "Shawarma", "Falafel", "Hummus Plate", "Shakshuka", "Lamb Kofta",
    # Greek/Mediterranean
    "Gyros", "Souvlaki", "Moussaka", "Greek Mezze",
    # British
    "Fish & Chips", "Roast Dinner", "Mac & Cheese", "Burger", "Pie", "Bangers & Mash",
    "Shepherd's Pie", "Jacket Potato", "Casserole",
    # American
    "Wings", "Chicken Nuggets", "BBQ Ribs", "Pulled Pork",
    # Caribbean/African
    "Jerk Chicken", "Jollof Rice", "Curry Goat", "Oxtail",
    # European
    "Schnitzel", "Stroganoff", "Tagine", "Paella", "Cous Cous",
    # Healthy/Bowls
    "Salad", "Poke Bowl", "Buddha Bowl", "Grain Bowl", "Rice Bowl",
    # Other
    "Soup", "Sandwich", "Wrap", "Grilled Chicken", "Rotisserie Chicken",
    # Categories
    "Chinese", "Thai", "Indian", "Japanese", "Mexican", "Mediterranean",
    "Vegetarian", "Healthy", "Kids Menu"
]


class GeminiClient:
    """Client for Gemini API with rate limiting and structured extraction."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-1.5-flash",
        requests_per_minute: int = 15,
        max_retries: int = 3
    ):
        """
        Initialize the Gemini client.
        
        Args:
            api_key: Gemini API key. If None, reads from GEMINI_API_KEY env var.
            model: Model to use (gemini-1.5-flash or gemini-1.5-pro)
            requests_per_minute: Rate limit for API calls
            max_retries: Number of retries on failure
        """
        if not GEMINI_AVAILABLE:
            raise ImportError(
                "google-generativeai package not installed. "
                "Run: pip install google-generativeai"
            )
        
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "No API key provided. Set GEMINI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.model_name = model
        self.requests_per_minute = requests_per_minute
        self.max_retries = max_retries
        self.min_delay = 60.0 / requests_per_minute
        self.last_request_time = 0
        
        # Configure the API
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
        
        logger.info(f"Initialized GeminiClient with model {model}")
    
    def _rate_limit(self):
        """Ensure we don't exceed rate limits."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_delay:
            sleep_time = self.min_delay - elapsed
            logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def _build_extraction_prompt(self, texts: List[str], source_type: str) -> str:
        """Build the prompt for dish mention extraction."""
        
        # Join texts with separators
        numbered_texts = []
        for i, text in enumerate(texts, 1):
            if text and text.strip():
                numbered_texts.append(f"[{i}] {text.strip()}")
        
        texts_block = "\n\n".join(numbered_texts)
        
        dish_types_str = ", ".join(STANDARD_DISH_TYPES[:50])  # First 50 for prompt
        
        prompt = f"""Analyze these customer feedback responses about Dinneroo, a £25 family meal delivery service.

SOURCE TYPE: {source_type}

CUSTOMER RESPONSES:
{texts_block}

---

TASK: Extract ALL mentions of food/dishes from these responses. For each mention, determine:

1. **dish_type**: Map to one of these standard types: {dish_types_str}
   - If a dish doesn't match, use the closest category or create a new descriptive name
   - Normalize brand names: "Nando's" → "Grilled Chicken", "Wagamama" → "Katsu" or "Ramen"

2. **signal_type**: Classify the mention as:
   - "want": Customer WANTS this but can't get it (unmet demand) - phrases like "wish you had", "would love", "looking for", "need more"
   - "complaint": Customer is unhappy with this dish (quality/availability issue)
   - "praise": Customer is happy with this dish

3. **verbatim_quote**: The exact phrase from the text (keep it short, max 100 chars)

4. **confidence**: Your confidence in this extraction (0.0 to 1.0)

5. **source_index**: Which response number [1], [2], etc.

IMPORTANT:
- Focus on "want" signals - these indicate unmet demand
- Don't count generic mentions without sentiment
- Be precise with dish_type mapping

OUTPUT FORMAT (JSON only, no markdown):
{{
  "mentions": [
    {{
      "dish_type": "Fish & Chips",
      "signal_type": "want",
      "verbatim_quote": "wish you had fish and chips",
      "confidence": 0.9,
      "source_index": 1
    }}
  ],
  "summary": {{
    "total_responses": {len(numbered_texts)},
    "responses_with_mentions": 0,
    "want_count": 0,
    "complaint_count": 0,
    "praise_count": 0
  }}
}}

If no food mentions found, return: {{"mentions": [], "summary": {{"total_responses": {len(numbered_texts)}, "responses_with_mentions": 0, "want_count": 0, "complaint_count": 0, "praise_count": 0}}}}
"""
        return prompt
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the JSON response from Gemini."""
        # Clean up response - remove markdown code blocks if present
        text = response_text.strip()
        if text.startswith("```"):
            # Remove markdown code block
            lines = text.split("\n")
            # Remove first line (```json) and last line (```)
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines)
        
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.debug(f"Raw response: {text[:500]}")
            return {"mentions": [], "summary": {}, "error": str(e)}
    
    def extract_dish_mentions(
        self,
        texts: List[str],
        source_type: str = "survey",
        source_ids: Optional[List[str]] = None
    ) -> ExtractionResult:
        """
        Extract dish mentions from a batch of texts.
        
        Args:
            texts: List of text responses to analyze
            source_type: Type of source (survey, transcript, rating)
            source_ids: Optional IDs to track which response each mention came from
        
        Returns:
            ExtractionResult with all extracted mentions
        """
        if not texts:
            return ExtractionResult(
                mentions=[],
                source_count=0,
                api_calls=0,
                tokens_used=0,
                errors=[]
            )
        
        # Filter out empty texts
        valid_texts = [(i, t) for i, t in enumerate(texts) if t and str(t).strip()]
        if not valid_texts:
            return ExtractionResult(
                mentions=[],
                source_count=len(texts),
                api_calls=0,
                tokens_used=0,
                errors=[]
            )
        
        all_mentions = []
        errors = []
        api_calls = 0
        total_tokens = 0
        
        # Build and send prompt
        prompt = self._build_extraction_prompt(
            [t for _, t in valid_texts],
            source_type
        )
        
        for attempt in range(self.max_retries):
            try:
                self._rate_limit()
                
                response = self.model.generate_content(prompt)
                api_calls += 1
                
                # Estimate tokens (rough approximation)
                total_tokens += len(prompt.split()) + len(response.text.split())
                
                # Parse response
                parsed = self._parse_response(response.text)
                
                if "error" in parsed:
                    errors.append(f"Parse error: {parsed['error']}")
                    continue
                
                # Convert to DishMention objects
                for mention_data in parsed.get("mentions", []):
                    source_idx = mention_data.get("source_index", 1) - 1
                    original_idx = valid_texts[source_idx][0] if source_idx < len(valid_texts) else 0
                    
                    mention = DishMention(
                        dish_type=mention_data.get("dish_type", "Unknown"),
                        signal_type=mention_data.get("signal_type", "unknown"),
                        verbatim_quote=mention_data.get("verbatim_quote", ""),
                        confidence=float(mention_data.get("confidence", 0.5)),
                        source_id=source_ids[original_idx] if source_ids and original_idx < len(source_ids) else None
                    )
                    all_mentions.append(mention)
                
                break  # Success, exit retry loop
                
            except Exception as e:
                errors.append(f"API error (attempt {attempt + 1}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                continue
        
        return ExtractionResult(
            mentions=all_mentions,
            source_count=len(texts),
            api_calls=api_calls,
            tokens_used=total_tokens,
            errors=errors
        )
    
    def extract_batch(
        self,
        texts: List[str],
        source_type: str = "survey",
        batch_size: int = 30,
        source_ids: Optional[List[str]] = None
    ) -> ExtractionResult:
        """
        Extract dish mentions from a large batch of texts, processing in chunks.
        
        Args:
            texts: List of all text responses
            source_type: Type of source
            batch_size: Number of texts per API call
            source_ids: Optional IDs for each text
        
        Returns:
            Combined ExtractionResult
        """
        all_mentions = []
        total_api_calls = 0
        total_tokens = 0
        all_errors = []
        
        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_ids = source_ids[i:i + batch_size] if source_ids else None
            
            logger.info(f"Processing batch {i // batch_size + 1} ({i} to {i + len(batch_texts)} of {len(texts)})")
            
            result = self.extract_dish_mentions(
                batch_texts,
                source_type=source_type,
                source_ids=batch_ids
            )
            
            all_mentions.extend(result.mentions)
            total_api_calls += result.api_calls
            total_tokens += result.tokens_used
            all_errors.extend(result.errors)
        
        return ExtractionResult(
            mentions=all_mentions,
            source_count=len(texts),
            api_calls=total_api_calls,
            tokens_used=total_tokens,
            errors=all_errors
        )


def test_client():
    """Test the Gemini client with sample data."""
    try:
        client = GeminiClient()
        
        test_texts = [
            "I wish you had fish and chips, that would be perfect for Friday nights",
            "The curry was great but my kids didn't like it",
            "Would love to see more vegetarian options for my daughter",
            "Pizza was excellent, will order again",
            "Why don't you have Chinese food? We love sweet and sour chicken",
        ]
        
        result = client.extract_dish_mentions(test_texts, source_type="test")
        
        print(f"\nExtracted {len(result.mentions)} mentions from {result.source_count} texts")
        print(f"API calls: {result.api_calls}, Tokens: {result.tokens_used}")
        
        for mention in result.mentions:
            print(f"  - {mention.dish_type} ({mention.signal_type}): '{mention.verbatim_quote}'")
        
        if result.errors:
            print(f"Errors: {result.errors}")
            
    except Exception as e:
        print(f"Test failed: {e}")


if __name__ == "__main__":
    test_client()

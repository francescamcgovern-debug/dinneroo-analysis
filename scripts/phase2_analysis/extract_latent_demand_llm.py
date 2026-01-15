"""
LLM-Based Latent Demand Extraction
==================================
Uses Gemini to semantically extract dish mentions from open-text responses
and customer interview transcripts.

This replaces the keyword-based approach in extract_latent_demand.py with
semantic understanding that can:
- Detect paraphrased requests ("something for the little ones" → Kids Menu)
- Distinguish sentiment (want vs complaint vs praise)
- Extract verbatim quotes for evidence

Usage:
    # Set API key
    export GEMINI_API_KEY="your-key-here"
    
    # Run extraction
    python scripts/phase2_analysis/extract_latent_demand_llm.py

Output:
    - DATA/3_ANALYSIS/latent_demand_scores.csv (updated)
    - DATA/3_ANALYSIS/transcript_mentions.json (new)
    - DATA/3_ANALYSIS/llm_extraction_log.json (audit trail)
"""

import pandas as pd
import numpy as np
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
from typing import List, Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.utils.gemini_client import GeminiClient, DishMention, ExtractionResult, GEMINI_AVAILABLE
from scripts.phase2_analysis.parse_transcripts import TranscriptParser, DOCX_AVAILABLE

# Paths
BASE_PATH = Path(__file__).parent.parent.parent
DATA_PATH = BASE_PATH / "DATA"


class LatentDemandExtractor:
    """Extracts latent demand signals using Gemini LLM."""
    
    def __init__(
        self,
        batch_size: int = 30,
        use_transcripts: bool = True,
        dry_run: bool = False
    ):
        """
        Initialize the extractor.
        
        Args:
            batch_size: Number of texts to process per API call
            use_transcripts: Whether to include transcript analysis
            dry_run: If True, don't make API calls (for testing)
        """
        self.batch_size = batch_size
        self.use_transcripts = use_transcripts
        self.dry_run = dry_run
        
        # Initialize clients
        if not dry_run:
            if not GEMINI_AVAILABLE:
                raise ImportError("google-generativeai not installed")
            self.gemini = GeminiClient()
        else:
            self.gemini = None
        
        # Storage for results
        self.all_mentions: List[DishMention] = []
        self.extraction_log = {
            "started": datetime.now().isoformat(),
            "sources": {},
            "api_calls": 0,
            "tokens_used": 0,
            "errors": []
        }
    
    def load_dropoff_survey(self) -> pd.DataFrame:
        """Load dropoff survey with open-text responses."""
        try:
            df = pd.read_csv(DATA_PATH / "2_ENRICHED" / "DROPOFF_ENRICHED.csv")
            logger.info(f"Loaded dropoff survey: {len(df)} responses")
            return df
        except Exception as e:
            logger.error(f"Could not load dropoff survey: {e}")
            return pd.DataFrame()
    
    def load_post_order_survey(self) -> pd.DataFrame:
        """Load post-order survey with open-text responses."""
        try:
            df = pd.read_csv(DATA_PATH / "2_ENRICHED" / "post_order_enriched_COMPLETE.csv")
            logger.info(f"Loaded post-order survey: {len(df)} responses")
            return df
        except Exception as e:
            logger.error(f"Could not load post-order survey: {e}")
            return pd.DataFrame()
    
    def load_ratings(self) -> pd.DataFrame:
        """Load ratings with comments."""
        try:
            df = pd.read_csv(DATA_PATH / "1_SOURCE" / "snowflake" / "DINNEROO_RATINGS.csv")
            logger.info(f"Loaded ratings: {len(df)} ratings")
            return df
        except Exception as e:
            logger.error(f"Could not load ratings: {e}")
            return pd.DataFrame()
    
    def load_og_survey(self) -> List[Dict]:
        """Load OG survey data with wishlist percentages."""
        try:
            with open(DATA_PATH / "3_ANALYSIS" / "extracted_factors_phase1.json", 'r') as f:
                data = json.load(f)
            og_dishes = data.get('og_survey_dishes', [])
            logger.info(f"Loaded OG survey: {len(og_dishes)} dishes")
            return og_dishes
        except Exception as e:
            logger.error(f"Could not load OG survey: {e}")
            return []
    
    def extract_from_dropoff(self, df: pd.DataFrame) -> ExtractionResult:
        """Extract mentions from dropoff survey open-text fields."""
        text_columns = [
            'What dishes and cuisines would you like to see more of? (please list as many as you can)',
            'What kid-friendly options would you like to see? (please be as descriptive as possible)',
            'What would you like to customise or add? (please describe as much as you can)',
            'What improvements would you suggest (if any) to the "Family Dinneroo" or "Feed the Family for £25" offering?'
        ]
        
        texts = []
        for col in text_columns:
            if col in df.columns:
                for text in df[col].dropna():
                    if isinstance(text, str) and text.strip():
                        texts.append(text.strip())
        
        logger.info(f"Dropoff survey: {len(texts)} open-text responses to analyze")
        
        if self.dry_run or not texts:
            return ExtractionResult(mentions=[], source_count=len(texts), api_calls=0, tokens_used=0, errors=[])
        
        return self.gemini.extract_batch(
            texts,
            source_type="dropoff_survey",
            batch_size=self.batch_size
        )
    
    def extract_from_post_order(self, df: pd.DataFrame) -> ExtractionResult:
        """Extract mentions from post-order survey open-text fields."""
        text_columns = [
            'Overall, how could this dish be improved to suit your needs better?',
            'What further improvements would you suggest (if any)?'
        ]
        
        # Also check for alternative column names
        alt_columns = ['DISH_IMPROVEMENTS', 'SUGGESTED_IMPROVEMENTS']
        
        texts = []
        for col in text_columns + alt_columns:
            if col in df.columns:
                for text in df[col].dropna():
                    if isinstance(text, str) and text.strip():
                        texts.append(text.strip())
        
        logger.info(f"Post-order survey: {len(texts)} open-text responses to analyze")
        
        if self.dry_run or not texts:
            return ExtractionResult(mentions=[], source_count=len(texts), api_calls=0, tokens_used=0, errors=[])
        
        return self.gemini.extract_batch(
            texts,
            source_type="post_order_survey",
            batch_size=self.batch_size
        )
    
    def extract_from_ratings(self, df: pd.DataFrame) -> ExtractionResult:
        """Extract mentions from rating comments."""
        if 'RATING_COMMENT' not in df.columns:
            logger.warning("No RATING_COMMENT column in ratings data")
            return ExtractionResult(mentions=[], source_count=0, api_calls=0, tokens_used=0, errors=[])
        
        texts = []
        for text in df['RATING_COMMENT'].dropna():
            if isinstance(text, str) and text.strip() and len(text.strip()) > 10:
                texts.append(text.strip())
        
        logger.info(f"Ratings: {len(texts)} comments to analyze")
        
        # For ratings, we might have a lot - sample if needed
        max_ratings = 2000
        if len(texts) > max_ratings:
            logger.info(f"Sampling {max_ratings} from {len(texts)} rating comments")
            import random
            random.seed(42)
            texts = random.sample(texts, max_ratings)
        
        if self.dry_run or not texts:
            return ExtractionResult(mentions=[], source_count=len(texts), api_calls=0, tokens_used=0, errors=[])
        
        return self.gemini.extract_batch(
            texts,
            source_type="rating_comment",
            batch_size=self.batch_size
        )
    
    def extract_from_transcripts(self) -> ExtractionResult:
        """Extract mentions from customer interview transcripts."""
        if not self.use_transcripts:
            return ExtractionResult(mentions=[], source_count=0, api_calls=0, tokens_used=0, errors=[])
        
        if not DOCX_AVAILABLE:
            logger.warning("python-docx not installed, skipping transcripts")
            return ExtractionResult(mentions=[], source_count=0, api_calls=0, tokens_used=0, errors=["python-docx not installed"])
        
        try:
            parser = TranscriptParser(filter_to_food=True)
            chunks = parser.get_all_chunks()
            
            logger.info(f"Transcripts: {len(chunks)} chunks to analyze")
            
            if self.dry_run or not chunks:
                return ExtractionResult(mentions=[], source_count=len(chunks), api_calls=0, tokens_used=0, errors=[])
            
            # Extract texts and source IDs
            texts = [chunk.text for chunk in chunks]
            source_ids = [f"{chunk.participant}_cycle{chunk.cycle}_chunk{chunk.chunk_index}" for chunk in chunks]
            
            return self.gemini.extract_batch(
                texts,
                source_type="transcript",
                batch_size=self.batch_size,
                source_ids=source_ids
            )
            
        except Exception as e:
            logger.error(f"Error processing transcripts: {e}")
            return ExtractionResult(mentions=[], source_count=0, api_calls=0, tokens_used=0, errors=[str(e)])
    
    def get_og_wishlist(self, og_data: List[Dict]) -> Dict[str, float]:
        """Extract wishlist percentages from OG survey."""
        wishlist = {}
        
        # Mapping from OG survey dish names to standard types
        mappings = {
            'pizza': 'Pizza',
            'boiled pasta': 'Pasta',
            'baked pasta': 'Baked Pasta',
            'filled pasta': 'Filled Pasta',
            'lasagne': 'Lasagne',
            'risotto': 'Risotto',
            'gnocchi': 'Gnocchi',
            'curry rice': 'Curry',
            'thai curry': 'Thai Curry',
            'katsu curry': 'Katsu',
            'stir fry noodles': 'Noodles',
            'thai noodles': 'Noodles',
            'ramen': 'Ramen',
            'rice bowl fried rice': 'Rice Bowl',
            'fajitas burritos': 'Fajitas',
            'tacos': 'Tacos',
            'chilli': 'Chilli',
            'burger chips': 'Burger',
            'fish chips': 'Fish & Chips',
            'mash pie': 'Pie',
            'pastry pie': 'Pie',
            'meat veg': 'Roast Dinner',
            'sausage mash': 'Bangers & Mash',
            'jacket potato': 'Jacket Potato',
            'casserole stew': 'Casserole',
            'sandwich toastie': 'Sandwich',
            'meat chips': 'Burger',
            'piri': 'Grilled Chicken',
            'cajun chicken': 'Grilled Chicken',
            'jerk chicken': 'Jerk Chicken',
            'chicken': 'Grilled Chicken',
            'soup': 'Soup',
            'salad': 'Salad',
            'cous cous': 'Cous Cous',
            'paella': 'Paella',
            'stroganoff': 'Stroganoff',
            'tagine': 'Tagine',
        }
        
        for item in og_data:
            dish = item.get('dish', '')
            wishlist_pct = item.get('wishlist_pct', '0%')
            
            try:
                pct = float(str(wishlist_pct).replace('%', ''))
            except:
                pct = 0
            
            dish_lower = dish.lower()
            for key, dish_type in mappings.items():
                if key in dish_lower:
                    if dish_type not in wishlist or pct > wishlist[dish_type]:
                        wishlist[dish_type] = pct
                    break
        
        return wishlist
    
    def calculate_scores(
        self,
        og_wishlist: Dict[str, float],
        barrier_signals: Dict[str, int]
    ) -> pd.DataFrame:
        """Calculate final latent demand scores from all extracted mentions."""
        
        # Count mentions by dish type and signal type
        want_counts = Counter()
        complaint_counts = Counter()
        praise_counts = Counter()
        
        source_breakdown = defaultdict(lambda: {"dropoff": 0, "post_order": 0, "ratings": 0, "transcript": 0})
        
        for mention in self.all_mentions:
            dish = mention.dish_type
            
            if mention.signal_type == "want":
                want_counts[dish] += 1
            elif mention.signal_type == "complaint":
                complaint_counts[dish] += 1
            elif mention.signal_type == "praise":
                praise_counts[dish] += 1
            
            # Track source
            if mention.source_id:
                if "dropoff" in mention.source_id.lower():
                    source_breakdown[dish]["dropoff"] += 1
                elif "post_order" in mention.source_id.lower():
                    source_breakdown[dish]["post_order"] += 1
                elif "rating" in mention.source_id.lower():
                    source_breakdown[dish]["ratings"] += 1
                elif "cycle" in mention.source_id.lower():
                    source_breakdown[dish]["transcript"] += 1
        
        # Get all dish types
        all_dishes = set()
        all_dishes.update(want_counts.keys())
        all_dishes.update(og_wishlist.keys())
        all_dishes.update(barrier_signals.keys())
        
        # Also include dishes from existing scores
        try:
            existing = pd.read_csv(DATA_PATH / "3_ANALYSIS" / "latent_demand_scores.csv")
            all_dishes.update(existing['dish_type'].tolist())
        except:
            pass
        
        results = []
        
        for dish in all_dishes:
            want_count = want_counts.get(dish, 0)
            complaint_count = complaint_counts.get(dish, 0)
            praise_count = praise_counts.get(dish, 0)
            wishlist_pct = og_wishlist.get(dish, 0)
            barrier_count = barrier_signals.get(dish, 0)
            
            # Source breakdown
            sources = source_breakdown.get(dish, {"dropoff": 0, "post_order": 0, "ratings": 0, "transcript": 0})
            
            # Calculate weighted score
            # Updated weights: Open-text 40%, Transcripts 25%, OG Wishlist 20%, Barriers 15%
            
            # Normalize scores to 0-5 scale
            open_text_mentions = sources["dropoff"] + sources["post_order"] + sources["ratings"]
            transcript_mentions = sources["transcript"]
            
            # Open-text score (40% weight) - based on want mentions
            open_text_score = min(open_text_mentions / 30, 1.0) * 5
            
            # Transcript score (25% weight)
            transcript_score = min(transcript_mentions / 10, 1.0) * 5
            
            # Wishlist score (20% weight)
            wishlist_score = min(wishlist_pct / 20, 1.0) * 5
            
            # Barrier score (15% weight)
            barrier_score = min(barrier_count / 100, 1.0) * 5
            
            # Weighted combination
            latent_demand_raw = (
                open_text_score * 0.40 +
                transcript_score * 0.25 +
                wishlist_score * 0.20 +
                barrier_score * 0.15
            )
            
            # Final score (1-5)
            final_score = max(1, min(5, round(latent_demand_raw + 1)))
            
            results.append({
                'dish_type': dish,
                'want_mentions': want_count,
                'complaint_mentions': complaint_count,
                'praise_mentions': praise_count,
                'dropoff_requests': sources["dropoff"],
                'post_order_requests': sources["post_order"],
                'ratings_requests': sources["ratings"],
                'transcript_mentions': sources["transcript"],
                'open_text_requests': open_text_mentions,
                'og_wishlist_pct': wishlist_pct,
                'barrier_signals': barrier_count,
                'latent_demand_raw': round(latent_demand_raw, 2),
                'latent_demand_score': final_score
            })
        
        return pd.DataFrame(results)
    
    def analyze_dropoff_barriers(self, df: pd.DataFrame) -> Dict[str, int]:
        """Analyze structured barrier responses for implicit demand."""
        barrier_signals = Counter()
        
        barrier_columns = {
            "There wasn't an option that suited everyone:Which of these best describe why it didn't work for you? (select all that apply)": ['Variety', 'Kids Menu'],
            "The meals didn't look appealing to my children:Which of these best describe why it didn't work for you? (select all that apply)": ['Kids Menu'],
            "I wasn't sure if the food fitted dietary needs:Which of these best describe why it didn't work for you? (select all that apply)": ['Vegetarian', 'Healthy'],
        }
        
        for col, dish_types in barrier_columns.items():
            if col in df.columns:
                count = df[col].notna().sum()
                for dish_type in dish_types:
                    barrier_signals[dish_type] += count
        
        return dict(barrier_signals)
    
    def save_transcript_mentions(self):
        """Save transcript mentions with quotes for evidence."""
        transcript_mentions = [
            {
                "dish_type": m.dish_type,
                "signal_type": m.signal_type,
                "quote": m.verbatim_quote,
                "confidence": m.confidence,
                "source": m.source_id
            }
            for m in self.all_mentions
            if m.source_id and "cycle" in m.source_id.lower()
        ]
        
        output = {
            "generated": datetime.now().isoformat(),
            "total_mentions": len(transcript_mentions),
            "mentions": transcript_mentions
        }
        
        output_path = DATA_PATH / "3_ANALYSIS" / "transcript_mentions.json"
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)
        
        logger.info(f"Saved {len(transcript_mentions)} transcript mentions to {output_path}")
    
    def save_extraction_log(self):
        """Save the extraction log for audit purposes."""
        self.extraction_log["completed"] = datetime.now().isoformat()
        
        output_path = DATA_PATH / "3_ANALYSIS" / "llm_extraction_log.json"
        with open(output_path, 'w') as f:
            json.dump(self.extraction_log, f, indent=2)
        
        logger.info(f"Saved extraction log to {output_path}")
    
    def run(self) -> pd.DataFrame:
        """Run the full extraction pipeline."""
        print("=" * 60)
        print("LLM-BASED LATENT DEMAND EXTRACTION")
        print("=" * 60)
        
        # Load data sources
        print("\n1. Loading data sources...")
        dropoff_df = self.load_dropoff_survey()
        post_order_df = self.load_post_order_survey()
        ratings_df = self.load_ratings()
        og_data = self.load_og_survey()
        
        # Extract from each source
        print("\n2. Extracting dish mentions with Gemini...")
        
        # Dropoff survey
        print("\n   Processing dropoff survey...")
        dropoff_result = self.extract_from_dropoff(dropoff_df)
        self.all_mentions.extend(dropoff_result.mentions)
        self.extraction_log["sources"]["dropoff"] = {
            "responses": dropoff_result.source_count,
            "mentions": len(dropoff_result.mentions),
            "api_calls": dropoff_result.api_calls
        }
        self.extraction_log["api_calls"] += dropoff_result.api_calls
        self.extraction_log["tokens_used"] += dropoff_result.tokens_used
        print(f"   → Extracted {len(dropoff_result.mentions)} mentions")
        
        # Post-order survey
        print("\n   Processing post-order survey...")
        post_order_result = self.extract_from_post_order(post_order_df)
        self.all_mentions.extend(post_order_result.mentions)
        self.extraction_log["sources"]["post_order"] = {
            "responses": post_order_result.source_count,
            "mentions": len(post_order_result.mentions),
            "api_calls": post_order_result.api_calls
        }
        self.extraction_log["api_calls"] += post_order_result.api_calls
        self.extraction_log["tokens_used"] += post_order_result.tokens_used
        print(f"   → Extracted {len(post_order_result.mentions)} mentions")
        
        # Ratings
        print("\n   Processing rating comments...")
        ratings_result = self.extract_from_ratings(ratings_df)
        self.all_mentions.extend(ratings_result.mentions)
        self.extraction_log["sources"]["ratings"] = {
            "responses": ratings_result.source_count,
            "mentions": len(ratings_result.mentions),
            "api_calls": ratings_result.api_calls
        }
        self.extraction_log["api_calls"] += ratings_result.api_calls
        self.extraction_log["tokens_used"] += ratings_result.tokens_used
        print(f"   → Extracted {len(ratings_result.mentions)} mentions")
        
        # Transcripts
        if self.use_transcripts:
            print("\n   Processing interview transcripts...")
            transcript_result = self.extract_from_transcripts()
            self.all_mentions.extend(transcript_result.mentions)
            self.extraction_log["sources"]["transcripts"] = {
                "chunks": transcript_result.source_count,
                "mentions": len(transcript_result.mentions),
                "api_calls": transcript_result.api_calls
            }
            self.extraction_log["api_calls"] += transcript_result.api_calls
            self.extraction_log["tokens_used"] += transcript_result.tokens_used
            print(f"   → Extracted {len(transcript_result.mentions)} mentions")
        
        # Get OG wishlist and barriers
        print("\n3. Processing structured data...")
        og_wishlist = self.get_og_wishlist(og_data)
        barrier_signals = self.analyze_dropoff_barriers(dropoff_df) if len(dropoff_df) > 0 else {}
        
        # Calculate final scores
        print("\n4. Calculating latent demand scores...")
        results_df = self.calculate_scores(og_wishlist, barrier_signals)
        results_df = results_df.sort_values('latent_demand_score', ascending=False)
        
        # Save outputs
        print("\n5. Saving outputs...")
        
        # Main scores file
        output_path = DATA_PATH / "3_ANALYSIS" / "latent_demand_scores.csv"
        results_df.to_csv(output_path, index=False)
        print(f"   Saved scores to: {output_path}")
        
        # Transcript mentions
        self.save_transcript_mentions()
        
        # Extraction log
        self.save_extraction_log()
        
        # Print summary
        print("\n" + "=" * 60)
        print("EXTRACTION SUMMARY")
        print("=" * 60)
        print(f"Total mentions extracted: {len(self.all_mentions)}")
        print(f"API calls made: {self.extraction_log['api_calls']}")
        print(f"Estimated tokens: {self.extraction_log['tokens_used']:,}")
        print(f"Dish types scored: {len(results_df)}")
        
        # Top dishes by latent demand
        print("\n" + "=" * 60)
        print("TOP 15 DISHES BY LATENT DEMAND (LLM-EXTRACTED)")
        print("=" * 60)
        top_cols = ['dish_type', 'want_mentions', 'transcript_mentions', 'og_wishlist_pct', 'latent_demand_score']
        print(results_df[top_cols].head(15).to_string(index=False))
        
        print("\n✓ LLM extraction complete!")
        
        return results_df


def main():
    """Run the LLM-based latent demand extraction."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract latent demand using Gemini LLM')
    parser.add_argument('--dry-run', action='store_true', help='Run without making API calls')
    parser.add_argument('--no-transcripts', action='store_true', help='Skip transcript processing')
    parser.add_argument('--batch-size', type=int, default=30, help='Texts per API call')
    
    args = parser.parse_args()
    
    try:
        extractor = LatentDemandExtractor(
            batch_size=args.batch_size,
            use_transcripts=not args.no_transcripts,
            dry_run=args.dry_run
        )
        
        results = extractor.run()
        
    except ValueError as e:
        if "API key" in str(e):
            print("\n" + "=" * 60)
            print("ERROR: Gemini API key not set")
            print("=" * 60)
            print("Set the GEMINI_API_KEY environment variable:")
            print("  export GEMINI_API_KEY='your-key-here'")
            print("\nOr run with --dry-run to test without API calls")
            sys.exit(1)
        raise
    except ImportError as e:
        print(f"\nMissing dependency: {e}")
        print("Run: pip install google-generativeai python-docx")
        sys.exit(1)


if __name__ == "__main__":
    main()

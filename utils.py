"""Utility functions for Transfermarkt Analytics"""
import logging
import re
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

def parse_market_value(value: Any) -> float:
    """
    Parse market value from various string formats to float (millions).
    
    Examples:
        "€50.5M" -> 50.5
        "€1.2bn" -> 1200
        "0" -> 0.0
    
    Args:
        value: Market value string or number
        
    Returns:
        Float value in millions
    """
    if not value or value in ["None", "0", "-", "", "N/A"]:
        return 0.0
    
    try:
        # Convert to string if not already
        value_str = str(value).strip()
        
        # Extract numbers and decimal points
        numbers = re.sub(r'[^\d.]', '', value_str)
        
        if not numbers:
            return 0.0
        
        val = float(numbers)
        
        # Convert billions to millions
        if 'bn' in value_str.lower():
            val *= 1000.0
        
        return val
    except Exception as e:
        logger.error(f"Error parsing market value '{value}': {e}")
        return 0.0

def format_market_value(value: Optional[float], currency: str = "€") -> str:
    """
    Format market value for display.
    
    Args:
        value: Market value in millions
        currency: Currency symbol
        
    Returns:
        Formatted string
    """
    if value is None or value == 0:
        return "N/A"
    
    if value >= 1000:
        return f"{currency}{value/1000:.1f}B"
    else:
        return f"{currency}{value:.1f}M"

def extract_id_from_url(url: str, id_pattern: str) -> Optional[str]:
    """
    Extract ID from URL using pattern.
    
    Args:
        url: URL string
        id_pattern: Pattern to match (e.g., "verein/", "spieler/")
        
    Returns:
        Extracted ID or None
    """
    try:
        if id_pattern not in url:
            return None
        
        parts = url.split(id_pattern)
        if len(parts) < 2:
            return None
        
        id_part = parts[1].split('/')[0]
        return id_part if id_part else None
    except Exception as e:
        logger.error(f"Error extracting ID from URL: {e}")
        return None

def clean_text(text: str) -> str:
    """
    Clean and normalize text.
    
    Args:
        text: Raw text
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    return text.strip()

def get_age_from_birthdate(birthdate_str: str) -> Optional[int]:
    """
    Calculate age from birthdate string.
    
    Args:
        birthdate_str: Date string (YYYY-MM-DD format)
        
    Returns:
        Age as integer or None
    """
    try:
        birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d")
        today = datetime.now()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        return age
    except Exception as e:
        logger.error(f"Error calculating age: {e}")
        return None

def match_score_to_goals(score_str: str) -> tuple[Optional[int], Optional[int]]:
    """
    Parse match score string to home and away goals.
    
    Args:
        score_str: Score string (e.g., "2:1", "-:-")
        
    Returns:
        Tuple of (home_goals, away_goals) or (None, None)
    """
    try:
        if not score_str or score_str == "-:-":
            return None, None
        
        parts = score_str.split(':')
        if len(parts) != 2:
            return None, None
        
        home = int(parts[0].strip()) if parts[0].strip().isdigit() else None
        away = int(parts[1].strip()) if parts[1].strip().isdigit() else None
        
        return home, away
    except Exception as e:
        logger.error(f"Error parsing score: {e}")
        return None, None

def categorize_position(position: str) -> Optional[str]:
    """
    Categorize player position to standard abbreviations.
    
    Args:
        position: Position string
        
    Returns:
        Standardized position (GK, DEF, MID, FWD) or None
    """
    if not position:
        return None
    
    pos_lower = position.lower()
    
    if 'gk' in pos_lower or 'keeper' in pos_lower or 'goalkeeper' in pos_lower:
        return 'GK'
    elif 'def' in pos_lower or 'cb' in pos_lower or 'lb' in pos_lower or 'rb' in pos_lower or 'back' in pos_lower:
        return 'DEF'
    elif 'mid' in pos_lower or 'cm' in pos_lower or 'lm' in pos_lower or 'rm' in pos_lower or 'cdm' in pos_lower:
        return 'MID'
    elif 'fwd' in pos_lower or 'st' in pos_lower or 'cf' in pos_lower or 'striker' in pos_lower or 'forward' in pos_lower:
        return 'FWD'
    
    return None

def get_match_status(home_goals: Optional[int], away_goals: Optional[int]) -> str:
    """
    Determine match status from score.
    
    Args:
        home_goals: Home team goals
        away_goals: Away team goals
        
    Returns:
        Match status string
    """
    if home_goals is None or away_goals is None:
        return 'Scheduled'
    return 'Finished'

def calculate_possession_difference(home_poss: Optional[float], away_poss: Optional[float]) -> Optional[float]:
    """
    Calculate possession difference.
    
    Args:
        home_poss: Home team possession percentage
        away_poss: Away team possession percentage
        
    Returns:
        Difference or None
    """
    if home_poss is None or away_poss is None:
        return None
    
    return home_poss - away_poss

def get_performance_rating(rating: Optional[float]) -> str:
    """
    Convert numerical rating to performance category.
    
    Args:
        rating: Rating from 0-10 scale
        
    Returns:
        Performance category
    """
    if rating is None:
        return "N/A"
    
    if rating >= 8.5:
        return "Outstanding"
    elif rating >= 7.5:
        return "Excellent"
    elif rating >= 6.5:
        return "Good"
    elif rating >= 5.5:
        return "Average"
    elif rating >= 4.5:
        return "Below Average"
    else:
        return "Poor"

class DataCache:
    """Simple in-memory cache for reducing database queries"""
    
    def __init__(self, ttl_seconds: int = 300):
        self.cache: Dict[str, tuple[Any, float]] = {}
        self.ttl = ttl_seconds
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key not in self.cache:
            return None
        
        value, timestamp = self.cache[key]
        if datetime.now().timestamp() - timestamp > self.ttl:
            del self.cache[key]
            return None
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache"""
        self.cache[key] = (value, datetime.now().timestamp())
    
    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()

# Global cache instance
_global_cache = DataCache()

def cache_get(key: str) -> Optional[Any]:
    """Get from global cache"""
    return _global_cache.get(key)

def cache_set(key: str, value: Any) -> None:
    """Set in global cache"""
    _global_cache.set(key, value)

def cache_clear() -> None:
    """Clear global cache"""
    _global_cache.clear()

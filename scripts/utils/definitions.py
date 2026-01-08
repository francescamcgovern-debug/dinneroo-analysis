"""
CANONICAL DEFINITIONS - Single Source of Truth
==============================================

All agents MUST import from this module to ensure consistency.
DO NOT define cuisine/dish/zone mappings elsewhere.

Version: 1.0 (Jan 2026)
"""

# =============================================================================
# CORE 7 CUISINES
# =============================================================================

CORE_7 = ['Asian', 'Italian', 'Indian', 'Healthy', 'Mexican', 'Middle Eastern', 'British']

# Required for MVP (5 of these 5)
REQUIRED_FOR_MVP = ['Asian', 'Italian', 'Indian', 'Healthy', 'Mexican']

# Optional cuisines (not required for MVP)
OPTIONAL_CUISINES = ['Middle Eastern', 'British']

# =============================================================================
# SUB-CUISINE TO CORE 7 MAPPING
# =============================================================================
# Maps granular cuisines (from Snowflake/Deliveroo tags) to Core 7

SUB_TO_CORE = {
    # Asian sub-cuisines
    'japanese': 'Asian',
    'thai': 'Asian', 
    'vietnamese': 'Asian',
    'chinese': 'Asian',
    'korean': 'Asian',
    'pan_asian': 'Asian',
    'pan asian': 'Asian',
    'asian': 'Asian',
    'asian fusion': 'Asian',
    
    # Italian (direct mapping)
    'italian': 'Italian',
    'pizza': 'Italian',  # Deliveroo tag
    'pasta': 'Italian',  # Deliveroo tag
    
    # Indian (direct mapping)
    'indian': 'Indian',
    'curry': 'Indian',  # Deliveroo tag
    
    # Healthy sub-cuisines
    'healthy': 'Healthy',
    'salads': 'Healthy',
    'sandwiches': 'Healthy',
    'poke': 'Healthy',
    'healthy/fresh': 'Healthy',
    
    # Mexican sub-cuisines
    'mexican': 'Mexican',
    'tex_mex': 'Mexican',
    'tex-mex': 'Mexican',
    'latin american': 'Mexican',
    'tacos': 'Mexican',  # Deliveroo tag
    'burritos': 'Mexican',  # Deliveroo tag
    
    # Middle Eastern sub-cuisines
    'middle eastern': 'Middle Eastern',
    'lebanese': 'Middle Eastern',
    'turkish': 'Middle Eastern',
    'mediterranean': 'Middle Eastern',
    'greek': 'Middle Eastern',
    'shawarma': 'Middle Eastern',  # Deliveroo tag
    
    # British (direct mapping)
    'british': 'British',
    'roasteries': 'British',  # Deliveroo tag
    
    # American - maps to Other (not Core 7)
    'american': 'Other',
    'burgers': 'Other',
    
    # Global/Other - needs dish-level mapping
    'global': 'Other',
}

# =============================================================================
# DISH TO SUB-CUISINE MAPPING
# =============================================================================
# Maps dish types to their sub-cuisine (for granular analysis)
# Source: Anna's Item Categorisation

DISH_TO_SUB = {
    # Japanese dishes
    'Katsu': 'Japanese',
    'Sushi': 'Japanese',
    'Ramen': 'Japanese',
    'Teriyaki': 'Japanese',
    'Gyoza': 'Japanese',
    
    # Vietnamese dishes
    'Pho': 'Vietnamese',
    
    # Thai dishes
    'Pad Thai': 'Thai',
    'Thai Curry': 'Thai',
    'Satay': 'Thai',
    
    # Chinese dishes
    'Fried Rice': 'Chinese',
    'Sweet & Sour Chicken': 'Chinese',
    'Sweet & Sour': 'Chinese',
    'Dim Sum': 'Chinese',
    'Spring Rolls': 'Chinese',
    'Chinese Family Meal': 'Chinese',
    'Stir Fry': 'Chinese',
    
    # Korean dishes
    'Korean Fried Chicken': 'Korean',
    'Bibimbap': 'Korean',
    
    # Pan-Asian (multi-origin)
    'Noodles': 'Pan-Asian',
    'Rice Bowl': 'Pan-Asian',
    
    # Indian dishes
    'Curry': 'Indian',
    'Biryani': 'Indian',
    'Butter Chicken': 'Indian',
    'Tikka Masala': 'Indian',
    'Daal': 'Indian',
    'Samosa': 'Indian',
    
    # Italian dishes
    'Pasta': 'Italian',
    'Lasagne': 'Italian',
    'Pizza': 'Italian',
    
    # Mexican dishes
    'Fajitas': 'Mexican',
    'Veggie Fajitas': 'Mexican',
    'Tacos': 'Mexican',
    'Quesadilla': 'Mexican',
    'Burrito': 'Mexican',
    'Chilli': 'Mexican',
    
    # Middle Eastern dishes
    'Shawarma': 'Middle Eastern',
    'Falafel': 'Middle Eastern',
    'Greek Mezze': 'Greek',
    'Souvlaki': 'Greek',
    
    # Healthy dishes
    'Bowl': 'Healthy',
    'Salad': 'Healthy',
    'Grain Bowl': 'Healthy',
    'Poke Bowl': 'Healthy',
    'Buddha Bowl': 'Healthy',
    
    # British dishes
    'Roast Dinner': 'British',
    'Shepherd\'s Pie': 'British',
    'Chicken Pie': 'British',
    'Cottage Pie': 'British',
    'Fish & Chips': 'British',
    'Pie': 'British',
    
    # Global/Other dishes
    'Mac & Cheese': 'American',
    'Burger': 'American',
    'Grilled Chicken': 'American',
    'Grilled Chicken with Sides': 'American',
    'Chicken Nuggets': 'American',
    'Wings': 'American',
    'Halloumi Wrap': 'Mediterranean',
    'Wrap': 'Global',
    'Soup': 'Global',
}

# =============================================================================
# DISH TO CORE 7 MAPPING
# =============================================================================
# Direct mapping from dish type to Core 7 cuisine

DISH_TO_CORE = {
    # Asian dishes
    'Katsu': 'Asian',
    'Sushi': 'Asian',
    'Ramen': 'Asian',
    'Teriyaki': 'Asian',
    'Gyoza': 'Asian',
    'Pho': 'Asian',
    'Pad Thai': 'Asian',
    'Thai Curry': 'Asian',
    'Satay': 'Asian',
    'Fried Rice': 'Asian',
    'Sweet & Sour Chicken': 'Asian',
    'Sweet & Sour': 'Asian',
    'Dim Sum': 'Asian',
    'Spring Rolls': 'Asian',
    'Chinese Family Meal': 'Asian',
    'Stir Fry': 'Asian',
    'Korean Fried Chicken': 'Asian',
    'Bibimbap': 'Asian',
    'Noodles': 'Asian',
    'Rice Bowl': 'Asian',
    
    # Indian dishes
    'Curry': 'Indian',
    'Biryani': 'Indian',
    'Butter Chicken': 'Indian',
    'Tikka Masala': 'Indian',
    'Daal': 'Indian',
    'Samosa': 'Indian',
    
    # Italian dishes
    'Pasta': 'Italian',
    'Lasagne': 'Italian',
    'Pizza': 'Italian',
    
    # Mexican dishes
    'Fajitas': 'Mexican',
    'Veggie Fajitas': 'Mexican',
    'Tacos': 'Mexican',
    'Quesadilla': 'Mexican',
    'Burrito': 'Mexican',
    'Chilli': 'Mexican',
    
    # Middle Eastern dishes
    'Shawarma': 'Middle Eastern',
    'Falafel': 'Middle Eastern',
    'Greek Mezze': 'Middle Eastern',
    'Souvlaki': 'Middle Eastern',
    'Halloumi Wrap': 'Middle Eastern',
    
    # Healthy dishes
    'Bowl': 'Healthy',
    'Salad': 'Healthy',
    'Grain Bowl': 'Healthy',
    'Poke Bowl': 'Healthy',
    'Buddha Bowl': 'Healthy',
    
    # British dishes
    'Roast Dinner': 'British',
    'Shepherd\'s Pie': 'British',
    'Chicken Pie': 'British',
    'Cottage Pie': 'British',
    'Fish & Chips': 'British',
    'Pie': 'British',
    
    # Other (not Core 7)
    'Mac & Cheese': 'Other',
    'Burger': 'Other',
    'Grilled Chicken': 'Other',
    'Grilled Chicken with Sides': 'Other',
    'Chicken Nuggets': 'Other',
    'Wings': 'Other',
    'Wrap': 'Other',
    'Soup': 'Other',
}

# =============================================================================
# MVP STATUS TIERS
# =============================================================================

MVP_STATUS_TIERS = {
    'MVP Ready': {'min_cuisines': 5, 'description': 'North star - full family offering'},
    'Near MVP': {'min_cuisines': 4, 'description': 'Almost there - 1 cuisine gap'},
    'Progressing': {'min_cuisines': 3, 'description': 'Data inflection point - meaningful variety'},
    'Developing': {'min_cuisines': 1, 'description': 'Early stage - limited options'},
    'Not Started': {'min_cuisines': 0, 'description': 'No Dinneroo partners yet'},
    'Supply Only': {'min_cuisines': 0, 'description': 'Has partners but no orders'},
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def normalize_cuisine(cuisine: str) -> str:
    """Normalize cuisine string for consistent lookups."""
    if not cuisine or str(cuisine).lower() in ['nan', 'none', '']:
        return None
    return str(cuisine).lower().strip()


def get_core_7(cuisine_or_sub: str) -> str:
    """
    Map any cuisine/sub-cuisine to Core 7 category.
    
    Args:
        cuisine_or_sub: A cuisine name (e.g., 'Japanese', 'thai', 'Asian')
        
    Returns:
        Core 7 cuisine name or 'Other' if not mappable
        
    Examples:
        >>> get_core_7('Japanese')
        'Asian'
        >>> get_core_7('Italian')
        'Italian'
        >>> get_core_7('Burgers')
        'Other'
    """
    if not cuisine_or_sub:
        return None
        
    normalized = normalize_cuisine(cuisine_or_sub)
    if not normalized:
        return None
    
    # Check if already a Core 7 cuisine
    for core in CORE_7:
        if normalized == core.lower():
            return core
    
    # Look up in sub-to-core mapping
    return SUB_TO_CORE.get(normalized, 'Other')


def get_sub_cuisine(dish_type: str) -> str:
    """
    Get the sub-cuisine for a dish type.
    
    Args:
        dish_type: A dish name (e.g., 'Katsu', 'Pho', 'Biryani')
        
    Returns:
        Sub-cuisine name or None if not found
        
    Examples:
        >>> get_sub_cuisine('Katsu')
        'Japanese'
        >>> get_sub_cuisine('Pho')
        'Vietnamese'
    """
    if not dish_type:
        return None
    return DISH_TO_SUB.get(dish_type)


def get_core_7_for_dish(dish_type: str) -> str:
    """
    Get the Core 7 cuisine for a dish type.
    
    Args:
        dish_type: A dish name (e.g., 'Katsu', 'Pho', 'Biryani')
        
    Returns:
        Core 7 cuisine name or 'Other' if not found
        
    Examples:
        >>> get_core_7_for_dish('Katsu')
        'Asian'
        >>> get_core_7_for_dish('Biryani')
        'Indian'
    """
    if not dish_type:
        return None
    return DISH_TO_CORE.get(dish_type, 'Other')


def get_mvp_status(core_7_count: int, has_orders: bool = True) -> str:
    """
    Calculate tiered MVP status based on Core 7 cuisine count.
    
    Args:
        core_7_count: Number of Core 7 cuisines with dishes in the zone (0-7)
        has_orders: Whether the zone has any Dinneroo orders
        
    Returns:
        MVP status string: 'MVP Ready', 'Near MVP', 'Progressing', 'Developing',
                          'Supply Only', or 'Not Started'
        
    Examples:
        >>> get_mvp_status(7, True)
        'MVP Ready'
        >>> get_mvp_status(4, True)
        'Near MVP'
        >>> get_mvp_status(3, True)
        'Progressing'
        >>> get_mvp_status(2, False)
        'Supply Only'
    """
    if not has_orders:
        return "Supply Only" if core_7_count > 0 else "Not Started"
    
    if core_7_count >= 5:
        return "MVP Ready"      # North star target
    elif core_7_count == 4:
        return "Near MVP"       # 1 cuisine away
    elif core_7_count >= 3:
        return "Progressing"    # Data inflection point
    elif core_7_count >= 1:
        return "Developing"
    else:
        return "Not Started"


def get_cuisine_pass(core_7_count: int) -> bool:
    """
    Check if zone passes cuisine threshold for MVP.
    
    Args:
        core_7_count: Number of Core 7 cuisines with dishes
        
    Returns:
        True if zone has 5+ Core 7 cuisines
    """
    return core_7_count >= 5


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_cuisine(cuisine: str) -> dict:
    """
    Validate a cuisine value and return mapping info.
    
    Returns:
        dict with 'valid', 'core_7', 'sub_cuisine', 'warning' keys
    """
    result = {
        'valid': False,
        'core_7': None,
        'sub_cuisine': None,
        'warning': None
    }
    
    if not cuisine:
        result['warning'] = 'Empty cuisine value'
        return result
        
    normalized = normalize_cuisine(cuisine)
    core_7 = get_core_7(cuisine)
    
    if core_7 and core_7 != 'Other':
        result['valid'] = True
        result['core_7'] = core_7
        # Check if it's a sub-cuisine
        if normalized not in [c.lower() for c in CORE_7]:
            result['sub_cuisine'] = cuisine.title()
    elif core_7 == 'Other':
        result['valid'] = True
        result['core_7'] = 'Other'
        result['warning'] = f"'{cuisine}' maps to 'Other' (not a Core 7 cuisine)"
    else:
        result['warning'] = f"Unknown cuisine: '{cuisine}'"
    
    return result


def validate_dish(dish_type: str) -> dict:
    """
    Validate a dish type and return mapping info.
    
    Returns:
        dict with 'valid', 'core_7', 'sub_cuisine', 'warning' keys
    """
    result = {
        'valid': False,
        'core_7': None,
        'sub_cuisine': None,
        'warning': None
    }
    
    if not dish_type:
        result['warning'] = 'Empty dish type'
        return result
    
    sub = get_sub_cuisine(dish_type)
    core = get_core_7_for_dish(dish_type)
    
    if core and core != 'Other':
        result['valid'] = True
        result['core_7'] = core
        result['sub_cuisine'] = sub
    elif core == 'Other':
        result['valid'] = True
        result['core_7'] = 'Other'
        result['sub_cuisine'] = sub
        result['warning'] = f"'{dish_type}' maps to 'Other' (not a Core 7 dish)"
    else:
        result['warning'] = f"Unknown dish type: '{dish_type}'"
    
    return result


# =============================================================================
# EXPORT ALL
# =============================================================================

__all__ = [
    # Constants
    'CORE_7',
    'REQUIRED_FOR_MVP',
    'OPTIONAL_CUISINES',
    'SUB_TO_CORE',
    'DISH_TO_SUB',
    'DISH_TO_CORE',
    'MVP_STATUS_TIERS',
    # Functions
    'get_core_7',
    'get_sub_cuisine',
    'get_core_7_for_dish',
    'get_mvp_status',
    'get_cuisine_pass',
    'normalize_cuisine',
    'validate_cuisine',
    'validate_dish',
]



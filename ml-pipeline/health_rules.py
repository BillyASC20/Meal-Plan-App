"""
Health risk rules and keyword matching for ingredient classification.
Maps ingredient names to health risk categories.
"""

# Keywords indicating high cholesterol risk
CHOLESTEROL_KEYWORDS = [
    'egg', 'yolk', 'liver', 'organ', 'kidney', 'brain', 'shrimp', 'lobster',
    'cheese', 'butter', 'cream', 'whole milk', 'lard', 'tallow', 'ghee'
]

# Keywords for heart disease risk (high saturated fat, sodium)
HEART_DISEASE_KEYWORDS = [
    'bacon', 'sausage', 'salami', 'pepperoni', 'hot dog', 'processed meat',
    'red meat', 'beef', 'pork', 'lamb', 'butter', 'lard', 'tallow', 'palm oil',
    'coconut oil', 'cheese', 'cream', 'fried', 'fast food', 'canned', 'pickled',
    'smoked', 'cured', 'salted', 'sodium'
]

# Keywords for diabetes risk (high sugar, refined carbs)
DIABETES_KEYWORDS = [
    'sugar', 'syrup', 'honey', 'candy', 'chocolate', 'sweet', 'dessert',
    'cake', 'cookie', 'pastry', 'donut', 'soda', 'juice', 'refined flour',
    'white bread', 'white rice', 'pasta', 'sweetened', 'frosting', 'glaze'
]

# Keywords for hypertension/high blood pressure (high sodium)
HYPERTENSION_KEYWORDS = [
    'salt', 'sodium', 'soy sauce', 'fish sauce', 'bouillon', 'broth',
    'canned', 'pickled', 'cured', 'smoked', 'processed', 'frozen meal',
    'instant', 'package', 'seasoning mix', 'salted', 'brine'
]

# Keywords for obesity risk (high calorie density, unhealthy fats)
OBESITY_KEYWORDS = [
    'fried', 'deep fried', 'battered', 'breaded', 'butter', 'oil', 'lard',
    'mayonnaise', 'cream', 'cheese sauce', 'gravy', 'fast food', 'junk food',
    'chips', 'fries', 'nugget', 'ice cream', 'milkshake', 'dessert'
]

# Healthy ingredients (low risk)
HEALTHY_KEYWORDS = [
    'vegetable', 'fruit', 'leafy', 'spinach', 'kale', 'broccoli', 'carrot',
    'apple', 'banana', 'berry', 'citrus', 'whole grain', 'oat', 'quinoa',
    'lentil', 'bean', 'legume', 'lean', 'fish', 'salmon', 'tuna', 'nuts',
    'seeds', 'olive oil', 'avocado', 'yogurt nonfat', 'skim milk'
]


def classify_ingredient_health_risk(ingredient_name: str) -> dict:
    """
    Classify an ingredient based on health risk keywords.
    
    Args:
        ingredient_name: Name of the ingredient (lowercase)
    
    Returns:
        Dictionary with risk flags:
        {
            'high_cholesterol': bool,
            'heart_disease': bool,
            'diabetes': bool,
            'hypertension': bool,
            'obesity': bool,
            'healthy': bool
        }
    """
    name_lower = ingredient_name.lower()
    
    risks = {
        'high_cholesterol': any(kw in name_lower for kw in CHOLESTEROL_KEYWORDS),
        'heart_disease': any(kw in name_lower for kw in HEART_DISEASE_KEYWORDS),
        'diabetes': any(kw in name_lower for kw in DIABETES_KEYWORDS),
        'hypertension': any(kw in name_lower for kw in HYPERTENSION_KEYWORDS),
        'obesity': any(kw in name_lower for kw in OBESITY_KEYWORDS),
        'healthy': any(kw in name_lower for kw in HEALTHY_KEYWORDS)
    }
    
    return risks


def get_risk_level(risks: dict) -> str:
    """
    Determine overall risk level based on individual risk flags.
    
    Args:
        risks: Dictionary of risk flags from classify_ingredient_health_risk
    
    Returns:
        Risk level: 'low', 'moderate', 'high', 'very_high'
    """
    # Count number of risk factors
    risk_count = sum([
        risks['high_cholesterol'],
        risks['heart_disease'],
        risks['diabetes'],
        risks['hypertension'],
        risks['obesity']
    ])
    
    # If marked as healthy, lower the risk
    if risks['healthy']:
        return 'low'
    
    # Classify based on number of risk factors
    if risk_count == 0:
        return 'low'
    elif risk_count == 1:
        return 'moderate'
    elif risk_count == 2:
        return 'high'
    else:  # 3 or more
        return 'very_high'


def analyze_recipe_risks(ingredients: list) -> dict:
    """
    Analyze health risks for a complete recipe.
    
    Args:
        ingredients: List of ingredient names
    
    Returns:
        Dictionary with aggregated risk analysis
    """
    all_risks = {
        'high_cholesterol': 0,
        'heart_disease': 0,
        'diabetes': 0,
        'hypertension': 0,
        'obesity': 0,
        'healthy': 0
    }
    
    risk_levels = []
    
    for ingredient in ingredients:
        risks = classify_ingredient_health_risk(ingredient)
        risk_level = get_risk_level(risks)
        risk_levels.append(risk_level)
        
        # Aggregate risk counts
        for key in all_risks:
            if risks[key]:
                all_risks[key] += 1
    
    # Calculate percentages
    total_ingredients = len(ingredients)
    risk_percentages = {
        key: (count / total_ingredients * 100) if total_ingredients > 0 else 0
        for key, count in all_risks.items()
    }
    
    # Determine overall recipe risk
    very_high_count = risk_levels.count('very_high')
    high_count = risk_levels.count('high')
    
    if very_high_count > 0 or high_count > len(ingredients) * 0.3:
        overall_risk = 'high'
    elif high_count > 0 or risk_levels.count('moderate') > len(ingredients) * 0.5:
        overall_risk = 'moderate'
    else:
        overall_risk = 'low'
    
    return {
        'overall_risk': overall_risk,
        'risk_percentages': risk_percentages,
        'ingredient_count': total_ingredients,
        'high_risk_ingredients': sum(1 for rl in risk_levels if rl in ['high', 'very_high']),
        'warnings': generate_warnings(risk_percentages)
    }


def generate_warnings(risk_percentages: dict) -> list:
    """Generate human-readable warnings based on risk percentages."""
    warnings = []
    
    if risk_percentages['high_cholesterol'] > 20:
        warnings.append("⚠️ High cholesterol ingredients detected - consider moderation")
    
    if risk_percentages['heart_disease'] > 30:
        warnings.append("❤️ Multiple heart disease risk factors - limit saturated fats and sodium")
    
    if risk_percentages['diabetes'] > 25:
        warnings.append("🩺 High sugar content - may affect blood glucose levels")
    
    if risk_percentages['hypertension'] > 20:
        warnings.append("🧂 High sodium content - not recommended for high blood pressure")
    
    if risk_percentages['obesity'] > 30:
        warnings.append("⚖️ High calorie density - portion control recommended")
    
    if risk_percentages['healthy'] > 50:
        warnings.append("✅ Recipe contains many healthy ingredients!")
    
    return warnings

"""
Example usage of the ML pipeline for health risk classification.
"""

from health_risk_service import get_health_risk_service
from health_rules import classify_ingredient_health_risk, get_risk_level


def example_single_ingredient():
    """Example: Analyze a single ingredient."""
    print("=" * 60)
    print("EXAMPLE 1: Single Ingredient Analysis")
    print("=" * 60)
    
    ingredient = "cheddar cheese"
    risks = classify_ingredient_health_risk(ingredient)
    risk_level = get_risk_level(risks)
    
    print(f"\nIngredient: {ingredient}")
    print(f"Risk Level: {risk_level.upper()}")
    print("\nRisk Factors:")
    for risk_type, has_risk in risks.items():
        if has_risk:
            print(f"  ✓ {risk_type.replace('_', ' ').title()}")


def example_recipe_analysis():
    """Example: Analyze a complete recipe."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Recipe Analysis")
    print("=" * 60)
    
    recipe_ingredients = [
        "butter",
        "heavy cream",
        "bacon",
        "cheddar cheese",
        "eggs",
        "spinach",
        "olive oil"
    ]
    
    service = get_health_risk_service()
    summary = service.get_risk_summary(recipe_ingredients)
    
    print(f"\nRecipe Ingredients: {', '.join(recipe_ingredients)}")
    print(f"Overall Risk: {summary['risk_level'].upper()}")
    print(f"High-Risk Ingredients: {summary['high_risk_count']}/{summary['total_ingredients']}")
    
    print("\nRisk Factor Breakdown:")
    for factor, percentage in summary['risk_factors'].items():
        if percentage > 0:
            print(f"  {factor.title()}: {percentage:.1f}%")
    
    if summary['warnings']:
        print("\nWarnings:")
        for warning in summary['warnings']:
            print(f"  {warning}")


def example_healthy_recipe():
    """Example: Analyze a healthy recipe."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Healthy Recipe Analysis")
    print("=" * 60)
    
    healthy_recipe = [
        "salmon fillet",
        "olive oil",
        "garlic",
        "spinach",
        "broccoli",
        "quinoa",
        "lemon juice"
    ]
    
    service = get_health_risk_service()
    summary = service.get_risk_summary(healthy_recipe)
    
    print(f"\nRecipe Ingredients: {', '.join(healthy_recipe)}")
    print(f"Overall Risk: {summary['risk_level'].upper()}")
    
    if summary['warnings']:
        print("\nHealth Notes:")
        for warning in summary['warnings']:
            print(f"  {warning}")


def example_comparison():
    """Example: Compare two recipes."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Recipe Comparison")
    print("=" * 60)
    
    recipe_a = ["bacon", "butter", "cream cheese", "eggs", "white bread"]
    recipe_b = ["chicken breast", "olive oil", "vegetables", "brown rice", "herbs"]
    
    service = get_health_risk_service()
    
    print("\nRecipe A (Traditional Breakfast):")
    print(f"  Ingredients: {', '.join(recipe_a)}")
    summary_a = service.get_risk_summary(recipe_a)
    print(f"  Risk Level: {summary_a['risk_level'].upper()}")
    print(f"  High-Risk: {summary_a['high_risk_count']}/{summary_a['total_ingredients']} ingredients")
    
    print("\nRecipe B (Healthy Meal):")
    print(f"  Ingredients: {', '.join(recipe_b)}")
    summary_b = service.get_risk_summary(recipe_b)
    print(f"  Risk Level: {summary_b['risk_level'].upper()}")
    print(f"  High-Risk: {summary_b['high_risk_count']}/{summary_b['total_ingredients']} ingredients")


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "HEALTH RISK CLASSIFIER - EXAMPLES" + " " * 14 + "║")
    print("╚" + "=" * 58 + "╝")
    
    example_single_ingredient()
    example_recipe_analysis()
    example_healthy_recipe()
    example_comparison()
    
    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()

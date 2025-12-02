"""
Command-line interface for the ML pipeline.
"""

import argparse
import sys
from pathlib import Path

from train_classifier import main as train_main
from predict import HealthRiskPredictor
from test_classifier import run_tests
from health_rules import analyze_recipe_risks


def cmd_train(args):
    """Train the classifier."""
    print("Starting training pipeline...")
    train_main()


def cmd_predict(args):
    """Make predictions."""
    try:
        predictor = HealthRiskPredictor(args.model_dir)
        
        # Get ingredients
        if args.file:
            with open(args.file, 'r') as f:
                ingredients = [line.strip() for line in f if line.strip()]
        else:
            ingredients = [ing.strip() for ing in args.ingredients.split(',')]
        
        # Analyze
        if args.recipe:
            analysis = predictor.predict_recipe(ingredients)
            print_recipe_analysis(analysis)
        else:
            for ingredient in ingredients:
                result = predictor.predict_single(ingredient)
                print_single_result(result)
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_test(args):
    """Run test suite."""
    print("Running test suite...\n")
    success = run_tests()
    sys.exit(0 if success else 1)


def cmd_analyze(args):
    """Quick analysis without ML (rule-based only)."""
    if args.file:
        with open(args.file, 'r') as f:
            ingredients = [line.strip() for line in f if line.strip()]
    else:
        ingredients = [ing.strip() for ing in args.ingredients.split(',')]
    
    analysis = analyze_recipe_risks(ingredients)
    print_recipe_analysis(analysis)


def print_single_result(result):
    """Print single ingredient prediction."""
    print(f"\n{'=' * 60}")
    print(f"Ingredient: {result['ingredient']}")
    print(f"Risk Level: {result['risk_level_ml'].upper()}")
    print(f"Confidence: {result['confidence']:.1%}")
    
    # Show risk factors
    risks = result['individual_risks']
    risk_flags = [k for k, v in risks.items() if v and k != 'healthy']
    if risk_flags:
        print("Risk Factors:", ', '.join(r.replace('_', ' ').title() for r in risk_flags))


def print_recipe_analysis(analysis):
    """Print recipe analysis."""
    print(f"\n{'=' * 60}")
    print("RECIPE HEALTH ANALYSIS")
    print('=' * 60)
    print(f"Overall Risk: {analysis['overall_risk'].upper()}")
    print(f"Total Ingredients: {analysis['ingredient_count']}")
    print(f"High-Risk Ingredients: {analysis['high_risk_ingredients']}")
    
    if analysis.get('warnings'):
        print("\nWarnings:")
        for warning in analysis['warnings']:
            print(f"  {warning}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='ML Pipeline for Ingredient Health Risk Classification',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Train the model
  python cli.py train
  
  # Test a single ingredient
  python cli.py predict -i "cheddar cheese"
  
  # Analyze a recipe
  python cli.py predict -r -i "butter,cheese,bacon,eggs"
  
  # Run tests
  python cli.py test
  
  # Quick rule-based analysis (no ML)
  python cli.py analyze -i "spinach,olive oil,garlic"
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Train command
    train_parser = subparsers.add_parser('train', help='Train the classifier')
    train_parser.set_defaults(func=cmd_train)
    
    # Predict command
    predict_parser = subparsers.add_parser('predict', help='Make predictions')
    predict_parser.add_argument('-i', '--ingredients', required=True,
                               help='Comma-separated ingredients')
    predict_parser.add_argument('-f', '--file', help='File with ingredients (one per line)')
    predict_parser.add_argument('-r', '--recipe', action='store_true',
                               help='Analyze as complete recipe')
    predict_parser.add_argument('--model-dir', default='models',
                               help='Directory with trained model')
    predict_parser.set_defaults(func=cmd_predict)
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run test suite')
    test_parser.set_defaults(func=cmd_test)
    
    # Analyze command (rule-based only)
    analyze_parser = subparsers.add_parser('analyze', 
                                           help='Quick rule-based analysis (no ML)')
    analyze_parser.add_argument('-i', '--ingredients', required=True,
                               help='Comma-separated ingredients')
    analyze_parser.add_argument('-f', '--file', help='File with ingredients')
    analyze_parser.set_defaults(func=cmd_analyze)
    
    # Parse and execute
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == '__main__':
    main()

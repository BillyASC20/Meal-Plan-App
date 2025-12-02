"""
Prediction script for classifying ingredient health risks.
"""

import argparse
import joblib
import pandas as pd
from pathlib import Path
from typing import List, Dict

from health_rules import analyze_recipe_risks, classify_ingredient_health_risk, get_risk_level
from feature_engineering import normalize_ingredient_name


class HealthRiskPredictor:
    """Predict health risks for ingredients using trained ML model."""
    
    def __init__(self, model_dir='models'):
        """Load trained model and associated objects."""
        model_dir = Path(model_dir)
        
        try:
            self.model = joblib.load(model_dir / 'health_risk_classifier.pkl')
            self.scaler = joblib.load(model_dir / 'feature_scaler.pkl')
            self.extractor = joblib.load(model_dir / 'feature_extractor.pkl')
            
            with open(model_dir / 'feature_names.txt', 'r') as f:
                self.feature_names = [line.strip() for line in f]
            
            print("✅ Model loaded successfully")
        except FileNotFoundError:
            print("❌ Model files not found. Please run train_classifier.py first.")
            raise
    
    def predict_single(self, ingredient: str) -> Dict:
        """
        Predict health risk for a single ingredient.
        
        Returns:
            Dictionary with prediction results
        """
        # Normalize ingredient name
        ingredient_normalized = normalize_ingredient_name(ingredient)
        
        # Extract features
        features = self.extractor.extract_features(ingredient_normalized)
        feature_vector = [features[fn] for fn in self.feature_names]
        feature_vector = self.scaler.transform([feature_vector])
        
        # Predict risk level
        risk_level_ml = self.model.predict(feature_vector)[0]
        risk_proba = self.model.predict_proba(feature_vector)[0]
        
        # Also get rule-based classification for comparison
        risks_rules = classify_ingredient_health_risk(ingredient_normalized)
        risk_level_rules = get_risk_level(risks_rules)
        
        # Get class probabilities
        class_probs = dict(zip(self.model.classes_, risk_proba))
        
        return {
            'ingredient': ingredient,
            'risk_level_ml': risk_level_ml,
            'risk_level_rules': risk_level_rules,
            'confidence': max(risk_proba),
            'class_probabilities': class_probs,
            'individual_risks': risks_rules
        }
    
    def predict_batch(self, ingredients: List[str]) -> pd.DataFrame:
        """Predict health risks for multiple ingredients."""
        results = []
        for ingredient in ingredients:
            result = self.predict_single(ingredient)
            results.append(result)
        
        return pd.DataFrame(results)
    
    def predict_recipe(self, ingredients: List[str]) -> Dict:
        """Analyze health risks for a complete recipe."""
        # Get individual predictions
        individual_predictions = self.predict_batch(ingredients)
        
        # Get recipe-level analysis
        recipe_analysis = analyze_recipe_risks(ingredients)
        
        # Add ML predictions to analysis
        recipe_analysis['ml_predictions'] = individual_predictions.to_dict('records')
        recipe_analysis['high_risk_ml'] = len(
            individual_predictions[
                individual_predictions['risk_level_ml'].isin(['high', 'very_high'])
            ]
        )
        
        return recipe_analysis


def print_prediction_result(result: Dict):
    """Pretty print prediction result."""
    print("\n" + "=" * 60)
    print(f"INGREDIENT: {result['ingredient']}")
    print("=" * 60)
    print(f"ML Prediction: {result['risk_level_ml'].upper()}")
    print(f"Rule-based: {result['risk_level_rules'].upper()}")
    print(f"Confidence: {result['confidence']:.2%}")
    
    print("\nClass Probabilities:")
    for class_name, prob in result['class_probabilities'].items():
        print(f"  {class_name}: {prob:.2%}")
    
    print("\nIndividual Risk Factors:")
    for risk_type, has_risk in result['individual_risks'].items():
        if has_risk and risk_type != 'healthy':
            print(f"  ⚠️  {risk_type.replace('_', ' ').title()}")
    
    if result['individual_risks']['healthy']:
        print("  ✅ Marked as healthy ingredient")


def print_recipe_analysis(analysis: Dict):
    """Pretty print recipe analysis."""
    print("\n" + "=" * 60)
    print("RECIPE HEALTH RISK ANALYSIS")
    print("=" * 60)
    print(f"Overall Risk Level: {analysis['overall_risk'].upper()}")
    print(f"Total Ingredients: {analysis['ingredient_count']}")
    print(f"High-Risk Ingredients: {analysis['high_risk_ingredients']}")
    
    print("\nRisk Factor Percentages:")
    for risk_type, percentage in analysis['risk_percentages'].items():
        if percentage > 0:
            print(f"  {risk_type.replace('_', ' ').title()}: {percentage:.1f}%")
    
    if analysis['warnings']:
        print("\n⚠️  Warnings:")
        for warning in analysis['warnings']:
            print(f"  {warning}")
    
    print("\nIndividual Ingredient Analysis:")
    for pred in analysis['ml_predictions']:
        risk_indicator = "🔴" if pred['risk_level_ml'] in ['high', 'very_high'] else \
                        "🟡" if pred['risk_level_ml'] == 'moderate' else "🟢"
        print(f"  {risk_indicator} {pred['ingredient']}: {pred['risk_level_ml']}")


def main():
    parser = argparse.ArgumentParser(description='Predict health risks for ingredients')
    parser.add_argument('--ingredients', '-i', type=str, help='Comma-separated list of ingredients')
    parser.add_argument('--file', '-f', type=str, help='Path to file with ingredients (one per line)')
    parser.add_argument('--recipe', '-r', action='store_true', help='Analyze as a complete recipe')
    parser.add_argument('--output', '-o', type=str, help='Output CSV file for batch predictions')
    
    args = parser.parse_args()
    
    # Load predictor
    predictor = HealthRiskPredictor()
    
    # Get ingredients list
    if args.file:
        with open(args.file, 'r') as f:
            ingredients = [line.strip() for line in f if line.strip()]
    elif args.ingredients:
        ingredients = [ing.strip() for ing in args.ingredients.split(',')]
    else:
        # Interactive mode
        print("Enter ingredients (comma-separated):")
        ingredients_input = input("> ")
        ingredients = [ing.strip() for ing in ingredients_input.split(',')]
    
    # Make predictions
    if args.recipe:
        # Analyze as recipe
        analysis = predictor.predict_recipe(ingredients)
        print_recipe_analysis(analysis)
    else:
        # Analyze individual ingredients
        if len(ingredients) == 1:
            result = predictor.predict_single(ingredients[0])
            print_prediction_result(result)
        else:
            results_df = predictor.predict_batch(ingredients)
            
            # Print results
            print("\n" + "=" * 60)
            print("BATCH PREDICTION RESULTS")
            print("=" * 60)
            print(results_df[['ingredient', 'risk_level_ml', 'confidence']].to_string(index=False))
            
            # Save to file if requested
            if args.output:
                results_df.to_csv(args.output, index=False)
                print(f"\n✅ Results saved to {args.output}")


if __name__ == '__main__':
    main()

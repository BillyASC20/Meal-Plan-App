"""
Integration module for using health risk classifier in the main backend.
"""

import sys
from pathlib import Path

# Add ml-pipeline to path
ml_pipeline_path = Path(__file__).parent
sys.path.insert(0, str(ml_pipeline_path))

from predict import HealthRiskPredictor
from health_rules import analyze_recipe_risks


class HealthRiskService:
    """Service for checking ingredient health risks in recipes."""
    
    def __init__(self, model_dir=None):
        """Initialize the health risk service."""
        if model_dir is None:
            model_dir = Path(__file__).parent / 'models'
        
        try:
            self.predictor = HealthRiskPredictor(model_dir)
            self.ml_available = True
            print("✅ ML Health Risk Predictor loaded")
        except Exception as e:
            print(f"⚠️  ML model not available: {e}")
            print("   Using rule-based classification only")
            self.ml_available = False
            self.predictor = None
    
    def analyze_ingredients(self, ingredients: list) -> dict:
        """
        Analyze health risks for a list of ingredients.
        
        Args:
            ingredients: List of ingredient names/strings
        
        Returns:
            Dictionary with health risk analysis
        """
        if self.ml_available:
            # Use ML predictor
            return self.predictor.predict_recipe(ingredients)
        else:
            # Fallback to rule-based only
            return analyze_recipe_risks(ingredients)
    
    def get_ingredient_warnings(self, ingredients: list) -> list:
        """
        Get human-readable warnings for ingredients.
        
        Args:
            ingredients: List of ingredient names
        
        Returns:
            List of warning strings
        """
        analysis = self.analyze_ingredients(ingredients)
        return analysis.get('warnings', [])
    
    def is_high_risk(self, ingredients: list) -> bool:
        """
        Check if ingredients contain high health risks.
        
        Args:
            ingredients: List of ingredient names
        
        Returns:
            True if overall risk is high, False otherwise
        """
        analysis = self.analyze_ingredients(ingredients)
        return analysis.get('overall_risk') == 'high'
    
    def get_risk_summary(self, ingredients: list) -> dict:
        """
        Get simplified risk summary for frontend display.
        
        Args:
            ingredients: List of ingredient names
        
        Returns:
            Simplified risk summary dict
        """
        analysis = self.analyze_ingredients(ingredients)
        
        # Extract individual ingredient risks from ML predictions
        ingredient_details = []
        if 'ml_predictions' in analysis:
            for pred in analysis['ml_predictions']:
                risk_level = pred.get('risk_level_ml', 'unknown')
                is_high_risk = risk_level in ['high', 'very_high']
                
                # Get specific risk factors for this ingredient
                individual_risks = pred.get('individual_risks', {})
                risk_types = [k.replace('_', ' ').title() for k, v in individual_risks.items() if v and k != 'healthy']
                
                ingredient_details.append({
                    'name': pred.get('ingredient', ''),
                    'risk_level': risk_level,
                    'is_high_risk': is_high_risk,
                    'risk_types': risk_types,
                    'confidence': pred.get('confidence', 0)
                })
        
        return {
            'overall_risk': analysis.get('overall_risk', 'unknown'),
            'risk_level': analysis.get('overall_risk', 'unknown'),
            'warnings': analysis.get('warnings', []),
            'high_risk_count': analysis.get('high_risk_ingredients', 0),
            'total_ingredients': analysis.get('ingredient_count', len(ingredients)),
            'risk_factors': {
                'cholesterol': analysis.get('risk_percentages', {}).get('high_cholesterol', 0),
                'heart_disease': analysis.get('risk_percentages', {}).get('heart_disease', 0),
                'diabetes': analysis.get('risk_percentages', {}).get('diabetes', 0),
                'hypertension': analysis.get('risk_percentages', {}).get('hypertension', 0),
                'obesity': analysis.get('risk_percentages', {}).get('obesity', 0),
            },
            'ingredient_details': ingredient_details
        }


# Create singleton instance
_health_risk_service = None

def get_health_risk_service():
    """Get or create the health risk service singleton."""
    global _health_risk_service
    if _health_risk_service is None:
        _health_risk_service = HealthRiskService()
    return _health_risk_service

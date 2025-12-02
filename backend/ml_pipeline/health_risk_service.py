
import sys
from pathlib import Path
ml_pipeline_path = Path(__file__).parent
sys.path.insert(0, str(ml_pipeline_path))
from predict import HealthRiskPredictor
from health_rules import analyze_recipe_risks


class HealthRiskService:
    def __init__(self, model_dir=None):
        if model_dir is None:
            # Try backend/ml_models first (Docker/production), then ml-pipeline/models (local dev)
            backend_models = Path(__file__).parent.parent / 'ml_models'
            dev_models = Path(__file__).parent / 'models'
            
            if backend_models.exists():
                model_dir = backend_models
            elif dev_models.exists():
                model_dir = dev_models
            else:
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
        if self.ml_available:
            # Use ML predictor
            return self.predictor.predict_recipe(ingredients)
        else:
            # Fallback to rule-based only
            return analyze_recipe_risks(ingredients)
    
    def get_ingredient_warnings(self, ingredients: list) -> list:
        analysis = self.analyze_ingredients(ingredients)
        return analysis.get('warnings', [])
    
    def is_high_risk(self, ingredients: list) -> bool:
        analysis = self.analyze_ingredients(ingredients)
        return analysis.get('overall_risk') == 'high'
    
    def get_risk_summary(self, ingredients: list) -> dict:
        analysis = self.analyze_ingredients(ingredients)
        
        ingredient_details = []
        if 'ml_predictions' in analysis:
            for pred in analysis['ml_predictions']:
                risk_level = pred.get('risk_level_ml', 'unknown')
                is_high_risk = risk_level in ['high', 'very_high']
                individual_risks = pred.get('individual_risks', {})
                risk_types = [k.replace('_', ' ').title() for k, v in individual_risks.items() if v and k != 'healthy']
                confidence = pred.get('confidence', 0)
                confidence_type = 'high' if confidence >= 0.5 else ('low' if confidence >= 0.2 else 'none')
                ingredient_details.append({
                    'name': pred.get('ingredient', ''),
                    'risk_level': risk_level,
                    'is_high_risk': is_high_risk,
                    'risk_types': risk_types,
                    'confidence': confidence,
                    'confidence_type': confidence_type
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

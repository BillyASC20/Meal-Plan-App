"""
Test suite for health risk classification.
"""

import unittest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from health_rules import (
    classify_ingredient_health_risk,
    get_risk_level,
    analyze_recipe_risks
)
from feature_engineering import (
    IngredientFeatureExtractor,
    normalize_ingredient_name
)


class TestHealthRules(unittest.TestCase):
    """Test health risk classification rules."""
    
    def test_high_cholesterol_ingredients(self):
        """Test detection of high cholesterol ingredients."""
        high_cholesterol_items = ['egg yolk', 'whole egg', 'butter', 'cheese cheddar']
        
        for item in high_cholesterol_items:
            risks = classify_ingredient_health_risk(item)
            self.assertTrue(risks['high_cholesterol'], 
                          f"{item} should be flagged for high cholesterol")
    
    def test_heart_disease_ingredients(self):
        """Test detection of heart disease risk ingredients."""
        risky_items = ['bacon', 'sausage', 'red meat', 'butter']
        
        for item in risky_items:
            risks = classify_ingredient_health_risk(item)
            self.assertTrue(risks['heart_disease'],
                          f"{item} should be flagged for heart disease risk")
    
    def test_diabetes_ingredients(self):
        """Test detection of diabetes risk ingredients."""
        sugary_items = ['sugar', 'candy', 'chocolate cake', 'sweetened juice']
        
        for item in sugary_items:
            risks = classify_ingredient_health_risk(item)
            self.assertTrue(risks['diabetes'],
                          f"{item} should be flagged for diabetes risk")
    
    def test_healthy_ingredients(self):
        """Test detection of healthy ingredients."""
        healthy_items = ['broccoli', 'spinach', 'apple', 'salmon', 'olive oil']
        
        for item in healthy_items:
            risks = classify_ingredient_health_risk(item)
            self.assertTrue(risks['healthy'],
                          f"{item} should be marked as healthy")
    
    def test_risk_level_classification(self):
        """Test overall risk level determination."""
        # Healthy ingredient - should be low risk
        risks_healthy = {'high_cholesterol': False, 'heart_disease': False,
                        'diabetes': False, 'hypertension': False, 
                        'obesity': False, 'healthy': True}
        self.assertEqual(get_risk_level(risks_healthy), 'low')
        
        # Single risk factor - moderate
        risks_moderate = {'high_cholesterol': True, 'heart_disease': False,
                         'diabetes': False, 'hypertension': False,
                         'obesity': False, 'healthy': False}
        self.assertEqual(get_risk_level(risks_moderate), 'moderate')
        
        # Multiple risk factors - high
        risks_high = {'high_cholesterol': True, 'heart_disease': True,
                     'diabetes': False, 'hypertension': False,
                     'obesity': False, 'healthy': False}
        self.assertEqual(get_risk_level(risks_high), 'high')
    
    def test_recipe_analysis(self):
        """Test recipe-level risk analysis."""
        # Healthy recipe
        healthy_recipe = ['spinach', 'chicken breast', 'olive oil', 'garlic']
        analysis = analyze_recipe_risks(healthy_recipe)
        self.assertEqual(analysis['overall_risk'], 'low')
        
        # Risky recipe
        risky_recipe = ['bacon', 'cheese', 'butter', 'cream', 'sugar']
        analysis = analyze_recipe_risks(risky_recipe)
        self.assertIn(analysis['overall_risk'], ['moderate', 'high'])
        self.assertGreater(len(analysis['warnings']), 0)


class TestFeatureEngineering(unittest.TestCase):
    """Test feature extraction."""
    
    def setUp(self):
        self.extractor = IngredientFeatureExtractor()
    
    def test_feature_extraction(self):
        """Test that features are extracted correctly."""
        features = self.extractor.extract_features("butter whole milk")
        
        self.assertIn('has_fat_keyword', features)
        self.assertIn('has_dairy_keyword', features)
        self.assertEqual(features['has_fat_keyword'], 1.0)
        self.assertEqual(features['has_dairy_keyword'], 1.0)
    
    def test_batch_feature_extraction(self):
        """Test batch feature extraction."""
        ingredients = ['butter', 'cheese', 'spinach']
        features = self.extractor.extract_batch_features(ingredients)
        
        self.assertEqual(features.shape[0], 3)
        self.assertGreater(features.shape[1], 0)
    
    def test_normalize_ingredient_name(self):
        """Test ingredient name normalization."""
        # Test lowercase conversion
        self.assertEqual(normalize_ingredient_name("BUTTER"), "butter")
        
        # Test whitespace normalization
        self.assertEqual(normalize_ingredient_name("  butter   cheese  "), 
                        "butter cheese")
        
        # Test abbreviation expansion
        normalized = normalize_ingredient_name("butter w/ salt")
        self.assertIn("with", normalized)


class TestIntegration(unittest.TestCase):
    """Integration tests for the full pipeline."""
    
    def test_end_to_end_prediction(self):
        """Test end-to-end prediction flow."""
        # Test ingredients
        test_ingredients = [
            'whole milk',
            'cheddar cheese',
            'spinach',
            'olive oil',
            'bacon'
        ]
        
        # Analyze recipe
        analysis = analyze_recipe_risks(test_ingredients)
        
        # Verify structure
        self.assertIn('overall_risk', analysis)
        self.assertIn('warnings', analysis)
        self.assertIn('risk_percentages', analysis)
        self.assertIn('ingredient_count', analysis)
        
        # Verify data types
        self.assertIsInstance(analysis['warnings'], list)
        self.assertIsInstance(analysis['risk_percentages'], dict)
        self.assertEqual(analysis['ingredient_count'], len(test_ingredients))


def run_tests():
    """Run all tests and print results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestHealthRules))
    suite.addTests(loader.loadTestsFromTestCase(TestFeatureEngineering))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)

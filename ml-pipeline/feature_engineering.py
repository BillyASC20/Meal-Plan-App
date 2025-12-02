"""
Feature engineering for ingredient health risk classification.
Extracts features from ingredient names and descriptions.
"""

import re
import numpy as np
from typing import List, Dict


class IngredientFeatureExtractor:
    """Extract features from ingredient names for ML classification."""
    
    def __init__(self):
        # Nutritional keywords
        self.fat_keywords = ['fat', 'oil', 'butter', 'lard', 'cream', 'fried', 'ghee']
        self.protein_keywords = ['meat', 'chicken', 'beef', 'pork', 'fish', 'egg', 'protein']
        self.carb_keywords = ['flour', 'rice', 'bread', 'pasta', 'sugar', 'starch']
        self.dairy_keywords = ['milk', 'cheese', 'yogurt', 'cream', 'butter', 'whey']
        self.processed_keywords = ['canned', 'frozen', 'instant', 'packaged', 'processed']
        self.natural_keywords = ['fresh', 'raw', 'whole', 'organic', 'natural']
        
    def extract_features(self, ingredient_name: str) -> Dict[str, float]:
        """
        Extract features from a single ingredient name.
        
        Returns:
            Dictionary of feature values
        """
        name_lower = ingredient_name.lower()
        
        features = {
            # Keyword presence features
            'has_fat_keyword': float(any(kw in name_lower for kw in self.fat_keywords)),
            'has_protein_keyword': float(any(kw in name_lower for kw in self.protein_keywords)),
            'has_carb_keyword': float(any(kw in name_lower for kw in self.carb_keywords)),
            'has_dairy_keyword': float(any(kw in name_lower for kw in self.dairy_keywords)),
            'has_processed_keyword': float(any(kw in name_lower for kw in self.processed_keywords)),
            'has_natural_keyword': float(any(kw in name_lower for kw in self.natural_keywords)),
            
            # Text statistics
            'name_length': len(ingredient_name),
            'word_count': len(ingredient_name.split()),
            'has_numbers': float(bool(re.search(r'\d', ingredient_name))),
            
            # Specific indicators
            'is_reduced_fat': float('reduced fat' in name_lower or 'low fat' in name_lower),
            'is_whole': float('whole' in name_lower),
            'is_skim': float('skim' in name_lower or 'nonfat' in name_lower),
            'has_salt': float('salt' in name_lower or 'sodium' in name_lower),
            'has_sugar': float('sugar' in name_lower or 'sweet' in name_lower),
            
            # Processing level indicators
            'is_dried': float('dried' in name_lower or 'powder' in name_lower),
            'is_fresh': float('fresh' in name_lower),
            'is_frozen': float('frozen' in name_lower),
            'is_canned': float('canned' in name_lower or 'can' in name_lower),
        }
        
        return features
    
    def extract_batch_features(self, ingredient_names: List[str]) -> np.ndarray:
        """
        Extract features for multiple ingredients.
        
        Returns:
            2D numpy array of shape (n_samples, n_features)
        """
        feature_list = []
        for name in ingredient_names:
            features = self.extract_features(name)
            feature_list.append(list(features.values()))
        
        return np.array(feature_list)
    
    def get_feature_names(self) -> List[str]:
        """Get list of feature names in order."""
        sample_features = self.extract_features("sample ingredient")
        return list(sample_features.keys())


def create_ngram_features(ingredient_names: List[str], n: int = 2) -> Dict:
    """
    Create character n-gram features for ingredient names.
    Useful for capturing patterns in ingredient terminology.
    
    Args:
        ingredient_names: List of ingredient names
        n: N-gram size (default 2 for bigrams)
    
    Returns:
        Dictionary mapping n-grams to their frequencies
    """
    ngram_counts = {}
    
    for name in ingredient_names:
        name_clean = name.lower().replace(' ', '_')
        # Extract n-grams
        for i in range(len(name_clean) - n + 1):
            ngram = name_clean[i:i+n]
            ngram_counts[ngram] = ngram_counts.get(ngram, 0) + 1
    
    return ngram_counts


def normalize_ingredient_name(name: str) -> str:
    """
    Normalize ingredient name for better matching.
    
    - Convert to lowercase
    - Remove extra whitespace
    - Remove special characters
    - Standardize common abbreviations
    """
    # Lowercase
    name = name.lower()
    
    # Common abbreviations
    replacements = {
        'w/': 'with',
        'wo/': 'without',
        'oz': 'ounce',
        'lb': 'pound',
        'tbsp': 'tablespoon',
        'tsp': 'teaspoon',
        'pkg': 'package',
    }
    
    for abbr, full in replacements.items():
        name = name.replace(abbr, full)
    
    # Remove special characters except spaces and hyphens
    name = re.sub(r'[^a-z0-9\s\-]', '', name)
    
    # Normalize whitespace
    name = ' '.join(name.split())
    
    return name

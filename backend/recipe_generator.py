import random
from .openai_service import OpenAIService
from .vision_service import vision_service

class RecipeGenerator:
    def __init__(self, openai_service=None):
        """Initialize the recipe generator with OpenAI service and Vision service."""
        self.openai_service = openai_service or OpenAIService()
        self.vision_service = vision_service
    
    def detect_ingredients_from_image(self, base64_image):
        """
        Detect food ingredients from an image using YOLOv8.
        
        Args:
            base64_image (str): Base64 encoded image data
            
        Returns:
            list: List of detected ingredient names
        """
        try:
            # Use YOLOv8 for free, self-hosted detection
            ingredients = self.vision_service.detect_ingredients(base64_image)
            return ingredients
        except Exception as e:
            print(f"Error detecting ingredients: {str(e)}")
            # Fallback to mock data if detection fails
            return self.detect_food_items_mock()
    
    def detect_food_items_mock(self):
        """Mock function to simulate food item detection."""
        possible_ingredient_sets = [
            ["banana", "apple", "bread"],
            ["chicken", "broccoli", "rice", "garlic"],
            ["pasta", "tomato", "basil", "cheese"],
            ["egg", "milk", "flour", "butter", "sugar"],
            ["potato", "carrot", "onion", "beef"],
            ["salmon", "lemon", "dill", "asparagus"]
        ]
        return random.choice(possible_ingredient_sets)
    
    def generate_recipes(self, ingredients=None):
        """Generate recipes based on ingredients using OpenAI service."""
        if ingredients is None:
            ingredients = self.detect_food_items_mock()
        
        try:
            recipes_list = self.openai_service.generate_recipes_from_ingredients(ingredients)
            
            return {
                "ingredients": ingredients,
                "recipes": recipes_list
            }
        
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error generating recipes: {str(e)}")
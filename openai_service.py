import json
import os
from openai import OpenAI

class OpenAIService:
    SYSTEM_PROMPT = """You are a helpful cooking assistant. Always respond with a JSON array of recipe objects that strictly follows this schema:

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Recipe List",
  "description": "A list of recipes with basic details.",
  "type": "array",
  "items": {
    "type": "object",
    "required": ["title", "meal_type", "ingredients", "steps"],
    "additionalProperties": false,
    "properties": {
      "title": {
        "type": "string",
        "description": "Name of the recipe"
      },
      "meal_type": {
        "type": "string",
        "enum": ["breakfast", "lunch", "dinner", "snack", "dessert", "drink"],
        "description": "Type of meal this recipe belongs to"
      },
      "ingredients": {
        "type": "array",
        "description": "List of ingredients for the recipe",
        "items": {
          "type": "string"
        },
        "minItems": 1
      },
      "steps": {
        "type": "array",
        "description": "Step-by-step instructions",
        "items": {
          "type": "string"
        },
        "minItems": 1
      }
    }
  }
}

IMPORTANT: 
- Return valid json that only matches this exact schema

"""

    def __init__(self, api_key=None):
        if api_key is None:
            api_key = os.getenv('OPENAI_API_KEY', 'YOUR_API_KEY_HERE')
        
        self.client = OpenAI(api_key=api_key)
        self.conversation_messages = [
            {
                "role": "system", 
                "content": self.SYSTEM_PROMPT
            }
        ]
    
    def generate_recipes_from_ingredients(self, ingredients):
        ingredients_string = ", ".join(ingredients)
        
        user_message = f"Here are the ingredients: {ingredients_string}. Create 2-3 recipes using these ingredients."
        
        self.conversation_messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=self.conversation_messages
            )
            
            assistant_response = response.choices[0].message.content
            self.conversation_messages.append({"role": "assistant", "content": assistant_response})
            
            recipes_list = json.loads(assistant_response)
            
            return recipes_list
        
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON response from AI")
        except Exception as e:
            raise Exception(f"Error calling OpenAI API: {str(e)}")
    
    def reset_conversation(self):
        self.conversation_messages = [
            {
                "role": "system", 
                "content": self.SYSTEM_PROMPT
            }
        ]
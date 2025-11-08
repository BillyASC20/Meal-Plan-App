import json
import os
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError
from typing import List, Literal

class Recipe(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    meal_type: Literal["breakfast", "lunch", "dinner", "snack", "dessert", "drink"]
    cook_time: int = Field(..., ge=1, le=300)
    servings: int = Field(..., ge=1, le=20)
    difficulty: Literal["easy", "medium", "hard"]
    ingredients: List[str] = Field(..., min_length=1)
    steps: List[str] = Field(..., min_length=1)
    tags: List[str] = Field(default_factory=list, max_length=10)

class RecipeList(BaseModel):
    recipes: List[Recipe] = Field(..., min_length=1, max_length=10)

class OpenAIService:
    SYSTEM_PROMPT = """You are a chef AI. Generate recipes as JSON matching this exact structure:
{
  "recipes": [
    {
      "title": "Recipe Name",
      "meal_type": "breakfast|lunch|dinner|snack|dessert|drink",
      "cook_time": 30,
      "servings": 4,
      "difficulty": "easy|medium|hard",
      "ingredients": ["ingredient 1", "ingredient 2"],
      "steps": ["step 1", "step 2"],
      "tags": ["tag1", "tag2"]
    }
  ]
}
Return ONLY valid JSON. No markdown, no explanations."""

    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")
        self.client = OpenAI(api_key=api_key)

    def generate_recipes_stream(self, ingredients):
        prompt = f"Create 3-5 recipes using these ingredients: {', '.join(ingredients)}. Include creative combinations."
        
        stream = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            stream=True,
            temperature=0.7
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def generate_recipes_from_ingredients(self, ingredients):
        prompt = f"Create 3-5 recipes using these ingredients: {', '.join(ingredients)}. Include creative combinations."
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        content = response.choices[0].message.content.strip()
        
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        try:
            data = json.loads(content)
            validated = RecipeList(**data)
            return [recipe.dict() for recipe in validated.recipes]
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON from OpenAI: {str(e)}")
        except ValidationError as e:
            raise ValueError(f"Schema validation failed: {str(e)}")

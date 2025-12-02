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
    SYSTEM_PROMPT = """You are an expert chef AI. Generate detailed, professional recipes as JSON matching this exact structure:
{
  "recipes": [
    {
      "title": "Recipe Name",
      "meal_type": "breakfast|lunch|dinner|snack|dessert|drink",
      "cook_time": 30,
      "servings": 4,
      "difficulty": "easy|medium|hard",
      "ingredients": ["2 cups all-purpose flour", "1 tsp salt", "3 large eggs"],
      "steps": ["Preheat oven to 350°F. Grease a 9x13 pan.", "In a large bowl, whisk together flour and salt.", "Add eggs one at a time, beating well after each addition."],
      "tags": ["vegetarian", "quick", "family-friendly"]
    }
  ]
}

CRITICAL JSON REQUIREMENTS FOR STREAMING:
- Start IMMEDIATELY with { and "recipes": [
- Each recipe must be a COMPLETE, VALID JSON object
- Close each recipe object properly with }
- Separate recipes with commas
- End with ] } to close the structure
- DO NOT include markdown code blocks (no ```json or ```)
- DO NOT include any text before or after the JSON
- Ensure all strings are properly escaped
- Complete each recipe fully before starting the next one

RECIPE CONTENT REQUIREMENTS:
- Include PRECISE measurements in ingredients (cups, tbsp, oz, grams, etc.)
- Include DETAILED cooking temperatures and times in steps
- Make steps clear and specific (not just "mix ingredients")
- Add helpful cooking tips in steps when relevant
- Each step should be 1-2 sentences with actionable instructions
- Use the provided ingredients creatively but realistically

Return ONLY valid JSON. Stream each complete recipe object as you generate it."""

    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")
        self.client = OpenAI(api_key=api_key)

    def generate_recipes_stream(self, ingredients):
        prompt = f"""Create 3-5 detailed, delicious recipes using ONLY these ingredients: {', '.join(ingredients)}.

STRICT REQUIREMENTS:
- Use ONLY the ingredients listed above - do not add any other ingredients
- You may use common pantry staples like salt, pepper, oil, and water ONLY if absolutely necessary
- Do NOT suggest ingredients the user doesn't have
- Create recipes that can realistically be made with just these ingredients
- Include precise measurements for all ingredients
- Provide detailed, step-by-step cooking instructions
- Add cooking temperatures, times, and helpful tips
- Include a mix of meal types (breakfast, lunch, dinner, etc.) if possible"""
        
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
        prompt = f"""Create 3-5 detailed, delicious recipes using ONLY these ingredients: {', '.join(ingredients)}.

STRICT REQUIREMENTS:
- Use ONLY the ingredients listed above - do not add any other ingredients
- You may use common pantry staples like salt, pepper, oil, and water ONLY if absolutely necessary
- Do NOT suggest ingredients the user doesn't have
- Create recipes that can realistically be made with just these ingredients
- Include precise measurements for all ingredients
- Provide detailed, step-by-step cooking instructions
- Add cooking temperatures, times, and helpful tips
- Include a mix of meal types (breakfast, lunch, dinner, etc.) if possible"""
        
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

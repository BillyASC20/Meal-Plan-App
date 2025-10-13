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
    SYSTEM_PROMPT = """You are a concise, professional recipe developer.

Respond ONLY with valid JSON shaped exactly as:
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

Rules:
- Use ONLY user ingredients plus salt, black pepper, cooking oil (olive/vegetable), and water. Do not invent anything else.
- Each recipe can use any subset of their list; quality over quantity.
- Keep instructions realistic, actionable, and cookable at home.
- Include specific measurements and add temperatures/times when they matter.
- 1–2 sentences per step; keep tone matter-of-fact.
- No markdown fences, no narration, no extra text before/after JSON.
- Streaming-friendly: start with {, keep well-formed JSON, close with }.
"""

    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")
        self.client = OpenAI(api_key=api_key)

    def generate_recipes_stream(self, ingredients, meal_type=None):
        meal_type_requirement = ""
        meal_type_json_field = ""
        
        if meal_type:
            meal_type_requirement = f"""

CRITICAL MEAL TYPE REQUIREMENT
- You MUST ONLY generate {meal_type.upper()} recipes
- Every single recipe must have "meal_type": "{meal_type}" in the JSON
- DO NOT create breakfast recipes if this is lunch or dinner
- DO NOT create lunch recipes if this is breakfast or dinner  
- DO NOT create dinner recipes if this is breakfast or lunch
- ONLY generate recipes appropriate for {meal_type}
- Think about what people traditionally eat for {meal_type} and the portion sizes appropriate for that meal
- Consider the time of day and energy needs for {meal_type}
- If you cannot create good {meal_type} recipes with these ingredients, create fewer recipes (even just 1-2) but ALL must be {meal_type}
- Recipes must be dishes that make sense for {meal_type} based on culinary tradition and common eating habits"""
            meal_type_json_field = f' and MUST have "meal_type": "{meal_type}"'
        
        prompt = f"""Available ingredients (only use these + salt/pepper/oil/water): {', '.join(ingredients)}

    Create 3-5 real, cookable meal ideas from this list. Balanced, satisfying dishes that someone would actually make at home. Quality beats quantity; if the list is sparse, fewer strong recipes are fine.{meal_type_requirement}

    Output rules:
    - Use the exact JSON shape from the system prompt; no markdown.
    - Keep measurements specific and instructions concise with temps/times when relevant.
    - Each recipe{meal_type_json_field} must be realistic and achievable with the provided items only."""
        
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

    def generate_recipes_from_ingredients(self, ingredients, meal_type=None):
        meal_type_requirement = ""
        meal_type_json_field = ""
        
        if meal_type:
            meal_type_requirement = f"""

CRITICAL MEAL TYPE REQUIREMENT
- You MUST ONLY generate {meal_type.upper()} recipes
- Every single recipe must have "meal_type": "{meal_type}" in the JSON
- DO NOT create breakfast recipes if this is lunch or dinner
- DO NOT create lunch recipes if this is breakfast or dinner  
- DO NOT create dinner recipes if this is breakfast or lunch
- ONLY generate recipes appropriate for {meal_type}
- Think about what people traditionally eat for {meal_type} and the portion sizes appropriate for that meal
- Consider the time of day and energy needs for {meal_type}
- If you cannot create good {meal_type} recipes with these ingredients, create fewer recipes (even just 1-2) but ALL must be {meal_type}
- Recipes must be dishes that make sense for {meal_type} based on culinary tradition and common eating habits"""
            meal_type_json_field = f' and MUST have "meal_type": "{meal_type}"'
        
        prompt = f"""Available ingredients (only use these + salt/pepper/oil/water): {', '.join(ingredients)}

    Create 3-5 real, cookable meal ideas from this list. Balanced, satisfying dishes that someone would actually make at home. Quality beats quantity; if the list is sparse, fewer strong recipes are fine.{meal_type_requirement}

    Output rules:
    - Use the exact JSON shape from the system prompt; no markdown.
    - Keep measurements specific and instructions concise with temps/times when relevant.
    - Each recipe{meal_type_json_field} must be realistic and achievable with the provided items only."""
        
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

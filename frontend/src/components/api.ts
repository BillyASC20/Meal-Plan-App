// Centralized API helper for backend interactions
// Contract:
// - detectIngredients(imageDataUrl: string) => Promise<DetectedResult>
// - generateRecipes(ingredients: string[]) => Promise<RecipeResult>

export interface Recipe {
  title: string
  meal_type: string
  ingredients: string[]
  steps: string[]
}
export interface RecipeResult {
  recipes: Recipe[]
}

export interface PredictionWithConfidence {
  name: string
  confidence: number
}

export interface DetectedResult {
  ingredients: string[]
  predictions: PredictionWithConfidence[]
  message?: string
}

const BASE_URL = 'http://localhost:5000'

async function handleResponse(res: Response) {
  let data: any
  try {
    data = await res.json()
  } catch (e) {
    throw new Error('Invalid JSON response')
  }
  if (!res.ok || data.status !== 'success') {
    throw new Error(data?.message || `Request failed (${res.status})`)
  }
  return data.data
}

async function detectIngredients(imageDataUrl: string): Promise<DetectedResult> {
  const res = await fetch(`${BASE_URL}/detect-ingredients`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image: imageDataUrl })
  })
  const data = await handleResponse(res)
  return {
    ingredients: Array.isArray(data.ingredients) ? data.ingredients : [],
    predictions: Array.isArray(data.predictions) ? data.predictions : [],
    message: data.message
  }
}

async function generateRecipes(ingredients: string[]): Promise<RecipeResult> {
  const res = await fetch(`${BASE_URL}/generate-recipes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ingredients })
  })
  const data = await handleResponse(res)
  return data as RecipeResult
}

export const api = {
  detectIngredients,
  generateRecipes,
  async getHeroImageDataURL(): Promise<string> {
    const res = await fetch(`${BASE_URL}/debug/hero-b64`)
    const data = await handleResponse(res)
    return data.image as string
  }
}

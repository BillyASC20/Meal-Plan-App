// Centralized API helper for backend interactions
// Contract:
// - detectIngredients(imageDataUrl: string) => Promise<DetectedResult>
// - generateRecipes(ingredients: string[]) => Promise<RecipeResult>

export interface Recipe {
  title: string
  meal_type: string
  cook_time: number
  servings: number
  difficulty: string
  ingredients: string[]
  steps: string[]
  tags: string[]
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
  image_with_boxes?: string  // Base64 image with bounding boxes drawn
}

const BASE_URL = 'http://localhost:5001'  // Changed from 5000 to 5001

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
    message: data.message,
    image_with_boxes: data.image_with_boxes  // Include the image with bounding boxes
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

async function* generateRecipesStream(ingredients: string[]): AsyncGenerator<string, void, unknown> {
  const res = await fetch(`${BASE_URL}/generate-recipes-stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ingredients })
  })
  
  if (!res.ok || !res.body) {
    throw new Error(`Stream failed: ${res.status}`)
  }
  
  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    
    const chunk = decoder.decode(value)
    const lines = chunk.split('\n')
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6))
        if (data.error) throw new Error(data.error)
        if (data.chunk) yield data.chunk
      }
    }
  }
}

export const api = {
  detectIngredients,
  generateRecipes,
  generateRecipesStream
}

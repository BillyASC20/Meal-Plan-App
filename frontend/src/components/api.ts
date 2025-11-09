
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
  image_with_boxes?: string
}

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:5001'

function getAuthHeaders(): HeadersInit {
  const headers: HeadersInit = {
    'Content-Type': 'application/json'
  }
  
  const token = localStorage.getItem('access_token')
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  
  return headers
}

async function handleResponse(res: Response) {
  if (res.status === 401) {
    throw new Error('Authentication required')
  }
  
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
  const headers = getAuthHeaders()
  const res = await fetch(`${BASE_URL}/detect-ingredients`, {
    method: 'POST',
    headers,
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
  const headers = getAuthHeaders()
  const res = await fetch(`${BASE_URL}/generate-recipes`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ ingredients })
  })
  const data = await handleResponse(res)
  return data as RecipeResult
}

async function* generateRecipesStream(ingredients: string[], imageUrl?: string): AsyncGenerator<string, void, unknown> {
  const headers = getAuthHeaders()
  const res = await fetch(`${BASE_URL}/generate-recipes-stream`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ ingredients, image_url: imageUrl })
  })
  
  if (res.status === 401) {
    throw new Error('Authentication required')
  }
  
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

async function getHeroImageDataURL(): Promise<string> {
  try {
    const res = await fetch('https://images.unsplash.com/photo-1498837167922-ddd27525d352?w=800&q=80')
    if (!res.ok) throw new Error('Failed to fetch sample image')
    const blob = await res.blob()
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onloadend = () => resolve(reader.result as string)
      reader.onerror = reject
      reader.readAsDataURL(blob)
    })
  } catch (error) {
    throw new Error('Could not load sample image. Please upload your own image.')
  }
}

export const api = {
  detectIngredients,
  generateRecipes,
  generateRecipesStream,
  getHeroImageDataURL,
  uploadImage,
  saveRecipes
}

/**
 * Upload image to Supabase Storage
 */
async function uploadImage(imageDataUrl: string): Promise<string> {
  const headers = getAuthHeaders()
  const res = await fetch(`${BASE_URL}/api/upload-image`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ image: imageDataUrl })
  })
  const data = await handleResponse(res)
  return data.image_url
}

/**
 * Save recipes and image reference to database
 */
async function saveRecipes(imageUrl: string, ingredients: string[], recipes: Recipe[]): Promise<void> {
  const headers = getAuthHeaders()
  const res = await fetch(`${BASE_URL}/api/save-recipes`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ 
      image_url: imageUrl,
      ingredients,
      recipes 
    })
  })
  await handleResponse(res)
}

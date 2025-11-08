import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { useNavigate, useLocation } from 'react-router-dom'
import { GlassCard } from '../components/GlassCard'
import RecipeCard from '../components/RecipeCard'
import './RecipesPage.css'
import { api, Recipe } from '../components/api'

export const RecipesPage = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const [recipes, setRecipes] = useState<Recipe[]>([])
  const [ingredients, setIngredients] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [streamingText, setStreamingText] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)

  useEffect(() => {
    const fetchRecipes = async () => {
      try {
        const fromState = (location.state as any)?.ingredients as string[] | undefined
        const fromStorage = sessionStorage.getItem('detectedIngredients')
        const parsed = fromStorage ? (JSON.parse(fromStorage) as string[]) : undefined
        const ingredientsToUse = (fromState && fromState.length > 0)
          ? fromState
          : (parsed && parsed.length > 0)
            ? parsed
            : []
        setIngredients(ingredientsToUse)
        
        if (ingredientsToUse.length > 0) {
          setIsStreaming(true)
          setStreamingText('')
          let fullText = ''
          
          try {
            for await (const chunk of api.generateRecipesStream(ingredientsToUse)) {
              fullText += chunk
              setStreamingText(fullText)
            }
            
            const cleanJson = fullText.trim()
              .replace(/^```json\n?/, '')
              .replace(/^```\n?/, '')
              .replace(/\n?```$/, '')
              .trim()
            
            const data = JSON.parse(cleanJson)
            setRecipes(data.recipes || [])
          } catch (err) {
            const result = await api.generateRecipes(ingredientsToUse)
            setRecipes(result.recipes || [])
          } finally {
            setIsStreaming(false)
          }
        } else {
          setRecipes([])
        }
      } catch (error) {
        setIsStreaming(false)
      } finally {
        setTimeout(() => setLoading(false), 1000)
      }
    }

    fetchRecipes()
  }, [location.state])

  if (loading) {
    return (
      <div className="recipes-page">
        <div className="loading-container">
          <motion.div
            className="loading-spinner"
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          >
            🍳
          </motion.div>
          <motion.p
            className="loading-text"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            Generating delicious recipes...
          </motion.p>
        </div>
      </div>
    )
  }

  return (
    <div className="recipes-page">
      <div className="recipes-header">
        <button className="back-button" onClick={() => navigate('/camera')}>
          ← Back
        </button>
        <h1 className="recipes-title">Your Recipes</h1>
        <div className="spacer"></div>
      </div>

      <div className="recipes-content">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <GlassCard className="ingredients-card">
            <h2 className="section-title">📦 Your Ingredients</h2>
            <div className="ingredients-tags">
              {ingredients.map((ingredient, idx) => (
                <motion.span
                  key={ingredient}
                  className="ingredient-tag"
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: idx * 0.05 }}
                >
                  {ingredient}
                </motion.span>
              ))}
            </div>
          </GlassCard>
        </motion.div>

        {isStreaming && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="streaming-container"
          >
            <GlassCard>
              <pre className="streaming-text">{streamingText}</pre>
              <div className="streaming-cursor">▊</div>
            </GlassCard>
          </motion.div>
        )}

        {!isStreaming && recipes.length > 0 && (
          <motion.div
            className="recipes-list"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            {recipes.map((recipe, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
              >
                <RecipeCard recipe={recipe} />
              </motion.div>
            ))}
          </motion.div>
        )}

        {!isStreaming && recipes.length === 0 && ingredients.length === 0 && (
          <div className="no-recipes">
            <p>No ingredients detected. Please take a photo first!</p>
          </div>
        )}
      </div>
    </div>
  )
}

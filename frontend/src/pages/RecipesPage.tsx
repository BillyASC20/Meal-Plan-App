import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate, useLocation } from 'react-router-dom'
import { GlassCard } from '../components/GlassCard'
import { GlassButton } from '../components/GlassButton'
import './RecipesPage.css'

interface Recipe {
  title: string
  meal_type: string
  ingredients: string[]
  steps: string[]
}

export const RecipesPage = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const [recipes, setRecipes] = useState<Recipe[]>([])
  const [ingredients, setIngredients] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null)

  useEffect(() => {
    const fetchRecipes = async () => {
      try {
        // Get ingredients from navigation state
        const ingredientsToUse = location.state?.ingredients || ['chicken', 'rice', 'vegetables']
        setIngredients(ingredientsToUse)
        
        // Call real backend with detected ingredients (port 5001)
        const response = await fetch('http://localhost:5001/generate-recipes', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            ingredients: ingredientsToUse
          })
        })
        
        const data = await response.json()
        
        if (data.status === 'success' && data.data?.recipes) {
          setRecipes(data.data.recipes)
        }
      } catch (error) {
        console.error('Failed to fetch recipes:', error)
      } finally {
        setTimeout(() => setLoading(false), 1000)
      }
    }

    fetchRecipes()
  }, [location.state])

  const getMealTypeColor = (mealType: string) => {
    const colors: Record<string, string> = {
      breakfast: 'rgba(251, 191, 36, 0.6)',
      lunch: 'rgba(59, 130, 246, 0.6)',
      dinner: 'rgba(147, 51, 234, 0.6)',
      snack: 'rgba(34, 197, 94, 0.6)',
      dessert: 'rgba(236, 72, 153, 0.6)',
      drink: 'rgba(14, 165, 233, 0.6)'
    }
    return colors[mealType.toLowerCase()] || 'rgba(100, 100, 100, 0.6)'
  }

  const getMealTypeEmoji = (mealType: string) => {
    const emojis: Record<string, string> = {
      breakfast: '🌅',
      lunch: '☀️',
      dinner: '🌙',
      snack: '🍿',
      dessert: '🍰',
      drink: '🥤'
    }
    return emojis[mealType.toLowerCase()] || '🍽️'
  }

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
        {/* Ingredients Used Section */}
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

        {/* Recipe Cards Grid */}
        <motion.div
          className="recipes-grid"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          {recipes.map((recipe, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 + idx * 0.1 }}
            >
              <GlassCard 
                hoverable
                onClick={() => setSelectedRecipe(recipe)}
                className="recipe-card"
              >
                <div className="recipe-header">
                  <span 
                    className="meal-badge"
                    style={{ background: getMealTypeColor(recipe.meal_type) }}
                  >
                    {getMealTypeEmoji(recipe.meal_type)} {recipe.meal_type}
                  </span>
                </div>
                <h3 className="recipe-title">{recipe.title}</h3>
                <div className="recipe-preview">
                  <div className="preview-section">
                    <span className="preview-label">🥘 Ingredients:</span>
                    <span className="preview-count">{recipe.ingredients.length}</span>
                  </div>
                  <div className="preview-section">
                    <span className="preview-label">📝 Steps:</span>
                    <span className="preview-count">{recipe.steps.length}</span>
                  </div>
                </div>
                <div className="recipe-action">
                  <span className="view-details">View Recipe →</span>
                </div>
              </GlassCard>
            </motion.div>
          ))}
        </motion.div>

        {/* Action Buttons */}
        <motion.div
          className="action-section"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
        >
          <GlassButton
            variant="secondary"
            onClick={() => navigate('/camera')}
          >
            ← Scan New Ingredients
          </GlassButton>
          <GlassButton
            onClick={() => window.location.reload()}
          >
            🔄 Generate New Recipes
          </GlassButton>
        </motion.div>
      </div>

      {/* Recipe Detail Modal */}
      <AnimatePresence>
        {selectedRecipe && (
          <motion.div
            className="modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSelectedRecipe(null)}
          >
            <motion.div
              className="modal-content"
              initial={{ scale: 0.8, y: 50 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.8, y: 50 }}
              onClick={(e) => e.stopPropagation()}
            >
              <GlassCard className="recipe-detail">
                <button 
                  className="close-button"
                  onClick={() => setSelectedRecipe(null)}
                >
                  ✕
                </button>
                
                <span 
                  className="meal-badge large"
                  style={{ background: getMealTypeColor(selectedRecipe.meal_type) }}
                >
                  {getMealTypeEmoji(selectedRecipe.meal_type)} {selectedRecipe.meal_type}
                </span>
                
                <h2 className="detail-title">{selectedRecipe.title}</h2>
                
                <div className="detail-section">
                  <h3 className="detail-heading">🥘 Ingredients</h3>
                  <ul className="detail-list">
                    {selectedRecipe.ingredients.map((ing, idx) => (
                      <motion.li
                        key={idx}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.05 }}
                      >
                        {ing}
                      </motion.li>
                    ))}
                  </ul>
                </div>
                
                <div className="detail-section">
                  <h3 className="detail-heading">📝 Instructions</h3>
                  <ol className="detail-list numbered">
                    {selectedRecipe.steps.map((step, idx) => (
                      <motion.li
                        key={idx}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.2 + idx * 0.05 }}
                      >
                        {step}
                      </motion.li>
                    ))}
                  </ol>
                </div>
              </GlassCard>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

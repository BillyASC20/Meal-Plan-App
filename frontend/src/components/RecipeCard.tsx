import { useState } from 'react'
import './RecipeCard.css'

interface Recipe {
  title: string
  meal_type: string
  cook_time: number
  servings: number
  difficulty: string
  ingredients: string[]
  steps: string[]
  tags: string[]
}

interface RecipeCardProps {
  recipe: Recipe
}

export default function RecipeCard({ recipe }: RecipeCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  const difficultyColor = {
    easy: '#4ade80',
    medium: '#fbbf24',
    hard: '#f87171'
  }[recipe.difficulty] || '#94a3b8'

  const mealTypeEmoji = {
    breakfast: '🍳',
    lunch: '🥗',
    dinner: '🍽️',
    snack: '🍿',
    dessert: '🍰',
    drink: '🥤'
  }[recipe.meal_type] || '🍴'

  return (
    <div className="recipe-card">
      <div 
        className="recipe-header"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="recipe-title-row">
          <span className="meal-emoji">{mealTypeEmoji}</span>
          <h3 className="recipe-title">{recipe.title}</h3>
          <span className={`expand-icon ${isExpanded ? 'expanded' : ''}`}>
            ▼
          </span>
        </div>
        <div className="recipe-meta">
          <span className="meta-badge" style={{ backgroundColor: difficultyColor }}>
            {recipe.difficulty}
          </span>
          <span className="meta-badge">⏱️ {recipe.cook_time}m</span>
          <span className="meta-badge">👥 {recipe.servings}</span>
        </div>
      </div>

      {isExpanded && (
        <div className="recipe-content">
          <div className="recipe-section">
            <h4>Ingredients</h4>
            <ul className="ingredients-list">
              {recipe.ingredients.map((ing, i) => (
                <li key={i}>{ing}</li>
              ))}
            </ul>
          </div>

          <div className="recipe-section">
            <h4>Instructions</h4>
            <ol className="steps-list">
              {recipe.steps.map((step, i) => (
                <li key={i}>{step}</li>
              ))}
            </ol>
          </div>

          {recipe.tags && recipe.tags.length > 0 && (
            <div className="recipe-tags">
              {recipe.tags.map((tag, i) => (
                <span key={i} className="tag">{tag}</span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

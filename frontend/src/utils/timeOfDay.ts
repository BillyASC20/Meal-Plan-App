/**
 * Utility functions for determining time of day and meal type
 */

export type TimeOfDay = 'morning' | 'afternoon' | 'evening'
export type MealType = 'breakfast' | 'lunch' | 'dinner'

/**
 * Get the current time of day based on local time
 */
export const getTimeOfDay = (): TimeOfDay => {
  const hour = new Date().getHours()
  
  if (hour >= 5 && hour < 12) {
    return 'morning'
  } else if (hour >= 12 && hour < 17) {
    return 'afternoon'
  } else {
    return 'evening'
  }
}

/**
 * Get the recommended meal type based on time of day
 */
export const getRecommendedMealType = (timeOfDay?: TimeOfDay): MealType => {
  const tod = timeOfDay || getTimeOfDay()
  
  switch (tod) {
    case 'morning':
      return 'breakfast'
    case 'afternoon':
      return 'lunch'
    case 'evening':
      return 'dinner'
  }
}

/**
 * Get a friendly greeting based on time of day
 */
export const getTimeGreeting = (timeOfDay?: TimeOfDay): string => {
  const tod = timeOfDay || getTimeOfDay()
  
  switch (tod) {
    case 'morning':
      return 'Good morning'
    case 'afternoon':
      return 'Good afternoon'
    case 'evening':
      return 'Good evening'
  }
}

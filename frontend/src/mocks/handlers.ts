import { http, HttpResponse } from 'msw'

export const handlers = [
  // Generate recipes endpoint
  http.get('/api/generate-recipes', () => {
    return HttpResponse.json({
      status: 'success',
      data: {
        ingredients: ['chicken', 'broccoli', 'rice', 'garlic'],
        recipes: [
          {
            title: 'Garlic Chicken with Broccoli',
            meal_type: 'dinner',
            ingredients: [
              '2 chicken breasts',
              '2 cups broccoli florets',
              '1 cup jasmine rice',
              '4 cloves garlic, minced',
              '2 tbsp soy sauce',
              '1 tbsp olive oil'
            ],
            steps: [
              'Cook rice according to package instructions',
              'Heat olive oil in a large pan over medium-high heat',
              'Season chicken with salt and pepper, cook until golden',
              'Add minced garlic and cook for 30 seconds',
              'Add broccoli and soy sauce, stir-fry for 5 minutes',
              'Serve over rice and enjoy!'
            ]
          },
          {
            title: 'Chicken Fried Rice',
            meal_type: 'lunch',
            ingredients: [
              '1 cup cooked rice',
              '1 chicken breast, diced',
              '1 cup broccoli, chopped',
              '3 cloves garlic, minced',
              '2 eggs',
              '3 tbsp soy sauce',
              '2 tbsp sesame oil'
            ],
            steps: [
              'Heat sesame oil in a wok over high heat',
              'Cook diced chicken until no longer pink',
              'Push chicken to the side, scramble eggs',
              'Add garlic and broccoli, stir-fry for 3 minutes',
              'Add rice and soy sauce, mix everything together',
              'Cook for 2-3 minutes until heated through'
            ]
          },
          {
            title: 'Garlic Butter Rice Bowl',
            meal_type: 'dinner',
            ingredients: [
              '2 cups cooked rice',
              '1 cup broccoli',
              '5 cloves garlic, sliced',
              '3 tbsp butter',
              'Salt and pepper to taste',
              'Parmesan cheese (optional)'
            ],
            steps: [
              'Steam broccoli until tender-crisp',
              'In a pan, melt butter and sauté garlic until golden',
              'Add cooked rice and toss to coat',
              'Add broccoli and season with salt and pepper',
              'Serve hot with parmesan if desired'
            ]
          }
        ]
      }
    })
  })
]

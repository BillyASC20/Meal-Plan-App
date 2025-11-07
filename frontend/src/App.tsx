import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { WelcomePage } from './pages/WelcomePage'
import { CameraPage } from './pages/CameraPage'
import { RecipesPage } from './pages/RecipesPage'
import './App.css'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<WelcomePage />} />
        <Route path="/camera" element={<CameraPage />} />
        <Route path="/recipes" element={<RecipesPage />} />
      </Routes>
    </Router>
  )
}

export default App

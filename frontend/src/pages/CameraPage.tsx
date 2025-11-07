import { useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { GlassCard } from '../components/GlassCard'
import { GlassButton } from '../components/GlassButton'
import './CameraPage.css'

export const CameraPage = () => {
  const navigate = useNavigate()
  const [isDetecting, setIsDetecting] = useState(false)
  const [detectedItems, setDetectedItems] = useState<string[]>([])
  const [uploadedImage, setUploadedImage] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onloadend = () => {
        setUploadedImage(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const triggerFileInput = () => {
    fileInputRef.current?.click()
  }

  const detectIngredients = async () => {
    if (!uploadedImage) return
    
    setIsDetecting(true)
    
    try {
      // Call real backend with YOLOv8 detection (port 5001 to avoid AirPlay conflict)
      const response = await fetch('http://localhost:5001/detect-ingredients', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image: uploadedImage // Already in base64 format
        })
      })
      
      const data = await response.json()
      
      if (data.status === 'success' && data.data?.ingredients) {
        setDetectedItems(data.data.ingredients)
      } else {
        console.error('Detection failed:', data.message)
        // Fallback to mock data
        setDetectedItems(['chicken', 'broccoli', 'rice', 'garlic'])
      }
    } catch (error) {
      console.error('Error detecting ingredients:', error)
      // Fallback to mock data if backend is down
      setDetectedItems(['chicken', 'broccoli', 'rice', 'garlic'])
    } finally {
      setIsDetecting(false)
    }
  }

  const generateRecipes = async () => {
    // Navigate to results page with detected ingredients
    navigate('/recipes', { state: { ingredients: detectedItems } })
  }

  return (
    <div className="camera-page">
      <div className="camera-header">
        <button className="back-button" onClick={() => navigate('/')}>
          ← Back
        </button>
        <h1 className="camera-title">Upload Ingredients</h1>
        <div className="spacer"></div>
      </div>

      <div className="camera-content">
        <GlassCard className="camera-container">
          <div className="camera-view">
            {!uploadedImage ? (
              <motion.div 
                className="upload-placeholder"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                <div className="upload-icon-container">
                  <svg className="upload-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M17 8L12 3L7 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M12 3V15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <h2>Upload Your Ingredients Photo</h2>
                <p>Take a photo of your fridge or pantry</p>
                
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  capture="environment"
                  onChange={handleImageUpload}
                  style={{ display: 'none' }}
                />
                
                <div className="upload-buttons">
                  <GlassButton onClick={triggerFileInput} size="large">
                    📷 Take Photo / Upload
                  </GlassButton>
                </div>
              </motion.div>
            ) : (
              <motion.div 
                className="image-preview"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
              >
                <img src={uploadedImage} alt="Uploaded ingredients" className="uploaded-img" />
                <div className="image-overlay">
                  {!isDetecting && detectedItems.length === 0 && (
                    <GlassButton 
                      onClick={detectIngredients}
                      size="large"
                    >
                      Detect Ingredients
                    </GlassButton>
                  )}
                </div>
              </motion.div>
            )}
          </div>

          {isDetecting && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="detecting-overlay"
            >
              <div className="scanning-container">
                <div className="scanning-animation">
                  <div className="scan-line"></div>
                  <div className="scan-pulse"></div>
                </div>
                <svg className="ai-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="currentColor" opacity="0.2"/>
                  <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="2" fill="none"/>
                </svg>
              </div>
              <p className="detecting-text">Analyzing ingredients...</p>
            </motion.div>
          )}
        </GlassCard>

        {detectedItems.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="detected-section"
          >
            <GlassCard>
              <h2 className="detected-title">Detected Ingredients</h2>
              <div className="detected-grid">
                {detectedItems.map((item, idx) => (
                  <motion.div
                    key={item}
                    className="detected-item"
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: idx * 0.1 }}
                  >
                    <div className="item-icon">
                      <div className="ingredient-badge">
                        {item.charAt(0).toUpperCase()}
                      </div>
                    </div>
                    <span className="item-name">{item}</span>
                    <svg className="check-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M20 6L9 17L4 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </motion.div>
                ))}
              </div>
              <div className="action-buttons">
                <GlassButton
                  variant="secondary"
                  onClick={() => {
                    setDetectedItems([])
                    setUploadedImage(null)
                  }}
                >
                  Upload New Photo
                </GlassButton>
                <GlassButton
                  onClick={generateRecipes}
                  size="large"
                >
                  Generate Recipes →
                </GlassButton>
              </div>
            </GlassCard>
          </motion.div>
        )}
      </div>
    </div>
  )
}

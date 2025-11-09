import { useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { GlassCard } from '../components/GlassCard'
import { GlassButton } from '../components/GlassButton'
import Navbar from '../components/Navbar'
import './CameraPage.css'
import { api } from '../components/api'

export const CameraPage = () => {
  const navigate = useNavigate()
  const [isDetecting, setIsDetecting] = useState(false)
  const [detectedItems, setDetectedItems] = useState<string[]>([])
  const [uploadedImage, setUploadedImage] = useState<string | null>(null)
  const [predictions, setPredictions] = useState<{name: string, confidence: number}[]>([])
  const [hasDetected, setHasDetected] = useState(false) // Track if detection has been run
  const [isDragging, setIsDragging] = useState(false) // Track drag state
  const [showAuthModal, setShowAuthModal] = useState(false) // Track auth modal
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onloadend = () => {
        setUploadedImage(reader.result as string)
        setDetectedItems([]) // Clear previous detection
        setHasDetected(false) // Reset detection state
        setPredictions([])
      }
      reader.readAsDataURL(file)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    const file = e.dataTransfer.files?.[0]
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onloadend = () => {
        setUploadedImage(reader.result as string)
        setDetectedItems([])
        setHasDetected(false)
        setPredictions([])
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
    setHasDetected(true) // Mark that detection has been run
    try {
      const result = await api.detectIngredients(uploadedImage)
      
      setPredictions(result.predictions || [])
      const allNames = (result.predictions || []).map(p => p.name)
      
      if (result.image_with_boxes) {
        setUploadedImage(result.image_with_boxes)
      }
      
      if (allNames.length > 0) {
        setDetectedItems(allNames)
        sessionStorage.setItem('detectedIngredients', JSON.stringify(allNames))
      } else {
        setDetectedItems([]) // empty list -> UI will show nothing detected message
      }
    } catch (err: any) {
      console.error('Error detecting ingredients:', err)
      if (err.message === 'Authentication required') {
        setShowAuthModal(true)
        setIsDetecting(false)
        return
      }
      setDetectedItems([])
    } finally {
      setIsDetecting(false)
    }
  }

  const generateRecipes = async () => {
    if (detectedItems.length > 0 && uploadedImage) {
      try {
        setIsDetecting(true)
        
        const imageUrl = await api.uploadImage(uploadedImage)
        console.log('Image uploaded:', imageUrl)
        
        navigate('/recipes', { 
          state: { 
            ingredients: detectedItems,
            imageUrl: imageUrl
          } 
        })
      } catch (err) {
        console.error('Error uploading image:', err)
        navigate('/recipes', { state: { ingredients: detectedItems } })
      } finally {
        setIsDetecting(false)
      }
    } else {
      const saved = sessionStorage.getItem('detectedIngredients')
      const parsed = saved ? (JSON.parse(saved) as string[]) : []
      navigate('/recipes', { state: { ingredients: parsed } })
    }
  }

  return (
    <div className="camera-page">
      <Navbar />
      
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
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                style={{
                  border: isDragging ? '2px dashed rgba(139, 92, 246, 0.8)' : '2px dashed rgba(255, 255, 255, 0.2)',
                  backgroundColor: isDragging ? 'rgba(139, 92, 246, 0.1)' : 'transparent',
                  transition: 'all 0.3s ease'
                }}
              >
                <div className="upload-icon-container">
                  <svg className="upload-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M17 8L12 3L7 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M12 3V15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <h2>{isDragging ? 'Drop your image here!' : 'Upload Your Ingredients Photo'}</h2>
                <p>{isDragging ? 'Release to upload' : 'Take a photo of your fridge or pantry'}</p>
                
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
                  {!isDetecting && !hasDetected && (
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
              <div className="spinner-container">
                <div className="gold-spinner"></div>
              </div>
              <p className="detecting-text">Analyzing ingredients...</p>
            </motion.div>
          )}
        </GlassCard>

        {hasDetected && detectedItems.length === 0 && !isDetecting && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <GlassCard>
              <div style={{ textAlign: 'center', padding: '20px' }}>
                <p style={{ fontSize: '16px', opacity: 0.8 }}>
                  No ingredients detected. Try uploading a clearer image with visible food items.
                </p>
              </div>
            </GlassCard>
          </motion.div>
        )}

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
                    <span className="item-name">
                      {item}
                      {(() => {
                        const p = predictions.find(pr => pr.name === item)
                        return p ? `  ${(p.confidence*100).toFixed(1)}%` : ''
                      })()}
                    </span>
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
        {uploadedImage && !isDetecting && detectedItems.length === 0 && hasDetected && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="detected-section"
          >
            <GlassCard>
              <h2 className="detected-title">Nothing Detected</h2>
              <p style={{ marginTop: '8px', opacity: 0.8 }}>Try a clearer photo or different angle. Make sure the food is well lit.</p>
              <div className="action-buttons" style={{ marginTop: '16px' }}>
                <GlassButton
                  variant="secondary"
                  onClick={() => {
                    setDetectedItems([])
                    setUploadedImage(null)
                    setHasDetected(false)
                  }}
                >
                  Upload New Photo
                </GlassButton>
              </div>
            </GlassCard>
          </motion.div>
        )}
      </div>

      {/* Authentication Required Modal */}
      {showAuthModal && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.7)',
            backdropFilter: 'blur(8px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
          }}
          onClick={() => setShowAuthModal(false)}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.2 }}
            onClick={(e) => e.stopPropagation()}
            style={{
              background: 'rgba(20, 20, 40, 0.95)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '16px',
              padding: '32px',
              maxWidth: '400px',
              width: '90%',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)'
            }}
          >
            <h2 style={{ 
              fontSize: '24px', 
              marginBottom: '16px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              Authentication Required
            </h2>
            <p style={{ 
              color: 'rgba(255, 255, 255, 0.8)', 
              marginBottom: '24px',
              lineHeight: '1.6'
            }}>
              You need to be logged in to use this feature. Please log in or create an account to continue.
            </p>
            <div style={{ display: 'flex', gap: '12px', flexDirection: 'column' }}>
              <div style={{ width: '100%' }}>
                <GlassButton
                  onClick={() => navigate('/login')}
                >
                  Log In
                </GlassButton>
              </div>
              <div style={{ width: '100%' }}>
                <GlassButton
                  variant="secondary"
                  onClick={() => navigate('/signup')}
                >
                  Sign Up
                </GlassButton>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  )
}

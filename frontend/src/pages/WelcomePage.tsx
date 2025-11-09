import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { GlassButton } from '../components/GlassButton'
import Navbar from '../components/Navbar'
import './WelcomePage.css'

export const WelcomePage = () => {
  const navigate = useNavigate()

  const fadeInUp = {
    initial: { opacity: 0, y: 60 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.6 }
  }

  const stagger = {
    animate: {
      transition: {
        staggerChildren: 0.1
      }
    }
  }

  return (
    <div className="welcome-page">
      <Navbar />
      
      {/* Animated background blobs */}
      <div className="blob blob-1"></div>
      <div className="blob blob-2"></div>
      <div className="blob blob-3"></div>

      <motion.div 
        className="welcome-content"
        variants={stagger}
        initial="initial"
        animate="animate"
      >
        {/* Logo/Icon */}
        <motion.div 
          className="welcome-icon"
          {...fadeInUp}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <svg viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
            {/* Modern geometric logo - hexagon with inner shapes */}
            <path 
              d="M60 10 L95 30 L95 70 L60 90 L25 70 L25 30 Z" 
              stroke="url(#modernGradient)" 
              strokeWidth="2" 
              fill="none"
              opacity="0.6"
            />
            <path 
              d="M60 25 L82 37.5 L82 62.5 L60 75 L38 62.5 L38 37.5 Z" 
              stroke="url(#modernGradient)" 
              strokeWidth="2.5" 
              fill="url(#fillGradient)"
              opacity="0.4"
            />
            
            {/* Center accent */}
            <circle 
              cx="60" 
              cy="50" 
              r="12" 
              fill="none" 
              stroke="url(#accentGradient)" 
              strokeWidth="2"
            />
            <circle 
              cx="60" 
              cy="50" 
              r="6" 
              fill="url(#accentGradient)" 
              opacity="0.8"
            />
            
            <defs>
              <linearGradient id="modernGradient" x1="25" y1="10" x2="95" y2="90" gradientUnits="userSpaceOnUse">
                <stop stopColor="#00d4aa"/>
                <stop offset="0.5" stopColor="#0052ff"/>
                <stop offset="1" stopColor="#7c3aed"/>
              </linearGradient>
              <linearGradient id="fillGradient" x1="38" y1="25" x2="82" y2="75" gradientUnits="userSpaceOnUse">
                <stop stopColor="#00d4aa" stopOpacity="0.15"/>
                <stop offset="1" stopColor="#0052ff" stopOpacity="0.1"/>
              </linearGradient>
              <linearGradient id="accentGradient" x1="48" y1="38" x2="72" y2="62" gradientUnits="userSpaceOnUse">
                <stop stopColor="#00d4aa"/>
                <stop offset="1" stopColor="#0052ff"/>
              </linearGradient>
            </defs>
          </svg>
        </motion.div>

        {/* Title */}
        <motion.h1 
          className="welcome-title"
          {...fadeInUp}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          Meal Plan
        </motion.h1>

        {/* Subtitle */}
        <motion.p 
          className="welcome-subtitle"
          {...fadeInUp}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          AI-powered recipe generation from your ingredients
        </motion.p>

        {/* Features */}
        <motion.div 
          className="welcome-features"
          {...fadeInUp}
          transition={{ duration: 0.6, delay: 0.5 }}
        >
          <div className="feature-item">
            <div className="feature-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M23 19C23 19.5304 22.7893 20.0391 22.4142 20.4142C22.0391 20.7893 21.5304 21 21 21H3C2.46957 21 1.96086 20.7893 1.58579 20.4142C1.21071 20.0391 1 19.5304 1 19V8C1 7.46957 1.21071 6.96086 1.58579 6.58579C1.96086 6.21071 2.46957 6 3 6H7L9 3H15L17 6H21C21.5304 6 22.0391 6.21071 22.4142 6.58579C22.7893 6.96086 23 7.46957 23 8V19Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <circle cx="12" cy="13" r="4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <span className="feature-text">Upload photo</span>
          </div>
          <div className="feature-item">
            <div className="feature-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="currentColor" opacity="0.3"/>
                <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="2"/>
              </svg>
            </div>
            <span className="feature-text">AI detects food</span>
          </div>
          <div className="feature-item">
            <div className="feature-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                <path d="M12 6V12L16 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                <path d="M8 2H16M8 22H16" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </div>
            <span className="feature-text">Get recipes</span>
          </div>
        </motion.div>

        {/* CTA Button */}
        <motion.div
          {...fadeInUp}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          <GlassButton 
            size="large"
            onClick={() => navigate('/camera')}
            className="welcome-cta"
          >
            Get Started →
          </GlassButton>
        </motion.div>

        {/* Footer text */}
        <motion.p 
          className="welcome-footer"
          {...fadeInUp}
          transition={{ duration: 0.6, delay: 0.7 }}
        >
          Smart meal planning with AI
        </motion.p>
      </motion.div>
    </div>
  )
}

import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { GlassButton } from '../components/GlassButton'
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
            {/* Elegant plate with utensils */}
            <circle cx="60" cy="60" r="45" fill="url(#plateGradient)" opacity="0.15"/>
            <circle cx="60" cy="60" r="35" stroke="url(#goldGradient)" strokeWidth="2" fill="none"/>
            
            {/* Fork */}
            <path d="M40 45 L40 55 M43 45 L43 55 M46 45 L46 55 M43 55 L43 70" stroke="url(#goldGradient)" strokeWidth="2" strokeLinecap="round"/>
            
            {/* Knife */}
            <path d="M77 45 L77 70 M77 45 L74 48" stroke="url(#goldGradient)" strokeWidth="2" strokeLinecap="round"/>
            
            {/* Elegant center decoration */}
            <circle cx="60" cy="60" r="8" fill="none" stroke="url(#goldGradient)" strokeWidth="1.5"/>
            <path d="M60 52 L60 68 M52 60 L68 60" stroke="url(#goldGradient)" strokeWidth="1.5" strokeLinecap="round"/>
            
            <defs>
              <linearGradient id="goldGradient" x1="20" y1="20" x2="100" y2="100" gradientUnits="userSpaceOnUse">
                <stop stopColor="#d4af37"/>
                <stop offset="1" stopColor="#ffd700"/>
              </linearGradient>
              <linearGradient id="plateGradient" x1="15" y1="15" x2="105" y2="105" gradientUnits="userSpaceOnUse">
                <stop stopColor="#d4af37" stopOpacity="0.3"/>
                <stop offset="1" stopColor="#ffd700" stopOpacity="0.1"/>
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
          No sign up required • Free to use
        </motion.p>
      </motion.div>
    </div>
  )
}

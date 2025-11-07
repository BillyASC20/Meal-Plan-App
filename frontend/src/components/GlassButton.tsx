import { ButtonHTMLAttributes } from 'react'
import { motion } from 'framer-motion'
import './GlassButton.css'

interface GlassButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary';
  size?: 'small' | 'medium' | 'large';
  isLoading?: boolean;
}

export const GlassButton = ({ 
  children, 
  variant = 'primary', 
  size = 'medium',
  isLoading = false,
  className = '',
  ...props 
}: GlassButtonProps) => {
  return (
    <motion.button
      className={`glass-button glass-button-${variant} glass-button-${size} ${className}`}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      {...props}
    >
      {isLoading ? (
        <div className="loader" />
      ) : (
        children
      )}
    </motion.button>
  )
}

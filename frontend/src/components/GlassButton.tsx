import type { ButtonHTMLAttributes, ReactNode } from 'react'
import { motion } from 'framer-motion'
import './GlassButton.css'

// Restrict passthrough props to avoid conflicts with framer-motion HTMLMotionProps typing
interface GlassButtonProps {
  children: ReactNode;
  variant?: 'primary' | 'secondary';
  size?: 'small' | 'medium' | 'large';
  isLoading?: boolean;
  className?: string;
  type?: ButtonHTMLAttributes<HTMLButtonElement>['type'];
  disabled?: boolean;
  onClick?: ButtonHTMLAttributes<HTMLButtonElement>['onClick'];
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
      type={props.type}
      disabled={props.disabled}
      onClick={props.onClick}
    >
      {isLoading ? (
        <div className="loader" />
      ) : (
        children
      )}
    </motion.button>
  )
}

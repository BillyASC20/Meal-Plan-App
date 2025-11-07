import { ReactNode } from 'react'
import { motion } from 'framer-motion'
import './GlassCard.css'

interface GlassCardProps {
  children: ReactNode;
  className?: string;
  onClick?: () => void;
  hoverable?: boolean;
}

export const GlassCard = ({ children, className = '', onClick, hoverable = false }: GlassCardProps) => {
  return (
    <motion.div
      className={`glass-card ${hoverable ? 'hoverable' : ''} ${className}`}
      onClick={onClick}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      whileHover={hoverable ? { scale: 1.02, y: -5 } : {}}
    >
      {children}
    </motion.div>
  )
}

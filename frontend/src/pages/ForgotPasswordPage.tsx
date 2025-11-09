import { useState } from 'react'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import Navbar from '../components/Navbar'
import { resetPassword } from '../services/supabase'
import './AuthPages.css'

export const ForgotPasswordPage = () => {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await resetPassword(email)
      setSuccess(true)
    } catch (err: any) {
      setError(err.message || 'An error occurred. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <Navbar />
      
      <div className="auth-container">
        <motion.div 
          className="auth-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="auth-header">
            <h1 className="auth-title">Reset Password</h1>
            <p className="auth-subtitle">
              {success 
                ? 'Check your email for a reset link' 
                : 'Enter your email to receive a password reset link'
              }
            </p>
          </div>

          {!success ? (
            <form className="auth-form" onSubmit={handleResetPassword}>
              {error && (
                <motion.div 
                  className="auth-error"
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  {error}
                </motion.div>
              )}

              <div className="auth-field">
                <label htmlFor="email" className="auth-label">Email</label>
                <input
                  id="email"
                  type="email"
                  className="auth-input"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoComplete="email"
                />
              </div>

              <button 
                type="submit" 
                className="auth-button"
                disabled={loading}
              >
                {loading ? 'Sending...' : 'Send Reset Link'}
              </button>
            </form>
          ) : (
            <motion.div 
              className="auth-success"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <svg className="auth-success-icon" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                <path d="M8 12L11 15L16 9" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
              <p className="auth-success-text">
                We've sent a password reset link to <strong>{email}</strong>
              </p>
            </motion.div>
          )}

          <div className="auth-footer">
            <p className="auth-footer-text">
              <Link to="/login" className="auth-link">
                ← Back to Sign In
              </Link>
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

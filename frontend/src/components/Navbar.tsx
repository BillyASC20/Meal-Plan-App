import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { signOut, getAccessToken } from '../services/supabase';
import './Navbar.css';

interface NavbarProps {
  isSignedIn?: boolean;
}

export default function Navbar({ isSignedIn }: NavbarProps) {
  const navigate = useNavigate();
  const [showMenu, setShowMenu] = useState(false);
  const [authState, setAuthState] = useState(false);

  useEffect(() => {
    const checkAuth = () => {
      const token = getAccessToken();
      console.log('Navbar - checking auth, token:', token);
      const isAuth = isSignedIn ?? !!token;
      console.log('Navbar - authState:', isAuth);
      setAuthState(isAuth);
    };
    
    checkAuth();
    
    const handleStorageChange = () => {
      console.log('Navbar - storage changed');
      checkAuth();
    };
    
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [isSignedIn]);

  const handleSignIn = () => {
    navigate('/login');
  };

  const handleSignUp = () => {
    navigate('/signup');
  };

  const handleSignOut = async () => {
    try {
      await signOut();
      setAuthState(false);
      navigate('/');
    } catch (error) {
      console.error('Sign out error:', error);
    }
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-logo" onClick={() => navigate('/')}>
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
            <path
              d="M12 2L2 7V17L12 22L22 17V7L12 2Z"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M12 12L2 7"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M12 12V22"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M22 7L12 12"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <span className="navbar-brand">MealPlan</span>
        </div>

        <div className="navbar-actions">
          {!authState ? (
            <>
              <button className="navbar-btn navbar-btn-ghost" onClick={handleSignIn}>
                Sign In
              </button>
              <button className="navbar-btn navbar-btn-primary" onClick={handleSignUp}>
                Sign Up
              </button>
            </>
          ) : (
            <>
              <button className="navbar-btn navbar-btn-ghost" onClick={() => navigate('/history')}>
                📖 History
              </button>
              <button className="navbar-btn navbar-btn-ghost" onClick={handleSignOut}>
                Sign Out
              </button>
            </>
          )}
        </div>

        {/* Mobile menu toggle */}
        <button 
          className="navbar-menu-toggle"
          onClick={() => setShowMenu(!showMenu)}
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path
              d="M3 12H21M3 6H21M3 18H21"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
        </button>
      </div>

      {/* Mobile menu */}
      {showMenu && (
        <div className="navbar-mobile-menu">
          {!authState ? (
            <>
              <button className="navbar-btn navbar-btn-ghost" onClick={handleSignIn}>
                Sign In
              </button>
              <button className="navbar-btn navbar-btn-primary" onClick={handleSignUp}>
                Sign Up
              </button>
            </>
          ) : (
            <>
              <button className="navbar-btn navbar-btn-ghost" onClick={() => navigate('/history')}>
                📖 History
              </button>
              <button className="navbar-btn navbar-btn-ghost" onClick={handleSignOut}>
                Sign Out
              </button>
            </>
          )}
        </div>
      )}
    </nav>
  );
}

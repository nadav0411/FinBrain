/* AuthSwitcher.jsx */

import React, { useState } from 'react';
import LoginModal from './LoginModal';
import SignupModal from './SignupModal';
import MainScreen from './MainScreen';

/**
 * AuthSwitcher - Main authentication component that manages the flow between
 * login, signup, and the main application screen
 */
function AuthSwitcher() {
  // State to track which authentication mode we're in (login vs signup)
  const [isSignupMode, setIsSignupMode] = useState(false);
  // State to track if user is successfully authenticated
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  
  // Helper functions to switch between login and signup modes
  const goToSignup = () => setIsSignupMode(true);
  const goToLogin = () => setIsSignupMode(false);

  return (
    <>
      {/* Conditional rendering based on authentication state */}
      {isLoggedIn ? (
        // If user is logged in, show the main application
        <MainScreen />
      ) : (
        // If not logged in, show either signup or login modal
        isSignupMode ? (
          <SignupModal onBackToLogin={goToLogin} />
        ) : (
          <LoginModal 
            onGoToSignup={goToSignup} 
            onLoginSuccess={() => setIsLoggedIn(true)} 
          />
        )
      )}
    </>
  );
}

export default AuthSwitcher;

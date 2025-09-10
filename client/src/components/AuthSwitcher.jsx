import React, { useState } from 'react';
import LoginModal from './LoginModal';
import SignupModal from './SignupModal';
import MainScreen from './MainScreen';

function AuthSwitcher() {
  const [isSignupMode, setIsSignupMode] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  
  const goToSignup = () => setIsSignupMode(true);
  const goToLogin = () => setIsSignupMode(false);

  return (
    <>
      {isLoggedIn ? (
        <MainScreen />
      ) : (
        isSignupMode ? (
          <SignupModal onBackToLogin={goToLogin} />
        ) : (
          <LoginModal onGoToSignup={goToSignup} onLoginSuccess={() => setIsLoggedIn(true)} />
        )
      )}
    </>
  );
}

export default AuthSwitcher;

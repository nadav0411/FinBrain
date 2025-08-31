import React, { useState } from 'react';
import LoginModal from './LoginModal';
import SignupModal from './SignupModal';

/**
 * This component switches between Login and Signup modals.
 * It shows one of them based on internal state.
 */
function AuthSwitcher() {
  const [isSignupMode, setIsSignupMode] = useState(false);

  // Switch to Signup
  const goToSignup = () => setIsSignupMode(true);

  // Switch back to Login
  const goToLogin = () => setIsSignupMode(false);

  return (
    <>
      {isSignupMode ? (
        <SignupModal onBackToLogin={goToLogin} />
      ) : (
        <LoginModal onGoToSignup={goToSignup} />
      )}
    </>
  );
}

export default AuthSwitcher;

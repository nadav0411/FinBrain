/* AuthSwitcher.jsx */

import React, { useEffect, useState } from 'react';
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
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('session_id'));

  // On mount, set up a beforeunload handler to notify backend and clear local storage on surprise exit
  useEffect(() => {
    let heartbeatInterval;

    const startHeartbeat = () => {
      const send = async () => {
        const sessionId = localStorage.getItem('session_id');
        if (!sessionId) return;
        try {
          await fetch(`${import.meta.env.VITE_API_URL}/heartbeat`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Session-ID': sessionId
            }
          });
        } catch (e) {
          // ignore transient errors
        }
      };
      // fire immediately, then every 1 minute (keep TTL 15m fresh)
      send();
      heartbeatInterval = setInterval(send, 0.5 * 60 * 1000);
    };

    const stopHeartbeat = () => {
      if (heartbeatInterval) clearInterval(heartbeatInterval);
      heartbeatInterval = undefined;
    };

    if (localStorage.getItem('session_id')) {
      startHeartbeat();
    }

    const handleBeforeUnload = (event) => {
      const sessionId = localStorage.getItem('session_id');
      if (!sessionId) return;

      try {
        // Use sendBeacon when available for reliability during unload
        const url = `${import.meta.env.VITE_API_URL}/logout`;
        const headers = { 'Session-ID': sessionId };
        const body = JSON.stringify({});

        if (navigator.sendBeacon) {
          const blob = new Blob([body], { type: 'application/json' });
          // Note: sendBeacon doesn't allow custom headers; include session in query as fallback
          navigator.sendBeacon(`${url}?session_id=${encodeURIComponent(sessionId)}`, blob);
        } else {
          navigator.fetch(url, {
            method: 'POST',
            keepalive: true,
            headers: {
              'Content-Type': 'application/json',
              'Session-ID': sessionId
            },
            body
          });
        }
      } catch (e) {
        // ignore errors on unload
      }

      // Clear storage promptly
      localStorage.removeItem('session_id');
      localStorage.removeItem('user_name');
      stopHeartbeat();
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      stopHeartbeat();
    };
  }, [isLoggedIn]);
  
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

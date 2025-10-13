// FinBrain Project - AuthSwitcher.jsx - MIT License (c) 2025 Nadav Eshed


import React, { useEffect, useState } from 'react';
import LoginModal from './LoginModal';
import SignupModal from './SignupModal';
import MainScreen from './MainScreen';

/**
 * AuthSwitcher Component - The main router for authentication
 * 
 * This component decides what to show the user:
 * - If not logged in → show login or signup forms
 * - If logged in → show the main application screen
 * 
 * It also handles:
 * - Heartbeat requests to keep the session alive
 * - Cleanup when the user closes the browser tab
 */
function AuthSwitcher() {
  // State to control which form is shown (login vs signup)
  const [isSignupMode, setIsSignupMode] = useState(false);

  // State to track if user is logged in
  // We check localStorage for a session_id to determine login status
  const [isLoggedIn, setIsLoggedIn] = useState(
    !!localStorage.getItem('session_id') // !! converts to boolean (true if session exists)
  );

  /**
   * useEffect - Sets up session management when component loads
   * 
   * This effect handles:
   * 1. Heartbeat requests to keep the session alive
   * 2. Logout cleanup when user closes browser tab
   * 3. Listening for logout events from other components
   */
  useEffect(() => {
    let heartbeatInterval; // Store the interval timer reference

    /**
     * startHeartbeat - Begins sending heartbeat requests to the server
     * 
     * Heartbeat requests tell the server "I'm still here" to prevent
     * the session from expiring due to inactivity
     */
    const startHeartbeat = () => {
      const sendHeartbeat = async () => {
        const sessionId = localStorage.getItem('session_id');
        if (!sessionId) return; // No session to keep alive

        try {
          // Send heartbeat request to server
          await fetch(`${import.meta.env.VITE_API_URL}/heartbeat`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Session-ID': sessionId,
            },
          });
        } catch (error) {
          // Ignore network errors - they don't affect the user experience
          // The session will be handled by the server's own timeout logic
        }
      };

      sendHeartbeat(); // Send heartbeat immediately
      heartbeatInterval = setInterval(sendHeartbeat, 30 * 1000); // Then every 30 seconds
    };

    /**
     * stopHeartbeat - Stops sending heartbeat requests
     * 
     * This is called when the user logs out or the component is removed
     */
    const stopHeartbeat = () => {
      if (heartbeatInterval) {
        clearInterval(heartbeatInterval);
        heartbeatInterval = undefined;
      }
    };

    /**
     * handleLogout - Called when user logs out from another component
     * 
     * This stops heartbeat requests and updates the login state
     */
    const handleLogout = () => {
      stopHeartbeat();
      setIsLoggedIn(false);
    };

    /**
     * handleBeforeUnload - Called when user closes browser tab or refreshes
     * 
     * This ensures the server knows the user is logging out, even if the
     * browser tab is closing quickly
     */
    const handleBeforeUnload = () => {
      const sessionId = localStorage.getItem('session_id');
      if (!sessionId) return; // No session to logout

      try {
        const url = `${import.meta.env.VITE_API_URL}/logout`;

        // Use sendBeacon if available - it works even when tab is closing
        if (navigator.sendBeacon) {
          const blob = new Blob([JSON.stringify({})], {
            type: 'application/json',
          });
          navigator.sendBeacon(
            `${url}?session_id=${encodeURIComponent(sessionId)}`,
            blob
          );
        } else {
          // Fallback: use fetch with keepalive flag
          fetch(url, {
            method: 'POST',
            keepalive: true, // This ensures the request completes even if tab closes
            headers: {
              'Content-Type': 'application/json',
              'Session-ID': sessionId,
            },
            body: JSON.stringify({}),
          });
        }
      } catch (error) {
        // It's okay if logout fails - the tab is closing anyway
      }

      // Clean up local storage
      localStorage.removeItem('session_id');
      localStorage.removeItem('user_name');
      stopHeartbeat();
    };

    // Set up event listeners
    window.addEventListener('userLoggedOut', handleLogout);
    window.addEventListener('beforeunload', handleBeforeUnload);

    // Start heartbeat if user is already logged in
    if (localStorage.getItem('session_id')) {
      startHeartbeat();
    }

    // Cleanup function - runs when component is removed
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      window.removeEventListener('userLoggedOut', handleLogout);
      stopHeartbeat();
    };
  }, [isLoggedIn]); // Re-run this effect when login state changes

  // ====== HELPER FUNCTIONS ======

  /**
   * goToSignup - Switches to signup mode
   * 
   * This shows the signup form instead of the login form
   */
  const goToSignup = () => setIsSignupMode(true);

  /**
   * goToLogin - Switches to login mode
   * 
   * This shows the login form instead of the signup form
   */
  const goToLogin = () => setIsSignupMode(false);

  // ====== RENDER ======
  return (
    <>
      {isLoggedIn ? (
        // User is logged in - show the main application
        <MainScreen />
      ) : isSignupMode ? (
        // User is not logged in and wants to sign up
        <SignupModal onBackToLogin={goToLogin} />
      ) : (
        // User is not logged in and wants to log in (default)
        <LoginModal
          onGoToSignup={goToSignup}
          onLoginSuccess={() => {
            setIsLoggedIn(true);
            // Tell other components that user logged in
            window.dispatchEvent(new CustomEvent('userLoggedIn'));
          }}
        />
      )}
    </>
  );
}

export default AuthSwitcher;

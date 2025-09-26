// App.jsx - The main component that controls the entire application


import React, { useEffect, useRef, useState } from 'react';
import AuthSwitcher from './components/AuthSwitcher.jsx';

/**
 * App Component - The root component of our application
 * 
 * This component handles:
 * 1. Session timeout (automatically logs out inactive users)
 * 2. Warning system (shows countdown before logout)
 * 3. User activity detection (resets timer when user is active)
 */
function App() {
  // ====== TIMING CONFIGURATION ======
  // These constants define how long users can be inactive before logout
  const INACTIVITY_TIMEOUT_MS = 5 * 60 * 1000; // 5 minutes = 300,000 milliseconds
  const WARNING_OFFSET_MS = 4 * 60 * 1000;     // Show warning after 4 minutes
  const COUNTDOWN_SECONDS = 60;                // Countdown lasts 60 seconds

  // ====== TIMER REFERENCES ======
  // useRef stores values that don't trigger re-renders when changed
  // Perfect for timers because we don't want the UI to update every second
  const inactivityTimerRef = useRef(null);      // Main logout timer
  const warningTimerRef = useRef(null);         // Warning popup timer
  const countdownIntervalRef = useRef(null);    // Countdown animation timer
  const showWarningRef = useRef(false);         // Tracks if warning is showing

  // ====== STATE VARIABLES ======
  // useState creates variables that trigger re-renders when changed
  // We use these for things that need to update the UI
  const [showWarning, setShowWarning] = useState(false); // Controls warning popup visibility
  const [secondsLeft, setSecondsLeft] = useState(COUNTDOWN_SECONDS); // Countdown number

  // ====== HELPER FUNCTIONS ======

  /**
   * sendLogout - Logs out the user by clearing their session
   * 
   * This function:
   * 1. Tells the server to end the session
   * 2. Removes session data from browser storage
   * 3. Notifies other components that user logged out
   */
  const sendLogout = async () => {
    try {
      // Get the session ID from browser storage
      const sessionId = localStorage.getItem('session_id');
      if (!sessionId) return; // No session to logout

      // Tell the server to end this session
      await fetch(`${import.meta.env.VITE_API_URL}/logout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Session-ID': sessionId,
        },
      });
    } catch (error) {
      // If server request fails, we still want to logout locally
      console.error('Logout request failed:', error);
    } finally {
      // Always clean up local data, even if server request failed
      localStorage.removeItem('session_id');
      // Tell other components that user logged out
      window.dispatchEvent(new CustomEvent('userLoggedOut'));
    }
  };

  /**
   * scheduleInactivityTimer - Starts the main logout timer
   * 
   * This timer will automatically log out the user after 5 minutes of inactivity
   */
  const scheduleInactivityTimer = () => {
    // Clear any existing timer first
    if (inactivityTimerRef.current) clearTimeout(inactivityTimerRef.current);

    // Start new timer that will call sendLogout after 5 minutes
    inactivityTimerRef.current = setTimeout(sendLogout, INACTIVITY_TIMEOUT_MS);
  };

  /**
   * scheduleWarningTimer - Starts the warning timer
   * 
   * This timer shows a warning popup after 4 minutes, then starts a countdown
   */
  const scheduleWarningTimer = () => {
    // Clear any existing warning timer
    if (warningTimerRef.current) clearTimeout(warningTimerRef.current);

    // Start timer that will show warning after 4 minutes
    warningTimerRef.current = setTimeout(() => {
      // Show the warning popup and reset countdown to 60 seconds
      setSecondsLeft(COUNTDOWN_SECONDS);
      setShowWarning(true);
      showWarningRef.current = true;

      // Clear any existing countdown timer
      if (countdownIntervalRef.current) clearInterval(countdownIntervalRef.current);

      // Start countdown that updates every second
      countdownIntervalRef.current = setInterval(() => {
        setSecondsLeft((prev) => {
          if (prev <= 1) {
            // Countdown finished - logout the user
            clearInterval(countdownIntervalRef.current);
            setShowWarning(false);
            showWarningRef.current = false;
            sendLogout();
            return 0;
          }
          return prev - 1; // Decrease countdown by 1 second
        });
      }, 1000); // Update every 1000 milliseconds (1 second)
    }, WARNING_OFFSET_MS);
  };

  /**
   * clearAllTimers - Stops all running timers
   * 
   * This prevents memory leaks by cleaning up timers when they're no longer needed
   */
  const clearAllTimers = () => {
    if (inactivityTimerRef.current) clearTimeout(inactivityTimerRef.current);
    if (warningTimerRef.current) clearTimeout(warningTimerRef.current);
    if (countdownIntervalRef.current) clearInterval(countdownIntervalRef.current);
  };

  /**
   * resetAllTimers - Restarts all timers from the beginning
   * 
   * This is called when:
   * - User becomes active (moves mouse, types, etc.)
   * - User clicks "Stay Logged In" button
   */
  const resetAllTimers = () => {
    clearAllTimers();                    // Stop all existing timers
    setShowWarning(false);               // Hide warning popup
    showWarningRef.current = false;      // Update ref to match state
    setSecondsLeft(COUNTDOWN_SECONDS);   // Reset countdown to 60 seconds
    scheduleWarningTimer();              // Start 4-minute warning timer
    scheduleInactivityTimer();           // Start 5-minute logout timer
  };

  /**
   * handleStayLoggedIn - Called when user clicks "Stay Logged In" button
   * 
   * This resets all timers, giving the user another 5 minutes of activity
   */
  const handleStayLoggedIn = () => resetAllTimers();

  // ====== REACT EFFECTS ======

  // List of browser events that show the user is active
  const activityEvents = ['mousemove', 'keydown', 'mousedown', 'wheel', 'touchstart'];

  /**
   * useEffect - Sets up activity detection when component first loads
   * 
   * This effect:
   * 1. Listens for user activity (mouse movement, typing, etc.)
   * 2. Resets timers when user becomes active
   * 3. Starts timers if user is already logged in
   * 4. Cleans up event listeners when component is removed
   */
  useEffect(() => {
    /**
     * resetOnActivity - Called whenever user does something active
     * 
     * This function resets the timers if:
     * - User is logged in (has session_id)
     * - Warning popup is not currently showing
     */
    const resetOnActivity = () => {
      const isLoggedIn = localStorage.getItem('session_id');
      if (isLoggedIn && !showWarningRef.current) {
        resetAllTimers();
      }
    };

    // Add event listeners for all types of user activity
    activityEvents.forEach((event) => {
      window.addEventListener(event, resetOnActivity, { passive: true });
    });

    // If user is already logged in, start the timers
    if (localStorage.getItem('session_id')) {
      scheduleWarningTimer();
      scheduleInactivityTimer();
    }

    // Cleanup function - runs when component is removed
    return () => {
      clearAllTimers();
      activityEvents.forEach((event) => {
        window.removeEventListener(event, resetOnActivity);
      });
    };
  }, []); // Empty dependency array means this runs only once when component mounts

  /**
   * useEffect - Listens for login/logout events from other components
   * 
   * This effect handles custom events that are sent when:
   * - User logs in (from AuthSwitcher component)
   * - User logs out (from MainScreen component)
   */
  useEffect(() => {
    /**
     * handleUserLoggedOut - Called when user logs out
     * 
     * This stops all timers and hides the warning popup
     */
    const handleUserLoggedOut = () => {
      clearAllTimers();
      setShowWarning(false);
      showWarningRef.current = false;
    };

    /**
     * handleUserLoggedIn - Called when user logs in
     * 
     * This starts the inactivity timers for the new session
     */
    const handleUserLoggedIn = () => {
      scheduleWarningTimer();
      scheduleInactivityTimer();
    };

    // Listen for custom events from other components
    window.addEventListener('userLoggedOut', handleUserLoggedOut);
    window.addEventListener('userLoggedIn', handleUserLoggedIn);

    // Cleanup - remove event listeners when component is removed
    return () => {
      window.removeEventListener('userLoggedOut', handleUserLoggedOut);
      window.removeEventListener('userLoggedIn', handleUserLoggedIn);
    };
  }, []); // Empty dependency array means this runs only once when component mounts

  // ====== RENDER ======
  return (
    <div className="App">
      {/* Main authentication component - handles login/signup */}
      <AuthSwitcher />

      {/* Inactivity warning popup - only shows when showWarning is true */}
      {showWarning && (
        <div className="modal-overlay" role="dialog" aria-modal="true">
          <div className="modal-content" style={{ maxWidth: '480px' }}>
            {/* Popup header with title and close button */}
            <div className="modal-header">
              <h3 className="modal-title">You are inactive</h3>
              <button
                className="modal-close"
                onClick={resetAllTimers}
                aria-label="Close warning"
              >
                ✕
              </button>
            </div>
            
            {/* Popup body with warning message and countdown */}
            <div className="modal-body">
              <p>No activity detected for 4 minutes.</p>
              <p>
                The system will log you out in <strong>{secondsLeft}</strong> seconds.
              </p>
            </div>
            
            {/* Popup footer with action button */}
            <div className="modal-footer">
              <button className="modal-button" onClick={handleStayLoggedIn}>
                Stay Logged In
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;

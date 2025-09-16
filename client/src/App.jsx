import React, { useEffect, useRef, useState } from 'react';
import AuthSwitcher from './components/AuthSwitcher'; 

function App() {
  const INACTIVITY_TIMEOUT_MS = 5 * 60 * 1000;
  const WARNING_OFFSET_MS = 4 * 60 * 1000; 
  const inactivityTimerRef = useRef(null);
  const warningTimerRef = useRef(null);
  const countdownIntervalRef = useRef(null);
  const showWarningRef = useRef(false);
  const [showWarning, setShowWarning] = useState(false);
  const [secondsLeft, setSecondsLeft] = useState(60);

  const sendLogout = async () => {
    try {
      const sessionId = localStorage.getItem('session_id');
      if (!sessionId) return;
      await fetch(`${import.meta.env.VITE_API_URL}/logout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Session-ID': sessionId
        }
      });
    } catch (e) {
      console.error('Inactivity logout failed:', e);
    } finally {
      localStorage.removeItem('session_id');
      // Dispatch custom event to notify AuthSwitcher
      window.dispatchEvent(new CustomEvent('userLoggedOut'));
    }
  };

  const scheduleInactivityTimer = () => {
    if (inactivityTimerRef.current) clearTimeout(inactivityTimerRef.current);
    inactivityTimerRef.current = setTimeout(() => {
      sendLogout();
    }, INACTIVITY_TIMEOUT_MS);
  };

  const scheduleWarningTimer = () => {
    if (warningTimerRef.current) clearTimeout(warningTimerRef.current);
    warningTimerRef.current = setTimeout(() => {
      setSecondsLeft(60);
      setShowWarning(true);
      showWarningRef.current = true;
      if (countdownIntervalRef.current) clearInterval(countdownIntervalRef.current);
      countdownIntervalRef.current = setInterval(() => {
        setSecondsLeft((prev) => {
          if (prev <= 1) {
            clearInterval(countdownIntervalRef.current);
            setShowWarning(false);
            showWarningRef.current = false;
            sendLogout();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }, WARNING_OFFSET_MS);
  };

  const resetAllTimers = () => {
    if (inactivityTimerRef.current) clearTimeout(inactivityTimerRef.current);
    if (warningTimerRef.current) clearTimeout(warningTimerRef.current);
    if (countdownIntervalRef.current) clearInterval(countdownIntervalRef.current);
    setShowWarning(false);
    showWarningRef.current = false;
    setSecondsLeft(60);
    scheduleWarningTimer();
    scheduleInactivityTimer();
  };

  const handleStayLoggedIn = () => {
    resetAllTimers();
  };

  useEffect(() => {
    const resetOnActivity = () => {
      // Only reset timers if warning modal is NOT showing and user is logged in
      if (!showWarningRef.current && localStorage.getItem('session_id')) {
        resetAllTimers();
      }
    };
    const events = ['mousemove', 'keydown', 'mousedown', 'wheel', 'touchstart'];
    events.forEach((evt) => window.addEventListener(evt, resetOnActivity, { passive: true }));
    
    // Only start timers if user is logged in
    if (localStorage.getItem('session_id')) {
      scheduleWarningTimer();
      scheduleInactivityTimer();
    }
    
    return () => {
      if (inactivityTimerRef.current) clearTimeout(inactivityTimerRef.current);
      if (warningTimerRef.current) clearTimeout(warningTimerRef.current);
      if (countdownIntervalRef.current) clearInterval(countdownIntervalRef.current);
      events.forEach((evt) => window.removeEventListener(evt, resetOnActivity));
    };
  }, []); // Empty dependency array - only run once

  // Listen for login/logout events to start/stop timers
  useEffect(() => {
    const handleUserLoggedOut = () => {
      // Stop all timers when user logs out
      if (inactivityTimerRef.current) clearTimeout(inactivityTimerRef.current);
      if (warningTimerRef.current) clearTimeout(warningTimerRef.current);
      if (countdownIntervalRef.current) clearInterval(countdownIntervalRef.current);
      setShowWarning(false);
      showWarningRef.current = false;
    };

    const handleUserLoggedIn = () => {
      // Start timers when user logs in
      scheduleWarningTimer();
      scheduleInactivityTimer();
    };

    window.addEventListener('userLoggedOut', handleUserLoggedOut);
    window.addEventListener('userLoggedIn', handleUserLoggedIn);
    
    return () => {
      window.removeEventListener('userLoggedOut', handleUserLoggedOut);
      window.removeEventListener('userLoggedIn', handleUserLoggedIn);
    };
  }, []);

  return (
    <div className="App">
      <AuthSwitcher />

      {showWarning && (
        <div className="modal-overlay" role="dialog" aria-modal="true">
          <div className="modal-content" style={{ maxWidth: '480px' }}>
            <div className="modal-header">
              <h3 className="modal-title">You are inactive</h3>
              <button className="modal-close" onClick={resetAllTimers}>✕</button>
            </div>
            <div className="modal-body">
              <p>No activity detected for 4 minutes.</p>
              <p>The system will log you out in <strong>{secondsLeft}</strong> seconds.</p>
            </div>
            <div className="modal-footer">
              <button className="modal-button" onClick={handleStayLoggedIn}>Stay Logged In</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;

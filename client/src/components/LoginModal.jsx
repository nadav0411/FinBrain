import React, { useState } from 'react';
import logo from '../assets/logo.png';
import './LoginModal.css';


function LoginModal({ onGoToSignup, onLoginSuccess }) {
  // Store form inputs
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  // UI feedback
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  // Called when the user submits the form
  const handleSubmit = async (e) => {
    e.preventDefault(); // prevent page reload

    // Validate inputs
    if (!email || !password) {
      setError('Both email and password are required.');
      return;
    }

    setLoading(true);
    setError('');
    // Send request to server
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      // Wait for response from server
      const data = await response.json();

      // If login is successful
      if (response.status === 200) {
        // Save the session ID to local storage
        if (data.session_id) {
          localStorage.setItem('session_id', data.session_id);
        }
        // Show success message
        setSuccess(true);
        setTimeout(() => {
          setSuccess(false);
          setEmail('');
          setPassword('');
          onLoginSuccess();
        }, 2500);
      
      // If login fails
      } else {
        setError(data.message || 'Login failed.');
      }

    // If there is an error
    } catch (err) {
      setError('Server error. Please try again later.');
    }

    setLoading(false);
  };

  
  return (
    <div className="modal-overlay">
      <div className="modal login-modal">
      <div className="modal-header">
        {/* Header text */}
        <h2 className="header-text">Welcome Back</h2>
        <img src={logo} alt="Logo" className="modal-logo" />
      </div>

        <form className="modal-body" onSubmit={handleSubmit}>
          <div className="row">
            <div className="field">
              {/* Email input */}
              <label>Email</label>
              <input
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
          </div>

          <div className="row">
            <div className="field">
              {/* Password input */}
              <label>Password</label>
              <input
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <div className="row link-row">
            {/* Sign up link */}
            <a href="#" onClick={onGoToSignup} className="side-link">Sign Up</a>
            <a href="#" className="side-link">Forgot Password?</a>
          </div>

          {/* Error message */}
          {error && <div className="error-msg">{error}</div>}

          {/* Success message */}
          {success && (
            <div className="success-popup">
              <div className="checkmark">✓</div>
              <div className="success-text">Login successful!</div>
            </div>
          )}

          <div className="row button-group">
            {/* Login button */}
            <button type="submit" className="main-button login-button">
              Login
            </button>
            {/* Demo button */}
            <button type="button" className="main-button demo-button">
              Demo Mode
            </button>
          </div>

          {/* Loading message */}
          {loading && (
            <div className="loading-msg">
              <span className="spinner" /> Logging you in...
            </div>
          )}
        </form>
      </div>
    </div>
  );
}

// Export this component so other files can use it
export default LoginModal;

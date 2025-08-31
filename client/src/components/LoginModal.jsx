import React from 'react';

// Import the CSS file that styles this login modal
import './LoginModal.css';


function LoginModal() {
  return (
    // The dark background that covers the whole screen
    <div className="modal-overlay">

      {/* The white modal box in the center (with login content) */}
      <div className="modal login-modal">

        {/* Header section with welcome text */}
        <div className="modal-header">
          <h2>Welcome Back</h2>
        </div>

        {/* Main body of the modal (input fields and buttons) */}
        <div className="modal-body">

          {/* First row: Email input */}
          <div className="row">
            <div className="field">
              <label>Email</label>
              {/* Input for user's email address */}
              <input type="email" placeholder="you@example.com" />
            </div>
          </div>

          {/* Second row: Password input */}
          <div className="row">
            <div className="field">
              <label>Password</label>
              {/* Input for user's password (hidden text) */}
              <input type="password" placeholder="••••••••" />
            </div>
          </div>

          {/* Third row: Side links for Sign Up and Forgot Password */}
          <div className="row link-row">
            {/* Link to go to Sign Up page */}
            <a href="#" className="side-link">Sign Up</a>

            {/* Link to reset password */}
            <a href="#" className="side-link">Forgot Password?</a>
          </div>

          {/* Fourth row: Login and Demo buttons */}
          <div className="row button-group">
            {/* Main login button */}
            <button className="main-button login-button">Login</button>

            {/* Special demo button */}
            <button className="main-button demo-button">Demo Mode</button>
          </div>

        </div> {/* end of modal-body */}

      </div> {/* end of modal */}

    </div> // end of modal-overlay
  );
}

// Export this component so I can use it in other parts of the app
export default LoginModal;
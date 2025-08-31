import React from 'react';
import './LoginModal.css';

function LoginModal() {
  return (
    <div className="modal-overlay">
      <div className="modal login-modal">
        <div className="modal-header">
          <h2>Welcome Back</h2>
        </div>

        <div className="modal-body">
          <div className="row">
            <div className="field">
              <label>Email</label>
              <input type="email" placeholder="you@example.com" />
            </div>
          </div>

          <div className="row">
            <div className="field">
              <label>Password</label>
              <input type="password" placeholder="••••••••" />
            </div>
          </div>

          <div className="row link-row">
            <a href="#" className="side-link">Sign Up</a>
            <a href="#" className="side-link">Forgot Password?</a>
          </div>

          <div className="row button-group">
            <button className="main-button login-button">Login</button>
            <button className="main-button demo-button">🚀 Demo Mode</button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LoginModal;

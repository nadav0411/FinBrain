import React, { useState } from 'react';
import './SignupModal.css';

function SignupModal({ onBackToLogin }) {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: ''
  });

  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const { firstName, lastName, email, password, confirmPassword } = formData;

    // בדיקת שדות ריקים
    if (!firstName || !lastName || !email || !password || !confirmPassword) {
      setError('All fields are required.');
      return;
    }

    // בדיקת סיסמאות תואמות
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setError('');
    alert('Signup successful! ✅');
    // כאן אפשר לשלוח ל־backend
  };

  return (
    <div className="modal-overlay">
      <div className="modal signup-modal">
        <div className="modal-header">
          <h2>Create Account</h2>
        </div>

        <form className="modal-body" onSubmit={handleSubmit}>
          <div className="row">
            <div className="field">
              <label>First Name</label>
              <input
                type="text"
                name="firstName"
                placeholder="John"
                value={formData.firstName}
                onChange={handleChange}
              />
            </div>
            <div className="field">
              <label>Last Name</label>
              <input
                type="text"
                name="lastName"
                placeholder="Doe"
                value={formData.lastName}
                onChange={handleChange}
              />
            </div>
          </div>

          <div className="row">
            <div className="field">
              <label>Email</label>
              <input
                type="email"
                name="email"
                placeholder="you@example.com"
                value={formData.email}
                onChange={handleChange}
              />
            </div>
          </div>

          <div className="row">
            <div className="field">
              <label>Password</label>
              <input
                type="password"
                name="password"
                placeholder="••••••••"
                value={formData.password}
                onChange={handleChange}
              />
            </div>
            <div className="field">
              <label>Confirm Password</label>
              <input
                type="password"
                name="confirmPassword"
                placeholder="••••••••"
                value={formData.confirmPassword}
                onChange={handleChange}
              />
            </div>
          </div>

          {error && <div className="error-msg">{error}</div>}

          <div className="row button-group">
            <button type="submit" className="main-button signup-submit">Sign Up</button>
          </div>

          <div className="row back-row">
            <a href="#" onClick={onBackToLogin} className="back-link">← Back to Login</a>
          </div>
        </form>
      </div>
    </div>
  );
}

export default SignupModal;

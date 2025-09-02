import React, { useState } from 'react';
import logo from '../assets/logo.png';
import './SignupModal.css';


function SignupModal({ onBackToLogin }) {
  // Store form inputs
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: ''
  });

  // UI feedback
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  // Error message
  const [error, setError] = useState('');

  
  // Handle input changes
  const handleChange = (e) => {
    setFormData((prev) => ({
      ...prev, // keep the old fields as they are
      [e.target.name]: e.target.value // update only the changed field
    }));
  };

  // Handle name input
  const handleNameInput = (e) => {
    const regex = /^[A-Za-z\s]*$/; 
    if (regex.test(e.target.value)) {
      handleChange(e);
    }
  };

  // This function runs when the user clicks "Sign Up"
  const handleSubmit = async (e) => {
    e.preventDefault(); // stop page from reloading
    const { firstName, lastName, email, password, confirmPassword } = formData;

    // Check if any field is empty
    if (!firstName || !lastName || !email || !password || !confirmPassword) {
      setError('All fields are required.');
      return;
    }

    // Check if the passwords match
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);
    // Send request to server
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      // get the response from the server
      const data = await response.json();

      // if signup is successful
      if (response.status === 201) {
        setSuccess(true);
        setTimeout(() => {
          setSuccess(false);
          setFormData({
            firstName: '',
            lastName: '',
            email: '',
            password: '',
            confirmPassword: '',
          });
          setError('');
          onBackToLogin(); 
        }, 2500);
        
      // if signup fails
      } else {
        setError(data.message || 'Something went wrong');
      }

    // if there is an error
    } catch (error) {
      console.error('Signup error:', error);
      setError('Something went wrong. Please try again.');
    }
    setLoading(false);
  };


  return (
    <div className="modal-overlay">
      <div className="modal signup-modal">
        <div className="modal-header">
          {/* Header */}
          <h2>Create Account</h2>
          <img src={logo} alt="Logo" className="modal-logo" />
        </div>

        <form className="modal-body" onSubmit={handleSubmit}>

          {/* First row: first name and last name */}
          <div className="row">
            <div className="field">
              <label>First Name</label>
              <input
                type="text"
                name="firstName"
                placeholder="John"
                value={formData.firstName}
                onChange={handleNameInput}
              />
            </div>
            <div className="field">
              <label>Last Name</label>
              <input
                type="text"
                name="lastName"
                placeholder="Doe"
                value={formData.lastName}
                onChange={handleNameInput}
              />
            </div>
          </div>

          {/* Second row: email input */}
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

          {/* Third row: password and confirm password */}
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

          {/* If there is an error message, show it here */}
          {error && <div className="error-msg">{error}</div>}
          
          {/* If the signup is successful, show a success message */}
          {success && (
          <div className="success-popup">
            <div className="checkmark">✓</div>
            <div className="success-text">Signup successful!</div>
          </div> )}

          {/* Submit button row */}
          <div className="row button-group">
            <button type="submit" className="main-button signup-submit">
              Sign Up
            </button>
          </div>

          {/* Loading message while waiting for server */}
          {loading && (
            <div className="loading-msg">
              <span className="spinner" /> Creating your account...
            </div>          
          )}
          
          {/* Link to go back to the login screen */}
          <div className="row back-row">
            <a href="#" onClick={onBackToLogin} className="back-link">
              ← Back to Login
            </a>
          </div>

        </form>
      </div>
    </div>
  );
}

// Export this component so other files can use it
export default SignupModal;

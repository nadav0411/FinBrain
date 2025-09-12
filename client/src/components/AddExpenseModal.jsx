/* AddExpenseModal.jsx */

import React, { useState } from 'react';
import './AddExpenseModal.css';

// Modal component for adding new expense entries
function AddExpenseModal({ onClose }) {
  // State management for form inputs and UI feedback
  const [title, setTitle] = useState('');
  const [date, setDate] = useState('');
  const [amount, setAmount] = useState('');
  const [currency, setCurrency] = useState('USD');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Date constraints for validation
  const today = new Date().toISOString().split("T")[0];        
  const minDate = "2015-01-01";                                 

  // Handles form submission and API communication
  const handleSubmit = async () => {
    // Client-side validation before sending to server
    if (!title || !date || !amount || !currency) {
      setError("Please fill in all fields.");
      return;
    }

    const expenseData = { title, date, amount, currency };
    setLoading(true);

    try {
      // Send expense data to backend with session authentication
      const response = await fetch(`${import.meta.env.VITE_API_URL}/add_expense`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Session-ID': localStorage.getItem('session_id')
        },
        body: JSON.stringify(expenseData),
      });

      if (response.ok) {
        onClose(); // Close modal on successful submission
      } else {
        const err = await response.text();
        setError("Server error. Try again.");
      }
    } catch (err) {
      setError("Connection error.");
    } finally {
      setLoading(false);
    }
  };

  // Input validation for title field - only allows alphanumeric characters and spaces
  const handleTitleChange = (e) => {
    const regex = /^[A-Za-z0-9\s]*$/;
    const value = e.target.value;
    
    // Limit to 60 characters and validate format
    if (value.length <= 60 && regex.test(value)) {
      setTitle(value);
      setError('');
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Add Expense Item</h2>
          <button className="close-button" onClick={onClose}>&times;</button>
        </div>

        <div className="modal-body">
          {/* Error display for user feedback */}
          {error && <div className="error-message">{error}</div>}

          {/* Title input with character validation */}
          <div className="row">
            <div className="field">
              <label>Title</label>
              <input
                type="text"
                placeholder="Pizza with friends"
                value={title}
                onChange={handleTitleChange}
                maxLength={60}
              />
              <div className="char-counter">
                {title.length}/60 characters
              </div>
            </div>
          </div>

          {/* Date input with range restrictions */}
          <div className="row">
            <div className="field">
              <label>Date</label>
              <input
                type="date"
                className="date-input"
                value={date}
                min={minDate}
                max={today}
                onKeyDown={(e) => e.preventDefault()}
                onChange={(e) => {
                  setDate(e.target.value);
                  setError('');
                }}
              />
            </div>
          </div>

          {/* Amount and currency inputs */}
          <div className="row">
            <div className="field">
              <label>Amount</label>
              <input
                type="number"
                placeholder="60.00"
                min={0}
                value={amount}
                onChange={(e) => {
                  const value = e.target.value;
                  // Clean input to only allow numbers and decimal point
                  const cleanValue = value.replace(/[^0-9.]/g, '');
                  
                  // Limit to 10 digits total for reasonable expense amounts
                  const digitsOnly = cleanValue.replace(/\./g, '');
                  if (digitsOnly.length <= 10) {
                    setAmount(cleanValue);
                    setError('');
                  }
                }}
                onKeyDown={(e) => {
                  // Prevent non-numeric input except navigation keys
                  if (
                    !/[0-9.]/.test(e.key) &&
                    !["Backspace", "Tab", "ArrowLeft", "ArrowRight", "Delete"].includes(e.key)
                  ) {
                    e.preventDefault();
                  }
                }}
              />
              <div className="char-counter">
                {amount.replace(/\./g, '').length}/10 digits
              </div>
            </div>

            <div className="field">
              <label>Currency</label>
              <select
                value={currency}
                onChange={(e) => {
                  setCurrency(e.target.value);
                  setError('');
                }}
              >
                <option value="USD">USD</option>
                <option value="ILS">ILS</option>
              </select>
            </div>
          </div>

          {/* Submit button with loading state */}
          <div className="button-container">
            <button className="add-button" onClick={handleSubmit} disabled={loading}>
              {loading ? (
                <div className="loading-dots">
                  <span>.</span>
                  <span>.</span>
                  <span>.</span>
                </div>
              ) : (
                "Add"
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AddExpenseModal;

/* FinBrain Project - AddExpenseModal.jsx - MIT License (c) 2025 Nadav Eshed */


import React, { useState } from 'react';
import './AddExpenseModal.css';

/**
 * AddExpenseModal Component
 * 
 * This component shows a popup (modal) where the user can add an expense.
 * It checks input, shows errors, and sends data to the server.
 */
function AddExpenseModal({ onClose, onExpenseAdded }) {
  // React state variables (data that can change and re-render UI)
  const [title, setTitle] = useState('');          // Expense name
  const [date, setDate] = useState('');            // Expense date
  const [amount, setAmount] = useState('');        // Expense amount
  const [currency, setCurrency] = useState('USD'); // Currency (USD/ILS)
  const [error, setError] = useState('');          // Error message for user
  const [loading, setLoading] = useState(false);   // True when saving data

  // Limit dates in the date input
  const today = new Date().toISOString().split("T")[0]; // today = max
  const minDate = "2015-01-01"; // do not allow very old dates

  /**
   * handleSubmit - runs when clicking "Add"
   * - Validates input
   * - Sends data to server
   * - Shows loading animation
   */
  const handleSubmit = async () => {
    // Demo mode → do not save, just close
    if (localStorage.getItem('is_demo_user') === 'true') {
      onClose();
      return;
    }

    // Make sure all fields are filled
    if (!title || !date || !amount || !currency) {
      setError("Please fill in all fields.");
      return;
    }

    // Data object to send
    const expenseData = { title, date, amount, currency };
    setLoading(true);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/add_expense`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Session-ID': localStorage.getItem('session_id'),
        },
        body: JSON.stringify(expenseData),
      });

      if (response.ok) {
        onExpenseAdded(date); // notify parent
        onClose();            // close modal
      } else {
        setError("Server error. Try again.");
      }
    } catch (err) {
      setError("Connection error.");
    } finally {
      setLoading(false);
    }
  };

  /**
   * handleTitleChange - runs every time user types in title field
   * Only allows letters, numbers and spaces
   */
  const handleTitleChange = (e) => {
    const value = e.target.value;
    const regex = /^[A-Za-z0-9\s]*$/; 
    
    if (value.length <= 60 && regex.test(value)) {
      setTitle(value);
      setError('');
    }
  };

  /**
   * handleAmountChange - only numbers and decimal point allowed
   * Limit: 10 digits (ignores decimal point)
   */
  const handleAmountChange = (e) => {
    const value = e.target.value;
    const cleanValue = value.replace(/[^0-9.]/g, '');
    const digitsOnly = cleanValue.replace(/\./g, '');
    if (digitsOnly.length <= 10) {
      setAmount(cleanValue);
      setError('');
    }
  };

  /**
   * handleAmountKeyDown - block invalid keys
   * Allows: numbers, ".", and navigation keys
   */
  const handleAmountKeyDown = (e) => {
    const allowedKeys = ["Backspace", "Tab", "ArrowLeft", "ArrowRight", "Delete"];
    if (!/[0-9.]/.test(e.key) && !allowedKeys.includes(e.key)) {
      e.preventDefault();
    }
  };

  return (
    // Overlay = dark background
    <div className="modal-overlay" onClick={onClose}>
      {/* Main white box. stopPropagation() = clicking inside does NOT close modal */}
      <div className="modal" onClick={(e) => e.stopPropagation()}>

        {/* Header = title + X button */}
        <div className="modal-header">
          <h2>Add Expense Item</h2>
          <button className="close-button" onClick={onClose}>&times;</button>
        </div>

        {/* Body = form fields */}
        <div className="modal-body">
          
          {/* Show error if needed */}
          {error && <div className="error-message">{error}</div>}

          {/* Title input */}
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

          {/* Date input */}
          <div className="row">
            <div className="field">
              <label>Date</label>
              <input
                type="date"
                value={date}
                min={minDate}
                max={today}
                onKeyDown={(e) => e.preventDefault()} // block typing
                onChange={(e) => {
                  setDate(e.target.value);
                  setError('');
                }}
              />
            </div>
          </div>

          {/* Amount + Currency in same row */}
          <div className="row">
            
            {/* Amount */}
            <div className="field">
              <label>Amount</label>
              <input
                type="number"
                placeholder="60.00"
                min={0}
                value={amount}
                onChange={handleAmountChange}
                onKeyDown={handleAmountKeyDown}
              />
              <div className="char-counter">
                {amount.replace(/\./g, '').length}/10 digits
              </div>
            </div>

            {/* Currency dropdown */}
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

          {/* Submit button */}
          <div className="button-container">
            <button 
              className="add-button" 
              onClick={handleSubmit} 
              disabled={loading}
            >
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